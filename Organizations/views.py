import re

from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from APIBackendService.views import AppUsersAPIView
from APIBackendService.views import AppCompanyAPIView
from Notifications.constants import ADMIN_INFO
from Organizations.models import *
from Organizations.utils.relations import get_potential_relationships_for_company
from Users.utils import get_random_password
from Users.utils.relations import get_list_of_subordinate_users, get_list_of_subordinate_users_with_creators, \
    get_user_company_permissions, get_russian_company_role, get_user_factory_permissions, get_list_of_users_in_factory
from .serializers import CompanyMainInformationSerializer, FactoryMainInformationSerializer, FactoryPreviewSerializer, \
    AddressSerializer, CreateRelationFileSerializer
import Users.constants.user_company_permissions as COMPANY_PERMISSIONS
import Users.constants.factory_permissions as FACTORY_PERMISSIONS

from Users.models import User, UserCompanyRelation, UserFactoryRelation
import Users.constants.user_organization_role as USER_FACTORY_ROLE
import Organizations.constants.organizations_relationship_type as ORGANIZATIONS_RELATIONSHIP_TYPE
from .utils import get_random_code

from APIBackendService.views import AppCompanyAPIView
from Users.constants.user_organization_role import OWNER, MANAGER, STAFF
from Notifications.views.system_notifications import *
from django.utils.crypto import get_random_string
from Notifications.service import send

from Notifications.views.telegram_admin import ReceiveTelegramAdminNotificationsView
import Communications.constants.message_status as MESSAGE_STATUS

import datetime
from Organizations.serializers import CompanyMainInformationSerializer, OkvedSerializer
from Users.serializers import UserCompanyRelationForInvitationLinkSerializer

from django.db.models import Q

from Organizations.utils.files_processing import add_file_to_relation

from Users.utils import get_full_name
from Documents.utils import add_file
from Documents.serializers import CreateFileSerializer, UpdateFileSerializer
from Documents.models import Document

NOT_HAVE_PERMISSIONS = {
    "data": {"detail": "Нет прав"},
    "status": status.HTTP_400_BAD_REQUEST,
}

#class CompanyCreateView(AppUsersAPIView):
class CompanyCreateView(AppUsersAPIView):
    

    def post(self, request):
        user = request.user
        # user = User.objects.get(id=1)
        #request.data._mutable = True
        data = request.data
        
        # Если пользователь ставит галочку, что он один из учредителей, то он добавляется в список лидеров компании
        data["leaders"] = []
        if data.get('is_leader', None):
           #data["leader"] = " ".join([user.last_name, user.first_name, user.middle_name])
           data["leaders"].append({"name": get_full_name(user),
                                   "id": user.id})
            
        serializer = CompanyMainInformationSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        company = serializer.save()
        UserCompanyRelation.objects.create(
            user=user,
            company=company,
            role=USER_FACTORY_ROLE.OWNER,
            product_interaction_permission=True,
            ordering_permission=True,
            company_info_permission=True,
            factory_permission=True,
            add_users_permission=True,
            proposal_permission=True,
        )

        #  ## Temporary remove this  ############
        # token = request.data.get('token', None)
        # if token is not None:
        #     invitation = TokenInviteOtherCompany.objects.filter(token=token).first()
        #     if invitation and not invitation.used:
        #         company_that_invited = invitation.company_that_invited
        #         company_that_invited.balance += 100500
        #         company_that_invited.save()
        #         invitation.used = True
        #         invitation.company_to_invite = company
        #         invitation.save()

        company_producer = CompanyProducer.objects.filter(inn=company.inn)

        if company_producer.exists():
            company_producer.first().update(company=company, name=company.name, inn=company.inn)
        else:
            CompanyProducer.objects.create(company=company, name=company.name, inn=company.inn)

        Organization.objects.create(
            company=company,
            creator=user,
        )

        return Response({'id': company.id})


class CompanyUpdateView(AppCompanyAPIView):
        # LAST CHANGED

    def post(self, request):
        relation: UserCompanyRelation = request.user
        user = relation.user
        company = relation.company
        if not relation.company_info_permission:
            return Response(data={"detail": "Нет прав на компанию"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CompanyMainInformationSerializer(company, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        company = serializer.save()

        return Response({'id': company.id})


class CompanyAddressCreateView(AppCompanyAPIView):
    """
    Создание более подробного адресса компании
    """
    def post(self, request):
        company_id = request.user.company.id
        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class CompanyAddressUpdateView(AppCompanyAPIView):
    """
    Изменение более подробного адресса компании
    """
    def post(self, request):
        company_id = request.user.company.id
        company_address = get_object_or_404(Address, company=company_id)
        serializer = AddressSerializer(company_address, data=request.data, partial=True)
        serializer.is_valid(True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


# class CompanyGetView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         user = request.user
#         company = get_object_or_404(Company, id=int(request.GET.get("id", 0)))
#         can_edit = False
#         relations = UserCompanyRelation.objects.filter(company=company, user=user)
#         if relations.exists() and relations.first().company_info_permission:
#             can_edit = True
#
#         company_data = CompanyMainInformationSerializer(company).data
#
#         return Response({
#             'edit': can_edit,
#             'info': company_data
#         })


class CompanyGetView(AppCompanyAPIView):
    

    def get(self, request):
        relation: UserCompanyRelation = request.user
        return Response({
            'edit': relation.company_info_permission,
            'info': CompanyMainInformationSerializer(relation.company).data
        })


class CompaniesListView(AppUsersAPIView):
    

    def get(self, request):
        user = request.user
        relations = UserCompanyRelation.objects.filter(user=user)
        companies = []
        for relation in relations:
            if relation.company:
                companies.append({
                    "name": CompanyMainInformationSerializer(relation.company).data["name"],
                    "role": get_russian_company_role(relation.role),
                    "id": relation.company.id,
                })

        return Response({'company_list': companies})


class FactoriesListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        relations = UserFactoryRelation.objects.filter(user=user)
        factories = []
        for relation in relations:
            factories.append(FactoryPreviewSerializer(relation.factory).data)

        return Response({'list': factories})


class CompanyAddUsersView(AppCompanyAPIView):
      # LAST CHANGED

    def post(self, request):
        relation: UserCompanyRelation = request.user
        user = relation.user
        email = user.email
        company = relation.company
        
        has_access = relation.add_users_permission
        if not has_access:
            return Response(
                data={"detail": "Нет прав на добавление пользователей"},
                status=status.HTTP_400_BAD_REQUEST
            )

        amount = int(request.data["amount"])

        permissions = request.data["permissions"]
        real_permissions = {p: False for p in COMPANY_PERMISSIONS.LIST}
        main_user_permissions = get_user_company_permissions(relation)
        
        #is_leader = request.data.get("is_leader", None)

        for permission in permissions:
            if permission in main_user_permissions:
                real_permissions[permission] = True

        users = []
        text = f"Здравствуйте!\nВ системе зарегистрированы новые пользователи (логин, пароль):\n"
        for _ in range(amount):
            counter = 0
            create_id = 0
            while True:
                counter += 1
                if counter > 20:
                    break
                try:
                    new_user = User.objects.create(username=f"user_{get_random_code(amount=6)}")
                    create_id = new_user.id
                    password = get_random_password()
                    new_user.set_password(password)
                    new_user.change_password_date = None  # timezone.now().date()
                    new_user.username = f"user{new_user.id}_{get_random_code(3)}"
                    new_user.organization_account = True
                    new_user.save()
                    users.append({
                        "id": new_user.id,
                        "username": new_user.username,
                        "password": password,
                    })
                    
                    #if is_leader:
                        #company.leaders.append({"name": None,
                                               #"id": new_user.id})

                    UserCompanyRelation.objects.create(
                        user=new_user,
                        creator=user,
                        company=company,
                        role=USER_FACTORY_ROLE.STAFF,
                        is_leader=False,
                        **real_permissions,
                    )
                    text += "\n" + new_user.username + " " + password
                    break
                except Exception as e:
                    User.objects.filter(id=create_id).delete()
                    print("Create user error:", e)
                    continue
        send(email,
             subject="Новые корпоративные пользователи",
             text=text)

        return Response(users)


class FactoryAddUsersView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        adding_user = get_object_or_404(User, id=request.data["user"])
        # company = get_object_or_404(Company, id=request.data["company_id"])
        factory = get_object_or_404(Factory, id=request.data["id"])
        company = factory.company
        relations = UserFactoryRelation.objects.filter(factory=factory, user=user)
        add_relation = UserCompanyRelation.objects.filter(company=company, user=adding_user)
        if not relations.exists() or not relations.first().add_users_permission or not add_relation.exists():
            return Response(
                data={"detail": "Нет прав на добавление пользователей к заводам"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # amount = int(request.data["amount"])

        permissions = request.data["permissions"]
        real_permissions = {p: False for p in FACTORY_PERMISSIONS.LIST}
        user_factory_relation = UserFactoryRelation.objects.filter(factory=factory, user=user).first()
        main_user_permissions = get_user_factory_permissions(user_factory_relation)

        for permission in permissions:
            if permission in main_user_permissions:
                real_permissions[permission] = True

        UserFactoryRelation.objects.create(
            user=adding_user,
            factory=factory,
            role=USER_FACTORY_ROLE.STAFF,
            **real_permissions,
        )

        return Response({"id": adding_user.id,
                         "username": adding_user.username, })


class CompanyShowSubordinateUsersView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        company = get_object_or_404(Company, id=int(request.GET.get("id", 0)))
        relations = UserCompanyRelation.objects.filter(company=company, user=user)
        if not relations.exists() or not relations.first().add_users_permission:
            return Response(
                data={"detail": "Нет прав на просмотр"},
                status=status.HTTP_400_BAD_REQUEST
            )

        users = get_list_of_subordinate_users_with_creators(user, company)

        return Response({
            'users': [{
                "user": {
                    "first_name": pair["u"].first_name,
                    "last_name": pair["u"].last_name,
                    "username": pair["u"].username,
                    "date_joined": pair["u"].date_joined.date(),
                    "id": pair["u"].id,
                },
                "creator": {
                    "name": pair["c"].get_full_name_or_username(),
                    "id": pair["c"].id,
                },
            } for pair in users]
        })


class FactoryShowSubordinateUsersView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        factory = get_object_or_404(Factory, id=int(request.GET.get("id", 0)))
        relations = UserFactoryRelation.objects.filter(factory=factory, user=user)
        if not relations.exists() or not relations.first().add_users_permission:
            return Response(
                data={"detail": "Нет прав на просмотр"},
                status=status.HTTP_400_BAD_REQUEST
            )

        users = get_list_of_users_in_factory(factory)

        return Response({
            'users': [{
                "user": {
                    "first_name": pair.first_name,
                    "last_name": pair.last_name,
                    "username": pair.username,
                    "date_joined": pair.date_joined.date(),
                    "id": pair.id,
                }
            } for pair in users]
        })


class CompanyPermissionsForUserView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        company = get_object_or_404(Company, id=int(request.GET.get("id", 0)))
        relations = UserCompanyRelation.objects.filter(company=company, user=user)
        if not relations.exists():
            permissions = []
            company_role = ""
            is_member = False
        else:
            user_company_relation = relations.first()
            permissions = get_user_company_permissions(user_company_relation)
            company_role = get_russian_company_role(user_company_relation.role)
            is_member = True

        return Response({
            'permissions': permissions,
            'role': company_role,
            "is_member": is_member,
        })


class UpdateCompanyUserPermissionsView(AppCompanyAPIView):
        # LAST CHANGED

    def post(self, request):
        # TODO: ADD UPDATING ROLE HERE
        relation: UserCompanyRelation = request.user
        user = relation.user
        company = relation.company
        
        if  not relation.add_users_permission:
            return Response(
                data={"detail": "Нет прав на изменение"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_to_edit = get_object_or_404(User, id=request.data["user_id"])

        permissions = request.data["permissions"]
        real_permissions = {p: False for p in COMPANY_PERMISSIONS.LIST}
        user_company_relation = relation
        main_user_permissions = get_user_company_permissions(user_company_relation)

        for permission in permissions:
            if permission in main_user_permissions:
                real_permissions[permission] = True

        subordinate_users = get_list_of_subordinate_users(user, company)
        if user_to_edit not in subordinate_users:
            return Response(
                data={"detail": "Нет прав на изменение"},
                status=status.HTTP_400_BAD_REQUEST
            )
        UserCompanyRelation.objects.filter(
            user=user_to_edit,
            company=company,
        ).update(**real_permissions)
                        
        is_leader = bool(request.data.get("is_leader", None)) # передавать 0 или 1
        if is_leader is not None:
            relation_to_update = get_object_or_404(
                                                   UserCompanyRelation,
                                                   user=user_to_edit,
                                                   company=company,
                                                   )       
            user_to_edit.is_leader = is_leader
            user_to_edit.save()
            
            # Словарик для добавления/удаления из учредителей
            new_leader = {"name": get_full_name(user_to_edit),
                          "id": user_to_edit.id}
            
            # Проверяем, есть ли юзер в списке учредителей компании
            new_leader_in_list = False
            for human in company.leaders:
                if human.get('id', None) == user_to_edit.id:
                    new_leader_in_list = True
                    break
            
            if company.leaders == {}:
                company.leaders = []
            
            if is_leader:
                if not new_leader_in_list:
                    company.leaders.append(new_leader)
            else:
                if new_leader_in_list:
                    company.leaders.remove(new_leader)
                    
            company.save()                         
            

        real_permissions_list = [key for key in real_permissions.keys() if real_permissions[key]]

        return Response({
            'permissions': real_permissions_list,
        })


class DeleteUserFromCompanyView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        company = get_object_or_404(Company, id=request.data["company_id"])
        relations = UserCompanyRelation.objects.filter(company=company, user=user)
        if not relations.exists() or not relations.first().add_users_permission:
            return Response(
                data={"detail": "Нет прав на изменение"},
                status=status.HTTP_400_BAD_REQUEST
            )

        users_id = request.data["users"]
        if type(users_id) == int:
            users_id = [users_id]
        subordinate_users = get_list_of_subordinate_users(user, company)
        subordinate_users_id = list(map(lambda x: x.id, subordinate_users))
        to_delete = []
        not_to_delete = []
        for user_id in users_id:
            if user_id in subordinate_users_id:
                to_delete.append(user_id)
            else:
                not_to_delete.append(user_id)

        for user_id in to_delete:
            try:
                user_to_delete = next(filter(lambda x: x.id == user_id, subordinate_users))
                UserCompanyRelation.objects.get(
                    user=user_to_delete,
                    company=company,
                ).delete()
                if user_to_delete.organization_account:
                    user_to_delete.delete()
            except:
                continue

        return Response({
            'not_deleted': not_to_delete,
        })


class FactoryCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        company = get_object_or_404(Company, id=int(request.data['company']))
        if company.single_factory and FactoryCompanyRelation.objects.filter(company=company).exists():
            return Response(
                data={
                    'detail': "У компании с одним заводом не может быть 2 и более заводов. "
                              "Требуется изменить информацию о компании"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = FactoryMainInformationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        factory = serializer.save()
        factory.company = company
        factory.save()

        FactoryCompanyRelation.objects.create(
            company=company,
            factory=factory,
            factory_confirmed=True,
            company_confirmed=True,
        )

        UserFactoryRelation.objects.create(
            product_interaction_permission=True,
            create_orders_permission=True,
            factory_info_permission=True,
            add_users_permission=True,
            proposal_permission=True,
            user=user,
            factory=factory,
            role=USER_FACTORY_ROLE.OWNER,
        )

        company_producer = CompanyProducer.objects.filter(inn=company.inn, company=company).first()
        FactoryProducer.objects.create(company_producer=company_producer, factory=factory, name=factory.name)

        Organization.objects.create(
            factory=factory,
            creator=user,
        )

        return Response({'id': factory.id})


class FactoryGetView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        factory = get_object_or_404(Factory, id=int(request.GET.get("id", 0)))
        can_edit = False
        relations = UserFactoryRelation.objects.filter(factory=factory, user=request.user)
        if relations.exists() and relations.first().factory_info_permission:
            can_edit = True

        factory_data = FactoryMainInformationSerializer(factory).data

        return Response({'edit': can_edit, 'info': factory_data})


class FactoryUpdateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        factory = get_object_or_404(Factory, id=request.data["id"])
        relations = UserFactoryRelation.objects.filter(factory=factory, user=user)
        if not relations.exists() or not relations.first().factory_info_permission:
            return Response(data={"detail": "Нет прав на завод"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = FactoryMainInformationSerializer(factory, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        factory = serializer.save()

        return Response({'id': factory.id})


class FactoriesForCompanyListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # print("START!")
        user = request.user
        company = get_object_or_404(Company, id=int(request.GET.get("id", 0)))
        # print("GET COMPANY:", company)
        relations = UserCompanyRelation.objects.filter(company=company, user=user)
        if not relations.exists():
            return Response(
                data={"detail": "Нет прав на просмотр"},
                status=status.HTTP_400_BAD_REQUEST
            )

        relations = FactoryCompanyRelation.objects.filter(company=company)
        factories = []
        for relation in relations:
            if relation.factory:
                factories.append({
                    "name": relation.factory.name,
                    "id": relation.factory.id,
                })

        return Response({'list': factories})


class SearchCompanyByNameView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        substring = request.GET.get("q", "")
        matching = re.match('^\d+$', substring)

        def get_id(obj):
            return {
                "id": obj.id,
                "name": obj.name,
                "inn": obj.inn,
            }

        if matching is None:
            companies = Company.objects.filter(name__contains=substring)[:4]

            companies_id = map(get_id, companies)
            return Response({"list": companies_id})
        else:
            company = Company.objects.filter(inn=substring)
            if company.exists():
                return Response({"list": [get_id(company.first())]})
            else:
                return Response({'list': []})



class AddCompanyApprovementFileView(AppCompanyAPIView):
    

    def post(self, request):

        relation: UserCompanyRelation = request.user
        company = relation.company
        user = relation.user

        if not relation.company_info_permission :
            return Response(**NOT_HAVE_PERMISSIONS)
        
        if CompanyFile.objects.filter(company=company).count() >= 5:
            return Response(
                data={"detail": "Максимальное число файлов для компании: 5"},
                status=status.HTTP_400_BAD_REQUEST
            )

        description = request.data.get('description', "")
        name = request.data.get('name', None)

        for filename in request.FILES.keys():
            try:
                document = add_file(request.FILES[filename], user=user,
                                description=description, name=name)
                CompanyFile.objects.create(document=document,
                                           company=company)
                return Response(CreateFileSerializer(document).data)

            except ValueError as v:
                return Response(
                    data={"detail": str(v)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            data={"detail": "Нет файла"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    
    
class DeleteCompanyApprovementFileView(AppCompanyAPIView):
    

    def post(self, request):
        
        relation: UserCompanyRelation = request.user
        company = relation.company

        if not relation.company_info_permission :
            return Response(**NOT_HAVE_PERMISSIONS)
        
        file_id = int(request.data.get('id', 0))

        file = get_object_or_404(CompanyFile, id=file_id)
        file_owner_company = file.company

        if company != file_owner_company:
            return Response(
                data={"detail": "Данный файл не имеет отношения к вашей компании"},
                status=status.HTTP_400_BAD_REQUEST
            )

        file.company = None
        file.save()
        return Response({"detail": "ok"})


class UpdateCompanyApprovementFileView(AppCompanyAPIView):
    

    def post(self, request):
        relation: UserCompanyRelation = request.user
        user = relation.user
        company = relation.company

        if not relation.company_info_permission:
            return Response(**NOT_HAVE_PERMISSIONS)

        file_id = int(request.data.get('id', 0))
        file = get_object_or_404(CompanyFile, id=file_id)
        document = file.document
        file_owner_company = file.company

        if company != file_owner_company:
            return Response(
                data={"detail": "Данный файл не имеет отношения к вашей компании"},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data
        serializer = UpdateFileSerializer(document, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"detail": "ok!"})


# PARTNERS

class AddPartnerRelationsCompanyView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        partner_id = int(request.data.get("partner_id", 0))
        company_id = int(request.data.get("company_id", 0))
        partner = get_object_or_404(Company, id=partner_id)
        company = get_object_or_404(Company, id=company_id)
        if partner_id == company_id:
            return Response(data={"detail": "Нельзя добавить в партнеры"}, status=status.HTTP_400_BAD_REQUEST)
        relations = UserCompanyRelation.objects.filter(company=company, user=request.user)
        if not relations.exists() or not relations.first().company_info_permission:
            return Response(data={"detail": "Нет прав на компанию"}, status=status.HTTP_400_BAD_REQUEST)
        relation_to = OrganizationsRelationship.objects.filter(
            company_1=company,
            company_2=partner,
            relationship_type=ORGANIZATIONS_RELATIONSHIP_TYPE.PARTNERSHIP)
        relation_from = OrganizationsRelationship.objects.filter(
            company_2=company,
            company_1=partner,
            relationship_type=ORGANIZATIONS_RELATIONSHIP_TYPE.PARTNERSHIP)
        if relation_from.exists():
            if relation_from.first().company_2_confirmed:
                return Response(data={"detail": "Партнер уже добавлен"}, status=status.HTTP_400_BAD_REQUEST)
            relation_from.update(company_2_confirmed=True)
        else:
            if relation_to.exists():
                error_message = "Партнер уже добавлен" if relation_to.first().company_2_confirmed else "Заявка уже отправлена"
                return Response(data={"detail": error_message}, status=status.HTTP_400_BAD_REQUEST)
            else:
                OrganizationsRelationship.objects.create(
                    company_1=company,
                    company_2=partner,
                    company_1_confirmed=True,
                    relationship_type=ORGANIZATIONS_RELATIONSHIP_TYPE.PARTNERSHIP)

        return Response(200)


class PotentialPartnersListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = get_object_or_404(Company, id=int(request.GET.get("id", 0)))
        company_relation = UserCompanyRelation.objects.filter(user=request.user, company=company)
        if not company_relation.exists():
            return Response(data={"detail": "Не является членом компании"}, status=status.HTTP_400_BAD_REQUEST)
        relations = get_potential_relationships_for_company(company)

        def get_id(obj):
            return {
                "id": obj.company_1.id,
                "name": obj.company_1.name,
                "inn": obj.company_1.inn,
                "type": obj.company_1.company_type,
                "verified": obj.verified,
            }

        companies_id = map(get_id, relations)
        return Response({"list": companies_id})


class PotentialPartnersAmountView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = get_object_or_404(Company, id=int(request.GET.get("id", 0)))
        company_relation = UserCompanyRelation.objects.filter(user=request.user, company=company)
        if not company_relation.exists() or not company_relation.first().company_info_permission:
            return Response(data={"detail": "Не является членом компании"}, status=status.HTTP_400_BAD_REQUEST)
        relations_amount = get_potential_relationships_for_company(company).count()

        return Response({"amount": relations_amount})


class ActualPartnersListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = get_object_or_404(Company, id=int(request.GET.get("id", 0)))
        company_relation = UserCompanyRelation.objects.filter(user=request.user, company=company)
        if not company_relation.exists():
            return Response(data={"detail": "Не является членом компании"}, status=status.HTTP_400_BAD_REQUEST)
        relations = OrganizationsRelationship.objects.filter(
            Q(company_1=company) | Q(company_2=company),
            company_2_confirmed=True,
            company_1_confirmed=True,
            relationship_type=ORGANIZATIONS_RELATIONSHIP_TYPE.PARTNERSHIP,
        )

        def get_id(obj):
            if obj.company_1.id == company.id:
                return {
                    "id": obj.company_2.id,
                    "name": obj.company_2.name,
                    "inn": obj.company_2.inn,
                    "type": obj.company_2.company_type,
                    "verified": obj.verified,
                }
            return {
                "id": obj.company_1.id,
                "name": obj.company_1.name,
                "inn": obj.company_1.inn,
                "type": obj.company_1.company_type,
                "verified": obj.verified,
            }

        companies_id = map(get_id, relations)
        return Response({"list": companies_id})


class ConfirmPartnersView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        partner_id = int(request.data.get("partner_id", 0))
        company_id = int(request.data.get("company_id", 0))
        partner = get_object_or_404(Company, id=partner_id)
        company = get_object_or_404(Company, id=company_id)
        # return Response(status=status.HTTP_204_NO_CONTENT)
        relations = UserCompanyRelation.objects.filter(company=company, user=request.user)
        if not relations.exists() or not relations.first().company_info_permission:
            return Response(data={"detail": "Нет прав на компанию"},
                            status=status.HTTP_400_BAD_REQUEST)
        OrganizationsRelationship.objects.filter(
            company_1=partner,
            company_2=company,
            company_1_confirmed=True,
            relationship_type=ORGANIZATIONS_RELATIONSHIP_TYPE.PARTNERSHIP
        ).update(company_2_confirmed=True)

        return Response(200)


class RejectPartnersView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # return Response(status=status.HTTP_204_NO_CONTENT)
        partner_id = int(request.data.get("partner_id", 0))
        company_id = int(request.data.get("company_id", 0))
        partner = get_object_or_404(Company, id=partner_id)
        company = get_object_or_404(Company, id=company_id)
        relations = UserCompanyRelation.objects.filter(company=company, user=request.user)
        if not relations.exists() or not relations.first().company_info_permission:
            return Response(data={"detail": "Нет прав на компанию"},
                            status=status.HTTP_400_BAD_REQUEST)
        OrganizationsRelationship.objects.filter(
            company_1=partner,
            company_2=company,
            company_1_confirmed=True,
            relationship_type=ORGANIZATIONS_RELATIONSHIP_TYPE.PARTNERSHIP
        ).update(company_2_confirmed=False)

        return Response(200)


class AddRelationshipFileView(AppCompanyAPIView):
    

    def post(self, request):

        relation: UserCompanyRelation = request.user
        company = relation.company
        user = relation.user

        if not relation.company_info_permission:
            return Response(**NOT_HAVE_PERMISSIONS)

        other_company_id = request.data.get('other_company_id')
        other_company = get_object_or_404(Company, id=other_company_id)

        try:
            company_relation = get_object_or_404(OrganizationsRelationship,
                                                 company_1=other_company,
                                                 company_2=company)
        except:
            #_, company_relation = OrganizationsRelationship.objects.get_or_create(company_1=company,
                                                                                  #company_2=other_company)
            company_relation = get_object_or_404(OrganizationsRelationship,
                                                 company_1=company,
                                                 company_2=other_company)

        if OrganizationsRelationshipFile.objects.filter(
                relation=company_relation).count() >= 1:  # Вдруг решим потом больше одного файла
            return Response(
                data={"detail": "Максимальное число файлов для партнерства: 1"},
                status=status.HTTP_400_BAD_REQUEST
            )

        description = request.data.get('description', "")
        name = request.data.get('name', None)

        for filename in request.FILES.keys():
            try:
                document = add_file(request.FILES[filename], user=user,
                                    description=description, name=name)
                OrganizationsRelationshipFile.objects.create(document=document,
                                           relation=company_relation)
                return Response(CreateFileSerializer(document).data)

            except ValueError as v:
                return Response(
                    data={"detail": str(v)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            data={"detail": "Нет файла"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    
class DeleteRelationshipFileView(AppCompanyAPIView):
    

    def post(self, request):
        
        relation: UserCompanyRelation = request.user
        company = relation.company

        if not relation.company_info_permission:
            return Response(**NOT_HAVE_PERMISSIONS)

        file_id = int(request.data.get('id', 0))

        file = get_object_or_404(OrganizationsRelationshipFile, id=file_id)
        relationship = file.relation

        relationship = file.relation
        if relationship is None:
            return Response(
                data={"detail": "Данный файл не имеет отношения к вашей компании"},
                status=status.HTTP_400_BAD_REQUEST
            )

        company_1 = relationship.company_1
        company_2 = relationship.company_2

        if company != company_1 and company != company_2:
            return Response(
                data={"detail": "Данный файл не имеет отношения к вашей компании"},
                status=status.HTTP_400_BAD_REQUEST
            )

        file.relation = None
        file.save()
        return Response({"relation": relationship.id})



class UpdateRelationshipFileView(AppCompanyAPIView):
    

    def post(self, request):
        relation: UserCompanyRelation = request.user
        user = relation.user
        company = relation.company

        if not relation.company_info_permission :
            return Response(**NOT_HAVE_PERMISSIONS)

        file_id = int(request.data.get('id', 0))
        file = get_object_or_404(OrganizationsRelationshipFile, id=file_id)

        relationship = file.relation
        if relationship is None:
            return Response(
                data={"detail": "Данный файл не имеет отношения к вашей компании"},
                status=status.HTTP_400_BAD_REQUEST
            )

        company_1 = relationship.company_1
        company_2 = relationship.company_2

        if company != company_1 and company != company_2:
            return Response(
                data={"detail": "Данный файл не имеет отношения к вашей компании"},
                status=status.HTTP_400_BAD_REQUEST
            )



        document = file.document
        data = request.data
        serializer = UpdateFileSerializer(document, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"detail": "ok!"})


# INVITATION LINKS


class SendInvitationLinkView(AppCompanyAPIView):
    

    def post(self, request):
        
        relation: UserCompanyRelation = request.user
        user = relation.user
        company = relation.company
        
        has_access = relation.add_users_permission
        if not has_access:
            return Response(
                data={"detail": "Нет прав"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        email = request.data.get('email')
        user_to_invite = User.objects.get(email=email)
        new_relation, created = UserCompanyRelation.objects.get_or_create(user=user_to_invite,
                                                                          company=company)
        data = request.data
        serializer = UserCompanyRelationForInvitationLinkSerializer(new_relation,
                                                                    data=data,
                                                                    partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(creator=user)

        invitation = TokenInviteToCompany.objects.create(user=user_to_invite,
                                                         company=company)

        text = f"Здравствуйте!\nТут будет ссылка в компанию {company.name},\nно пока вот вам токен:\n{invitation.token}"
        send(email,
             subject="Ссылка с приглашением в компанию",
             text=text)
        return Response({"invitation": invitation.token})


class AcceptInvitationLinkView(AppUsersAPIView):
    

    def post(self, request):

        user = request.user
        token = request.data.get("token")
        invitation = get_object_or_404(TokenInviteToCompany, token=token)

        time_now = datetime.datetime.now(datetime.timezone.utc)
        if (time_now - invitation.created_at).days >= 7:
            return Response(
                data={"detail": "Ссылка недействительна"},
                status=status.HTTP_400_BAD_REQUEST
            )

        invited_user = invitation.user
        if invited_user != user:
            return Response(
                data={"detail": "Данная ссылка предназначалась другому пользователю"},
                status=status.HTTP_400_BAD_REQUEST
            )
        company = invitation.company
        relation = UserCompanyRelation.objects.get(user=user,
                                                   company=company)
        relation.verified = False
        relation.save()

        return Response({"ok": "POST request processed"})


class GetCompanyFromInvitationLinkView(AppUsersAPIView):
    

    def post(self, request):
        user = request.user
        token = request.data.get("token")
        invitation = TokenInviteToCompany.objects.get(token=token)
        company = invitation.company
        serializer = CompanyMainInformationSerializer(company)

        return Response(serializer.data)
  
    
class InviteCompanyView(AppCompanyAPIView):
    
    
    def post(self, request):
        
        relation: UserCompanyRelation = request.user
        user = relation.user
        company_that_invited = relation.company
        
        email = request.data.get('email')
        token = TokenInviteOtherCompany.objects.create(company_that_invited=company_that_invited,
                                                       email_to_invite=email)
        
        text = f"Здравствуйте!\nКомпания {company_that_invited.name} приглашает вас зарегистрироваться \
        на торговой плаиформе SupplyDirector, тут будет ссылка, но пока вот вам токен:\n{token.token}"
        
        send(email,
             subject="Регистрация на торговой платформе SupplyDirector",
             text=text)
    
        return Response({"link": token.token})




class AddOkvedToTableView(APIView):
    

    def post(self, request):
        path = request.data.get('path', 'okved.csv') # path to csv with okveds
        with open('okved_utf-8.csv', 'r', encoding="utf-8") as okveds:
            for line in okveds.readlines():
                _, code, name = line.replace('"', '').split(";")
                _, okved = Okved.objects.get_or_create(code=code,
                                                       name=name)
        return Response({"ok": "POST request processed"})
    
    
    
class SearchOkvedView(AppCompanyAPIView):
    authentication_classes = []
    permission_classes = []
    

    def get(self, request):
        q = request.GET.get('q', '').strip()
        if q:
            okveds = Okved.objects.filter(Q(name__icontains=q) | Q(code__icontains=q))
        else:
            okveds = Okved.objects.all()
        
        serializer = OkvedSerializer(okveds[:10], many=True)
        
        return Response({"results": serializer.data})
    
    
    
    

    

            


# class GetListCompanyProducerView(AppCompanyAPIView):
#     
#
#     def get(self, request):
#         relation: UserCompanyRelation = request.user
#         company_name = request.query_params["company"]
#         companies = Company.objects.filter(name__contains=company_name)[:10]
#         return Response({
#             'list': companies,
#         })
#
#
# class GetListFactoryProducerView(AppCompanyAPIView):
#     
#
#     def get(self, request):
#         relation: UserCompanyRelation = request.user
#         factory_name = request.query_params["factory"]
#         factories = Factory.objects.filter(name__contains=factory_name)[:10]
#         return Response({
#             'list': factories,
#         })