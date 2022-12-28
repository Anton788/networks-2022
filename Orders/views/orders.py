from django.http import QueryDict
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication, BasicAuthentication, SessionAuthentication
import Orders.constants.request_delivery_types as REQUEST_DELIVERY_TYPES
import Orders.constants.product_request_status as PRODUCT_REQUEST_STATUS
from Orders.models import OrderChain, ProductRequest, ProductRequestImage, ProductRequestFile
from Orders.serializers import CreateUpdateProductRequestSerializer, GetProdRequestSummarySerializer, \
    GetRequestProductPreviewSerializer, GetOrderChainPreviewSerializer, UpdateAllProductRequestSerializer, \
    CreateProductRequestFileSerializer, CreateProductRequestImageSerializer, AllParamsOrderChain, \
    GetMoreInfoByCreatedProductRequestSerializer, GetRequestInfoSerializer
from Orders.utils.file_processing import add_image_to_request, add_file_to_request
from Products.models import (
    Product,
    ProductImage,
    ProductFile, ProductsProcessingFile)
from Organizations.models import Company
from Organizations.serializers import CompanyRequisitesSerializer

import Orders.constants.order_chain_status as ORDER_CHAIN_STATUS

from APIBackendService.views import AppCompanyAPIView
from Notifications.constants import ADMIN_INFO

from Users.models import (
    User,
    UserFactoryRelation,
    UserCompanyRelation,
)

from Products.serializers import (
    CreateUpdateProductSerializer,
    GetProductSerializer,
    CreateProductImageSerializer,
    SetMainImageSerializer,
    GetProductImageSerializer, ChangeImageDescriptionSerializer, ChangeFileInfoSerializer, CreateProductFileSerializer,
    GetProductPreviewSerializer, GetProductUpdateSerializer,
    ProductsProcessingFileSerializer, GetProductImageUpdateSerializer)

import Products.constants.products_file_check_status as PRODUCTS_FILE_CHECK_STATUS

NOT_HAVE_PERMISSIONS = {
    "data": {"detail": "Нет прав"},
    "status": status.HTTP_400_BAD_REQUEST,
}


def company_create_orders_permission(user, company_id):
    if company_id:
        company = get_object_or_404(Company, id=company_id)
        company_relation_queryset = UserCompanyRelation.objects.filter(user=user, company=company)
        if (not company_relation_queryset.exists()) or \
                not company_relation_queryset.first().ordering_permission:
            return False
    return True


class CreateProductRequestView(AppCompanyAPIView):
    

    def post(self, request):

        relation: UserCompanyRelation = request.user
        has_access = relation.ordering_permission
        if not has_access:
            return Response(**NOT_HAVE_PERMISSIONS)

        company_customer = relation.company
        req = request.data.get("request", "")
        product_id = request.data.get("product", None)

        data = QueryDict(mutable=True)
        data.update(request.data)
        data["delivery_type"] = REQUEST_DELIVERY_TYPES.ON_FACTORY
        data["user_id"] = relation.user_id
        # print(data)
        # try:
        serializer = CreateUpdateProductRequestSerializer(data=data, partial=False)
        serializer.is_valid(raise_exception=True)
        prod_req = serializer.save()
        # except Exception as e:
        #     print("ERR:", e)
        product = get_object_or_404(Product, id=product_id)
        # print(product)
        company_executor = product.company
        if company_executor == company_customer:
            return Response(
                data={"detail": "Нельзя заказывать товар у самого себя"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # factory = product.factory
        # print(f"Factory: {factory}")
        # if factory:
        #     ProductRequest.objects.filter(id=prod_req.id).update(factory_executor=factory)
        #     OrderChain.objects.create(product_request=prod_req, factory_executor=factory)
        # else:
        ProductRequest.objects.filter(id=prod_req.id).update(company_executor=company_executor)
        OrderChain.objects.create(product_request=prod_req, company_executor=company_executor)
        return Response({"id": prod_req.id})


class CreateAnonymousProductRequestView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        req = request.data.get("request", "")
        company_id = request.data.get("customer", None)

        has_access = company_create_orders_permission(user, company_id=company_id)

        if not has_access:
            return Response(**NOT_HAVE_PERMISSIONS)
        print(request.data)
        if company_id is None:
            return Response(
                data={
                    "detail": "Заказ должен быть привязан к компании",
                    "customer": "Нужно выбрать компанию",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        data = QueryDict(mutable=True)
        # print(request.data)
        data.update(request.data)
        data["delivery_type"] = REQUEST_DELIVERY_TYPES.ON_FACTORY
        data["user"] = request.user.id
        data["status"] = PRODUCT_REQUEST_STATUS.CONSTRUCTION
        # print(data)
        serializer = CreateUpdateProductRequestSerializer(data=data, partial=False)
        serializer.is_valid(raise_exception=True)
        # print(serializer.validated_data)
        prod_req = serializer.save()
        return Response({"id": prod_req.id})


class UpdateInformationAnonymousProductRequestView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        request_id = request.data.get("id", "")
        prod_req = get_object_or_404(ProductRequest, id=request_id)
        has_access = company_create_orders_permission(user, company_id=prod_req.customer.id)

        if not has_access:
            return Response(**NOT_HAVE_PERMISSIONS)
        data = QueryDict(mutable=True)
        data.update(request.data)
        data.pop("id")
        serializer = UpdateAllProductRequestSerializer(prod_req, data=data)
        serializer.is_valid(raise_exception=True)
        prod_req = serializer.save()
        return Response({"id": prod_req.id})


class AddImagesAnonymousProductRequestView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        # print(request.data)
        request_id = request.data.get("id", "")
        prod_req = get_object_or_404(ProductRequest, id=request_id)
        has_access = company_create_orders_permission(user, company_id=prod_req.customer.id)

        if not has_access:
            return Response(**NOT_HAVE_PERMISSIONS)

        if ProductRequestImage.objects.filter(request=prod_req).count() >= 10:
            return Response(
                data={"detail": "Максимальное число изображений: 10"},
                status=status.HTTP_400_BAD_REQUEST
            )

        description = request.data.get('description', "")

        for filename in request.FILES.keys():
            try:
                image = add_image_to_request(request.FILES[filename], request=prod_req, description=description)
                return Response(CreateProductRequestImageSerializer(image).data)
            except ValueError as v:
                return Response(
                    data={"detail": str(v)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            data={"detail": "Нет картинки"},
            status=status.HTTP_400_BAD_REQUEST
        )


class AddFilesAnonymousProductRequestView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        request_id = request.data.get("id", "")
        prod_req = get_object_or_404(ProductRequest, id=request_id)
        has_access = company_create_orders_permission(user, company_id=prod_req.customer.id)

        if not has_access:
            return Response(**NOT_HAVE_PERMISSIONS)

        if ProductRequestFile.objects.filter(request=prod_req).count() >= 5:
            return Response(
                data={"detail": "Максимальное число файлов: 5"},
                status=status.HTTP_400_BAD_REQUEST
            )

        description = request.data.get('description', "")
        name = request.data.get('name', None)
        # print(request.data)
        # print("completed")
        for filename in request.FILES.keys():
            try:
                file = add_file_to_request(request.FILES[filename], request=prod_req, description=description,
                                           name=name)
                return Response(CreateProductRequestFileSerializer(file).data)

            except ValueError as v:
                return Response(
                    data={"detail": str(v)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            data={"detail": "Нет файла"},
            status=status.HTTP_400_BAD_REQUEST
        )


class CompleteAnonymousProductRequestView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        request_id = request.data.get("id", "")
        prod_req = get_object_or_404(ProductRequest, id=request_id)
        has_access = company_create_orders_permission(user, company_id=prod_req.customer.id)

        if not has_access:
            return Response(**NOT_HAVE_PERMISSIONS)
        print(ProductRequest.objects.filter(id=request_id))
        ProductRequest.objects.filter(id=request_id).update(status=PRODUCT_REQUEST_STATUS.ACTIVE)
        return Response({"Answer": "Поиск начался"})


class ReceivedProductRequestListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company_id = request.GET.get("company", None)
        factory_id = request.GET.get("factory", None)
        # if factory_id is None:
        print(company_id)
        company = get_object_or_404(Company, id=int(company_id))
        reqs = OrderChain.objects.filter(company_executor=company)
        user_relations = UserCompanyRelation.objects.filter(user=request.user, company=company)
        has_access = user_relations.exists()
        if not has_access:
            return Response(**NOT_HAVE_PERMISSIONS)

        can_edit = user_relations.first().ordering_permission

        # else:
        #     factory = get_object_or_404(Factory, id=int(factory_id))
        #     reqs = OrderChain.objects.filter(factory_executor=factory)
        #     user_relations = UserFactoryRelation.objects.filter(user=request.user, factory=factory)
        #     has_access = user_relations.exists()
        #     if not has_access:
        #         return Response(**NOT_HAVE_PERMISSIONS)
        #
        #     can_edit = user_relations.first().create_orders_permission

        reqs_list = []
        for req in reqs:
            try:
                reqs_list.append(GetOrderChainPreviewSerializer(req).data)
            except Exception as e:
                print("Err:", e)

        return Response({
            "list": reqs_list,
            "edit": can_edit,
        })


class GetMoreInfoByReceivedProductRequestView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        chain_id = request.GET.get("id", None)
        prod_chain = get_object_or_404(OrderChain, id=chain_id)
        if prod_chain.company_executor is not None:
            user_relations = UserCompanyRelation.objects.filter(user=request.user, company=prod_chain.company_executor)
            has_access = user_relations.exists()
            if not has_access:
                return Response(**NOT_HAVE_PERMISSIONS)
        # elif prod_chain.factory_executor is not None:
        #     user_relations = UserFactoryRelation.objects.filter(user=request.user, factory=prod_chain.factory_executor)
        #     has_access = user_relations.exists()
        #     if not has_access:
        #         return Response(**NOT_HAVE_PERMISSIONS)
        else:
            return Response({"data": {"detail": "Пользователь должен быть членом компании или орагнизации."}})

        request_info = AllParamsOrderChain(prod_chain).data
        return Response({"data": request_info})


class CreatedProductRequestListView(APIView):
    """
    Product requests that were created by company
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        company_id = int(request.GET.get("company", 0))
        company = get_object_or_404(Company, id=company_id)
        user_relations = UserCompanyRelation.objects.filter(user=request.user, company=company)
        has_access = user_relations.exists()
        if not has_access:
            return Response(**NOT_HAVE_PERMISSIONS)

        can_edit = user_relations.first().ordering_permission

        reqs = ProductRequest.objects.filter(customer=company)
        reqs_list = []
        for req in reqs:
            try:
                reqs_list.append(GetRequestProductPreviewSerializer(req).data)
            except Exception as e:
                print("Err", e)

        return Response({
            "list": reqs_list,
            "edit": can_edit,
        })


class GetMoreInfoByCreatedProductRequestView(AppCompanyAPIView):
    

    def get(self, request):
        relation: UserCompanyRelation = request.user
        # user = relation.user
        request_id = request.GET.get("id", None)
        prod_req = get_object_or_404(ProductRequest, id=request_id)
        customer = prod_req.customer
        company = relation.company
        if customer != company:
            return Response(**NOT_HAVE_PERMISSIONS)

        can_edit = relation.ordering_permission
        request_info = GetMoreInfoByCreatedProductRequestSerializer(prod_req).data

        return Response({
            "request": request_info,
            "edit": can_edit,
        })


class GetRequestInfoView(AppCompanyAPIView):
    

    def get(self, request):
        relation: UserCompanyRelation = request.user
        user = relation.user
        request_id = request.GET.get("id", None)
        prod_req = get_object_or_404(ProductRequest, id=request_id)
        customer = prod_req.customer
        company = relation.company
        if customer != company:
            return Response(**NOT_HAVE_PERMISSIONS)

        request_info = GetRequestInfoSerializer(prod_req).data

        return Response({
            "request": request_info
        })


class RejectProductRequestView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        company_executor_id = request.data.get("company_executor", None)
        # factory_executor_id = request.data.get("factory_executor", None)
        request_id = request.data.get("product_request", None)

        # if factory_executor_id is None:
        company_executor = get_object_or_404(Company, id=company_executor_id)
        user_relations = UserCompanyRelation.objects.filter(user=request.user, company=company_executor)
        has_access = user_relations.exists()
        if not has_access or not user_relations.first().ordering_permission:
            return Response(**NOT_HAVE_PERMISSIONS)

        req = get_object_or_404(ProductRequest, id=request_id)
        OrderChain.objects.filter(product_request=req, company_executor=company_executor).update(
            status=ORDER_CHAIN_STATUS.REJECT)
        # else:
        #     factory_executor = get_object_or_404(Factory, id=factory_executor_id)
        #     user_relations = UserFactoryRelation.objects.filter(user=request.user, factory=factory_executor)
        #     has_access = user_relations.exists()
        #     if not has_access or not user_relations.first().create_orders_permission:
        #         return Response(**NOT_HAVE_PERMISSIONS)
        #     req = get_object_or_404(ProductRequest, id=request_id)
        #     OrderChain.objects.filter(product_request=req, factory_executor=factory_executor).update(
        #         status=ORDER_CHAIN_STATUS.REJECT)
        ProductRequest.objects.filter(id=request_id).update(status=PRODUCT_REQUEST_STATUS.HISTORY)
        return Response(200)


class AcceptProductRequestView(AppCompanyAPIView):
    
    
    def post(self, request):
        relation: UserCompanyRelation = request.user
        user = relation.user
        company_executor = relation.company
        #company_executor_id = request.data.get("company_executor", None)
        
        factory_executor_id = request.data.get("factory_executor", None)
        request_id = request.data.get("product_request", None)
        product_request = ProductRequest.objects.get(id=request_id)
        company_customer = product_request.customer
        #company_executor = get_object_or_404(Company, id=company_executor_id)
        if company_executor == company_customer:
            return Response(
                data={"detail": "Нельзя заказывать товар у самого себя"},
                status=status.HTTP_400_BAD_REQUEST
            )
        #has_access = user_relations.exists()
        has_access = relation.proposal_permission
        if not has_access:
            return Response(**NOT_HAVE_PERMISSIONS)

        req = get_object_or_404(ProductRequest, id=request_id)
        OrderChain.objects.filter(product_request=req, company_executor=company_executor).update(
            status=ORDER_CHAIN_STATUS.CONFIRMED)
        chain = get_object_or_404(OrderChain, product_request=req, company_executor=company_executor)
        # else:
        #     factory_executor = get_object_or_404(Factory, id=factory_executor_id)
        #     company_executor = factory_executor.company
        #     if company_executor == company_customer:
        #         return Response(
        #         data={"detail": "Нельзя заказывать товар у самого себя"},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        #     user_relations = UserFactoryRelation.objects.filter(user=user, factory=factory_executor)
        #     has_access = user_relations.exists()
        #     if not has_access or not user_relations.first().create_orders_permission:
        #         return Response(**NOT_HAVE_PERMISSIONS)
        #     req = get_object_or_404(ProductRequest, id=request_id)
        #     OrderChain.objects.filter(product_request=req, factory_executor=factory_executor).update(
        #         status=ORDER_CHAIN_STATUS.CONFIRMED)
        #     chain = get_object_or_404(OrderChain, product_request=req, factory_executor=factory_executor)
        # print(request.data)
        serializer = AllParamsOrderChain(chain, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        # print(serializer.validated_data)
        serializer.save()
        ProductRequest.objects.filter(id=request_id).update(status=PRODUCT_REQUEST_STATUS.ACTIVE)
        
        serializer = CompanyRequisitesSerializer(company_customer)
        #serializer.is_valid(raise_exception=True)
        requisites = serializer.data
        return Response({
            "bank_requisites": requisites
        })


class CompleteProductRequestView(AppCompanyAPIView):
    

    def post(self, request):
        relation: UserCompanyRelation = request.user
        user = relation.user
        company_executor = relation.company
        # company_executor_id = request.data.get("company_executor", None)

        factory_executor_id = request.data.get("factory_executor", None)
        request_id = request.data.get("product_request", None)
        product_request = ProductRequest.objects.get(id=request_id)
        company_customer = product_request.customer
        # company_executor = get_object_or_404(Company, id=company_executor_id)
        if company_executor == company_customer:
            return Response(
                data={"detail": "Нельзя заказывать товар у самого себя"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # has_access = user_relations.exists()
        has_access = relation.proposal_permission
        if not has_access:
            return Response(**NOT_HAVE_PERMISSIONS)

        req = get_object_or_404(ProductRequest, id=request_id)
        OrderChain.objects.filter(product_request=req, company_executor=company_executor).update(
            status=ORDER_CHAIN_STATUS.COMPLETED)
        return Response(status=status.HTTP_200_OK)


class SentProductRequestStatisticsView(AppCompanyAPIView):
    """
        Метрика показывающая процент выполненных заказов
    """
    

    def post(self, request):
        relation: UserCompanyRelation = request.user
        user = relation.user
        company = relation.company

        prod_reqs = ProductRequest.objects.filter(customer=company, status=PRODUCT_REQUEST_STATUS.ACTIVE)
        completed = 0
        confirmed = 0
        waiting = 0
        for req in prod_reqs:
            try:
                chain = OrderChain.objects.get(product_request=req)
                if chain.status == ORDER_CHAIN_STATUS.COMPLETED:
                    completed += 1
                elif chain.status == ORDER_CHAIN_STATUS.CONFIRMED:
                    confirmed += 1
                elif chain.status == ORDER_CHAIN_STATUS.WAITING:
                    waiting += 1
            except:
                continue
        count_prod_reqs = len(prod_reqs)
        result = {
            "waiting": waiting,
            "completed": completed,
            "completed_percent": completed / max(waiting + completed + confirmed, 1),
            "confirmed": confirmed,
            "rejected": count_prod_reqs - waiting - completed - confirmed,
        }
        return Response(data=result)


class ReceivedProductRequestStatisticsView(AppCompanyAPIView):
    """
        Метрика показывающая агрегированную статистику входящих заказов
    """
    

    def post(self, request):
        relation: UserCompanyRelation = request.user
        user = relation.user
        company = relation.company

        chains = OrderChain.objects.filter(company_executor=company)
        completed = 0
        confirmed = 0
        waiting = 0
        for chain in chains:
            if chain.status == ORDER_CHAIN_STATUS.COMPLETED:
                completed += 1
            elif chain.status == ORDER_CHAIN_STATUS.CONFIRMED:
                confirmed += 1
            elif chain.status == ORDER_CHAIN_STATUS.WAITING:
                waiting += 1
        count_chains = len(chains)
        result = {
            "waiting": waiting,
            "completed": completed,
            "completed_percent": completed / max(waiting + completed + confirmed, 1),
            "confirmed": confirmed,
            "rejected": count_chains - waiting - completed - confirmed,
        }
        return Response(data=result)
