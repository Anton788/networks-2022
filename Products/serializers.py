from rest_framework import serializers
from rest_framework.authtoken.models import Token
import json

from .models import (
    Product,
    ProductImage,
    ProductFile,
    ProductsProcessingFile,
    ProductRating)

from Products.constants.product_condition import (
    NEW,
    USED,
)


class CreateUpdateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        extra_kwargs = {
            'name': {
                "error_messages": {
                    "max_length": "'Название товара' превышает 150 символов",
                },
            },
            'price': {
                "error_messages": {
                    "min_value": "Цена должна быть положительным числом",
                },
            },
            'description': {
                "error_messages": {
                    "max_length": "'Описание товара' превышает 4000 символов",
                },
            },
        }

        fields = ['name', 'price', 'description',
                  'factory', 'company', 'meta_information', 'condition', 'is_available']

    def to_representation(self, instance):
        serializer = super().to_representation(instance)
        serializer["meta_information"] = json.loads(serializer["meta_information"])
        if instance.company_producer:
            if instance.company_producer.company is not None:
                serializer['region'] = instance.company_producer.company.legal_address.region
                serializer['country'] = instance.company_producer.company.legal_address.country
            else:
                serializer['region'] = ""
                serializer['country'] = ""

        return serializer


class GetProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'meta_information', 'id']

    def to_representation(self, instance):
        serializer = super().to_representation(instance)
        images = ProductImage.objects.filter(product=instance)
        files = ProductFile.objects.filter(product=instance)
        serializer["meta_information"] = json.loads(serializer["meta_information"])
        serializer["images"] = [GetProductImageSerializer(image).data for image in images]
        serializer["files"] = [GetProductFileSerializer(file).data for file in files]
        # if instance.main_image:
        #     serializer["main_image"] = instance.main_image.id

        return serializer


class GetProductSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'meta_information', 'id', 'condition', 'is_available']

    def to_representation(self, instance):
        serializer = super().to_representation(instance)
        images = ProductImage.objects.filter(product=instance)
        files = ProductFile.objects.filter(product=instance)
        serializer["meta_information"] = json.loads(serializer["meta_information"])
        serializer["images"] = [{"description": image.description} for image in images]
        serializer["files"] = [{"description": file.description, "name": file.name} for file in files]
        # if instance.main_image:
        #     serializer["main_image"] = instance.main_image.id
        if instance.company_producer:
            if instance.company_producer.company is not None:
                serializer['region'] = instance.company_producer.company.legal_address.region
                serializer['country'] = instance.company_producer.company.legal_address.country
            else:
                serializer['region'] = ""
                serializer['country'] = ""

        return serializer


class GetProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'meta_information', 'id', 'condition', 'is_available']

    def to_representation(self, instance):
        serializer = super().to_representation(instance)
        images = ProductImage.objects.filter(product=instance)
        files = ProductFile.objects.filter(product=instance)
        serializer["meta_information"] = json.loads(serializer["meta_information"])
        serializer["images"] = [GetProductImageUpdateSerializer(image).data for image in images]
        serializer["files"] = [GetProductFileUpdateSerializer(file).data for file in files]
        if instance.main_image:
            serializer["main_image"] = instance.main_image.id
        if instance.company_producer:
            if instance.company_producer.company is not None:
                serializer['region'] = instance.company_producer.company.legal_address.region
                serializer['country'] = instance.company_producer.company.legal_address.country
            else:
                serializer['region'] = ""
                serializer['country'] = ""
        return serializer


class CreateProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        extra_kwargs = {
            'link': {
                "error_messages": {
                    "max_length": "'Ссылка на изображение' превышает 300 символов",
                    "required": "Укажите ссылку на изображение",
                },
            },
            'description': {
                "error_messages": {
                    "max_length": "'Описание товара' превышает 300 символов",
                },
            },
        }

        fields = ['product', 'link', 'description']


class GetProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['link', 'description', ]


class GetProductImageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"


class GetProductFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFile
        fields = ['link', 'description', 'name']


class GetProductFileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFile
        fields = ['link', 'description', 'name', 'id']


class SetMainImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['main_image']


class GetProductPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price']

    def to_representation(self, instance: Product):
        serializer = super().to_representation(instance)
        if instance.main_image:
            serializer["image"] = instance.main_image.link
        if len(instance.description) > 100:
            serializer['description'] = instance.description[:100] + "..."
        else:
            serializer['description'] = instance.description
        if instance.company_producer:
            if instance.company_producer.company is not None:
                serializer['region'] = instance.company_producer.company.legal_address.region
                serializer['country'] = instance.company_producer.company.legal_address.country
            else:
                serializer['region'] = ""
                serializer['country'] = ""

        return serializer


class CreateProductFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFile
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

        fields = ['product', 'link', 'description', 'id', 'name']


class ChangeImageDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        extra_kwargs = {
            'description': {
                "error_messages": {
                    "max_length": "'Описание изображения' превышает 300 символов",
                },
            },
        }

        fields = ['description']


class ChangeFileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFile
        extra_kwargs = {
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

        fields = ['description', 'name']


class ProductsProcessingFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductsProcessingFile
        fields = ["name", "annotation", "status", "comment", "link", "datetime", 'id']
        read_only = True
        
        
class ProductTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description']
        
    def to_representation(self, instance: Product):
        serializer = super().to_representation(instance)

        serializer["condition"] = "new" if instance.condition == NEW \
            else "used" if instance.condition == USED else instance.condition
        serializer["company"] = instance.company.name if instance.company else '-' 
        serializer["factory"] = instance.factory.name if instance.factory else '-'
        serializer["company_producer"] = instance.company_producer.name if instance.company_producer else '-'
        serializer["factory_producer"] = instance.factory_producer.name if instance.factory_producer else '-'
        
        return serializer


class ProductFilterSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'condition']
        
        
        
class FilterParamsSerializer(serializers.Serializer):
    
    
    product_id_list = serializers.ListField(child=serializers.IntegerField(), default=[])
    price_min = serializers.IntegerField(default=0)
    price_max = serializers.IntegerField(default=10e10)
    factory_id_list = serializers.ListField(child=serializers.IntegerField(), default=[])
    factory_producer = serializers.ListField(child=serializers.IntegerField(), default=[])
    company_producer = serializers.ListField(child=serializers.IntegerField(), default=[])
    #condition = serializers.ListField(child=serializers.IntegerField(), default=[0, 1])
    #user_id = serializers.IntegerField(allow_null=True)
    #company_id = serializers.IntegerField(allow_null=True)
    

    def to_representation(self, instance: dict):
        serializer = super().to_representation(instance)
        if "condition" in instance:
            if type(instance["condition"]) == int:
                serializer["condition"] = [instance["condition"]]
            else:
                serializer["condition"] = instance["condition"]
        else:
            serializer["condition"] = None
        return serializer 
    
    
    def create(self, validated_data, relation):
        validated_data["user_id"] = relation.user_id
        validated_data["company_id"] = relation.company_id
        return validated_data

    
    
class ProductRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRating
        fields = ["product", "description", "last_changed_at", "rating", "company"]
        