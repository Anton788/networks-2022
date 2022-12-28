from django.shortcuts import render

from Users.models import (
    User,
    UserFactoryRelation,
    UserCompanyRelation,
)

from .models import Task

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication, BasicAuthentication, SessionAuthentication

from django.utils.crypto import get_random_string

# Create your views here.

        