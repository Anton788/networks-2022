from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.db.models import Max
from drf_yasg.utils import swagger_auto_schema
from collections import defaultdict

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token

from APIBackendService.views import AppUsersAPIView
from Notifications.constants import ADMIN_INFO
from Notifications.models import SystemNotification, UserNotification
from Organizations.models import Company
from Users.utils import get_random_password
from Users.utils.relations import can_user_edit_another_user
from .serializers import UserCreateUpdateSerializer, LoginUserQuerySerializer, InfoUserSerializer, \
    InfoUpdateUserSerializer

import requests
import meilisearch

from Users.models import User, UserCompanyRelation, UserCompanyRelationAuthToken


class AuthView(APIView):
    @swagger_auto_schema(
        operation_summary='Login',
        operation_description='Get authentication token for exists user',
        query_serializer=LoginUserQuerySerializer,
        responses={
            200: 'User successfully authenticated',
            400: 'Bad request',
            401: 'Incorrect password',
            404: 'User not found',
        }
    )
    def get(self, request):
        serializer = LoginUserQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(User, username=serializer.validated_data['username'])
        user.last_login = timezone.now()
        user.save()

        if user.check_password(serializer.validated_data['password']):
            token, created = Token.objects.get_or_create(user=user)
            return Response({'Token': str(token)})
        else:
            raise AuthenticationFailed()

    @swagger_auto_schema(
        operation_summary='Register',
        operation_description='Create user and return its authentication token',
        request_body=UserCreateUpdateSerializer,
        responses={
            200: 'User successfully created and authenticated',
            400: 'Bad request',
        }
    )
    def post(self, request):
        # print("START DATA:", request.data)
        serializer = UserCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token, created = Token.objects.get_or_create(user=user)
        return Response({'Token': str(token)})


class InformationUserView(AppUsersAPIView):
    """
    Информация о пользователе
    """
    

    def get(self, request):
        return Response(InfoUserSerializer(request.user).data)

    def post(self, request):
        # data = {
        #     "middle_name": "last_namelast_namelast_namelast_namelast_namelastlast_namelast_namelast_namelast_namelast_namelast_namelast_namelast_namelast_namelast_namelast_namelastlast_namelast_namelast_namelast_namelast_namelast_namelast_namelast_namelast_namelast_namelast_namelastlast_namelast_namelast_namelast_namelast_namelast_name",
        #     "last_name": "last_namelast_namelast_namelast_namelast_namelastlast_namelast_namelast_namelast_namelast_namelast_name"
        #                      "last_namelast_namelast_namelast_namelast_namelast_name_namelast_namelast_namelast_namelast_namelast_namelast_name"}

        data = request.data
        serializer = InfoUpdateUserSerializer(instance=request.user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        # print(serializer.errors)
        user = serializer.save()
        return Response(serializer.data)


class UpdateUserPasswordView(AppUsersAPIView):
    """
    Смена пароля
    """
    

    def get(self, request, user_id=None):
        user = request.user
        if user_id is not None:
            user_to_edit = get_object_or_404(User, id=int(user_id))
            if not (user.id != user_to_edit.id and can_user_edit_another_user(user, user_to_edit)):
                return Response(
                    data={"detail": "Нет прав на изменение"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            new_password = get_random_password()
            user_to_edit.set_password(new_password)
            user_to_edit.change_password_date = None
            user_to_edit.save()

            Token.objects.filter(user=user_to_edit).delete()
            return Response({"password": new_password})
        else:
            serializer = LoginUserQuerySerializer(data={
                'password': request.GET.get("password", ""),
                "username": user.username,
            })
            serializer.is_valid(raise_exception=True)
            if user.check_password(serializer.validated_data['password']):
                new_password = request.GET.get("new_password", "")
                user.set_password(new_password)
                user.change_password_date = timezone.now().date()

                Token.objects.filter(user=user).delete()
                token, created = Token.objects.get_or_create(user=user)
                return Response({'Token': str(token)})
            else:
                raise AuthenticationFailed()


class GetCompanyRelationTokenView(AppUsersAPIView):
    """
    View for getting user's token for API from company
    """
    

    def get(self, request, company_id=None):
        user = request.user

        company = get_object_or_404(Company, id=int(company_id))
        relations = UserCompanyRelation.objects.filter(company=company, user=user)
        if not relations.exists():
            return Response(
                data={"detail": "Нет прав на работу с данной компанией"},
                status=status.HTTP_400_BAD_REQUEST
            )
        token_obj = UserCompanyRelationAuthToken.objects.create(
            user=relations.first(),
            expired=timezone.datetime.utcnow() + timezone.timedelta(days=30),
        )

        return Response({'token': token_obj.key})
