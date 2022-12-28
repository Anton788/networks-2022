from django.contrib.auth.models import UserManager
from django.utils import timezone

from rest_framework import serializers
from .models import Company, Factory, Address, Okved, OrganizationsRelationshipFile, CompanyFile


class CompanyMainInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"
        #fields = ['name', 'address', 'company_type', 'inn', 'postal_code', 'website']
        # exclude = ('rating',)
        # read_only = True



class FactoryMainInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factory
        fields = ['name', 'address', 'website', 'postal_code', 'description', 'email']
        #exclude = ('company',)



class FactoryPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factory
        fields = ['name', 'address', 'id']
        
        
        
class CompanyRequisitesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['name', 'leaders', 'phone', 'address', 
                  'postal_code', 'email', 'inn', 'kpp', 'ogrn',
                  'okpo', 'okved', 'checking_account', 'correspondent_account', 'bik']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
    
    
class OkvedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Okved
        fields = ['name', 'code', 'id']
        

class CreateRelationFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationsRelationshipFile
        extra_kwargs = {
            'link': {
                "error_messages": {
                    "max_length": "'Ссылка на файл' превышает 300 символов",
                    "required": "Укажите ссылку на файл",
                },
            },
            'description': {
                "error_messages": {
                    "max_length": "'Описание файла' превышает 300 символов",
                },
            },
            'name': {
                "error_messages": {
                    "max_length": "'Название файла' превышает 50 символов",
                },
            },
        }

        fields = ['relation', 'link', 'description', 'id', 'name']



'''class CreateCompanyFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyFile
        extra_kwargs = {
            'link': {
                "error_messages": {
                    "max_length": "'Ссылка на файл' превышает 300 символов",
                    "required": "Укажите ссылку на файл",
                },
            },
            'description': {
                "error_messages": {
                    "max_length": "'Описание файла' превышает 300 символов",
                },
            },
            'name': {
                "error_messages": {
                    "max_length": "'Название файла' превышает 50 символов",
                },
            },
        }

        fields = ['company', 'link', 'description', 'id', 'name']'''
    


