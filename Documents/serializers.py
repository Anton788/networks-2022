from rest_framework import serializers
from .models import *
from .utils import get_max_filed_length


class CreateFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document

        extra_kwargs = {
            'link': {
                "error_messages": {
                    "max_length": f"'Ссылка на файл' превышает {get_max_filed_length('link')} символов",
                    "required": "Укажите ссылку на файл",
                },
            },
            'description': {
                "error_messages": {
                    "max_length": f"'Описание файла' превышает {get_max_filed_length('description')} символов",
                },
            },
            'name': {
                "error_messages": {
                    "max_length": f"'Название файла' превышает {get_max_filed_length('name')} символов",
                },
            },
        }

        fields = ['link', 'description', 'id', 'name', 'user']



class UpdateFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        extra_kwargs = {
            'link': {
                "error_messages": {
                    "max_length": f"'Ссылка на файл' превышает {get_max_filed_length('link')} символов",
                    "required": "Укажите ссылку на файл",
                },
            },
            'description': {
                "error_messages": {
                    "max_length": f"'Описание файла' превышает {get_max_filed_length('description')} символов",
                },
            },
            'name': {
                "error_messages": {
                    "max_length": f"'Название файла' превышает {get_max_filed_length('name')} символов",
                },
            },
        }

        fields = ['link', 'description', 'name']



class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = "__all__"


