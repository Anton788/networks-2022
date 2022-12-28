from rest_framework.views import APIView
from rest_framework.response import Response
from Products.models import *
from Users.models import User, UserCompanyRelation
from Organizations.models import *
from Services.models import Task
from Documents.utils.storage import add_file_to_storage, delete_file_from_storage, \
                                   add_excel_to_storage
                                   
from rest_framework.authentication import TokenAuthentication, BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser

import hashlib
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from Products.serializers import ProductTableSerializer, FilterParamsSerializer
import os
import re

import datetime

from Services.constants.download_status import (
    WAITING,
    FINISHED,
    REJECTED,
    IN_PROGRESS
)

from Services.constants.tasks import (
    CREATE_EXCEL_TABLE_FROM_PRODUCTS,
    OTHER,
)

from Products.constants.product_condition import (
    NEW,
    USED,
)

from Documents.models import Photo

from Notifications.constants import ADMIN_INFO
from APIBackendService.views import AppCompanyAPIView

from rest_framework import status

NOT_HAVE_PERMISSIONS = {
    "data": {"detail": "Нет прав"},
    "status": status.HTTP_400_BAD_REQUEST,
}


# TEST
class UploadImageView(AppCompanyAPIView):
    

    def post(self, request):

        relation: UserCompanyRelation = request.user
        user = relation.user
        company = relation.company

        if not relation.product_interaction_permission:
            return Response(**NOT_HAVE_PERMISSIONS)

        # print("FILES:")
        # print(request.FILES)
        # links = []
        link = ""
        limit = 1024 * 1024 * 5
        for filename in request.FILES.keys():
            file = request.FILES[filename]
            print("Name:", file.name, "type:", file.content_type, "size:", file.size)
            # print("Read", file.read())

            #image = ProductImage.objects.create(link="-")
            photo = Photo.objects.create(name=file.name,
                                         user=user)
            #link = add_file_to_storage(file, image.id, is_image=False)
            links = add_file_to_storage(file, photo.id, is_image=True)
            # print("New link:", link)
            photo.links = links
            photo.save(update_fields=["links"])
            break

        return Response({"urls": links})


# TEST
class DeleteImageView(APIView):

    def get(self, request):
        key = request.GET.get('key', None)
        key = "b914564477170cdad33118d0582d9dd6c74d97b01eae257e44aa9d5bade97baf/video_info.txt"
        delete_file_from_storage(key)
        return Response(200)
    

    
    
    
class CreateTableExcelView(AppCompanyAPIView):
    

    def post(self, request):
        
        relation: UserCompanyRelation = request.user
        #request.data._mutable = True
        data = request.data
        serializer = FilterParamsSerializer(data)
        data = serializer.create(validated_data=serializer.data, 
                                 relation=relation)
        
        task = Task.objects.create(task_type=CREATE_EXCEL_TABLE_FROM_PRODUCTS,
                                   data=data)
        return Response(
                        data={"task": task.token,}
                       )