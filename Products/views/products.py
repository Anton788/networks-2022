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
from rest_framework.authentication import TokenAuthentication, BasicAuthentication, SessionAuthentication

from Products.models import (
    Product,
    ProductImage, ProductRating,
    ProductFile, ProductsProcessingFile)
from Organizations.models import Factory, Company, FactoryCompanyRelation, CompanyProducer, FactoryProducer
from Products.utils.files_processing import add_image_to_product, add_file_to_product, add_file_to_processing
from Products.utils.product_producers import create_factory_producer, create_company_producer
from Products.utils.products import check_product_edit_permission, check_product_create_permission
from Products.utils.search import add_product_to_product_names_index, add_product_to_products_index

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
    ProductsProcessingFileSerializer, GetProductImageUpdateSerializer,
    ProductRatingSerializer)

import Products.constants.products_file_check_status as PRODUCTS_FILE_CHECK_STATUS
import datetime

from django.utils.crypto import get_random_string
from Services.models import Task

from django.core.paginator import Paginator

from Notifications.constants import ADMIN_INFO
from APIBackendService.views import AppCompanyAPIView, AppUsersAPIView

from Products.paginators import ProductPagination


from Documents.utils import add_file
from Documents.serializers import CreateFileSerializer, UpdateFileSerializer

from rest_framework.pagination import LimitOffsetPagination

from Documents.serializers import PhotoSerializer

NOT_HAVE_PERMISSIONS = {
    "data": {"detail": "Нет прав"},
    "status": status.HTTP_400_BAD_REQUEST,
}


class CreateProductView(AppCompanyAPIView):
    """
    Создание продукта
    """
    

    def post(self, request):
        relation: UserCompanyRelation = request.user
        user = relation.user

        factory_id = request.data.get("factory", None)
        company_id = relation.company_id
        # has_access = check_product_create_permission(user, company_id=company_id, factory_id=factory_id)
        if not relation.product_interaction_permission:
            return Response(**NOT_HAVE_PERMISSIONS)

        if company_id is None and factory_id is None:
            # TODO: remove this
            return Response(
                data={
                    "detail": "Продукт должен быть привязан к заводу или к компании",
                    "company": "Нужно выбрать завод или компанию",
                    "factory": "Нужно выбрать завод или компанию",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        data = dict(request.data)
        data["company"] = company_id
        serializer = CreateUpdateProductSerializer(data=data, partial=False)
        serializer.is_valid(raise_exception=True)

        product = serializer.save()
        add_product_to_product_names_index(product)
        add_product_to_products_index(product)
        return Response({"id": product.id})


class DeleteProductView(AppCompanyAPIView):
    

    def get(self, request):
        relation: UserCompanyRelation = request.user
        product_id = request.GET.get('id', None)

        product = Product.objects.get(id=product_id)
        if not relation.product_interaction_permission:
            return Response(**NOT_HAVE_PERMISSIONS)

        # IMAGES AND FILES WILL BE DELETED BY CRON JOB
        # images = ProductImage.objects.filter(product=product)
        # for image in images:
        #     pass  # ANYA: IN THE FUTURE THESE IMAGES SHOULD BE DELETED FROM THE SERVER

        product.delete()
        return Response({"detail": "успешно удалено!"})


class UpdateProductView(AppCompanyAPIView):
    

    def post(self, request):
        relation: UserCompanyRelation = request.user
        product_id = request.data.get('id', None)
        product = Product.objects.get(id=product_id)
        user = relation.user

        # has_edit_access = check_product_edit_permission(user, product)
        if not relation.product_interaction_permission:
            return Response(**NOT_HAVE_PERMISSIONS)

        data = request.data
        serializer = CreateUpdateProductSerializer(product, data=data, partial=True)
        serializer.is_valid(raise_exception=True)

        product = serializer.save()
        add_product_to_product_names_index(product)
        add_product_to_products_index(product)
        return Response(serializer.data)


class ReadProductView(AppUsersAPIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        product = get_object_or_404(Product, id=request.GET.get('id'))
        return Response(GetProductSerializer(product).data)


class GetProductPreviewView(AppUsersAPIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        product = get_object_or_404(Product, id=request.GET.get('id'))
        return Response(GetProductPreviewSerializer(product).data)


class ReadProductUpdateView(AppCompanyAPIView):
    

    def get(self, request):
        relation: UserCompanyRelation = request.user
        product = get_object_or_404(Product, id=request.GET.get('id'))
        # has_edit_access = check_product_edit_permission(request.user, product)
        if not relation.product_interaction_permission:
            return Response(**NOT_HAVE_PERMISSIONS)

        return Response(GetProductUpdateSerializer(product).data)


class DeleteImageView(AppCompanyAPIView):
    

    def post(self, request):
        relation: UserCompanyRelation = request.user
        image_id = int(request.data.get('id', None))
        user = relation.user

        image = get_object_or_404(ProductImage, id=image_id)
        product = image.product

        # has_edit_access = check_product_edit_permission(user, product)
        if not relation.product_interaction_permission:
            return Response(**NOT_HAVE_PERMISSIONS)

        # ANYA: IN THE FUTURE THE IMAGE WILL ALSO BE DELETED FROM THE SERVER
        new_id = None

        if product.main_image == image:
            images = ProductImage.objects.filter(product=product).exclude(id=image_id)
            if images.exists():
                product.main_image = images.first()
                product.save()
                new_id = product.main_image.id

        image.product = None
        image.save()
        return Response({"main_image": new_id})


class AddImageView(AppCompanyAPIView):
    

    def post(self, request):
        # return Response({'id': request.query_params['product_id']})
        relation: UserCompanyRelation = request.user
        user = relation.user

        product_id = request.data.get('product')  # request.data.get('product')
        product = get_object_or_404(Product, id=product_id)
        # has_edit_access = check_product_edit_permission(user, product)
        if not relation.product_interaction_permission:
            return Response(**NOT_HAVE_PERMISSIONS)

        if ProductImage.objects.filter(product=product).count() >= 10:
            return Response(
                data={"detail": "Максимальное число изображений для продукта: 10"},
                status=status.HTTP_400_BAD_REQUEST
            )

        #description = request.data.get('description', "")

        for filename in request.FILES.keys():
            try:
                image = add_image_to_product(request.FILES[filename], product=product, user=user)
                is_main = False
                if not product.main_image:
                    product.main_image = image
                    is_main = True
                    product.save()
                return Response({
                    "main": is_main,
                    **GetProductImageUpdateSerializer(image).data
                })

            except ValueError as v:
                return Response(
                    data={"detail": str(v)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            data={"detail": "Нет картинки"},
            status=status.HTTP_400_BAD_REQUEST
        )


class SetMainImageView(AppCompanyAPIView):
    

    def post(self, request):
        relation: UserCompanyRelation = request.user
        product_id = request.data.get('product_id')
        user = relation.user

        product = Product.objects.get(id=product_id)
        # has_edit_access = check_product_edit_permission(user, product)
        if not relation.product_interaction_permission:
            return Response(**NOT_HAVE_PERMISSIONS)

        image_id = request.data.get("image_id")
        image = get_object_or_404(ProductImage, id=image_id)

        if image.product != product:
            return Response(
                data={"detail": "Выбранное изображение не соответствует продукту"},
                status=status.HTTP_400_BAD_REQUEST
            )

        product.main_image = image
        product.save()

        return Response(
            data={"main_image": product.main_image.id}
        )


class GetFactoryProductsView(AppCompanyAPIView):
    

    def get(self, request):
        relation: UserCompanyRelation = request.user
        factory = get_object_or_404(Factory, id=int(request.GET.get('id', None)))
        products = Product.objects.filter(factory=factory)

        user_relations = UserFactoryRelation.objects.filter(user=relation.user, factory=factory)
        has_access = user_relations.exists()
        if not has_access:
            return Response(**NOT_HAVE_PERMISSIONS)

        can_edit = user_relations.first().product_interaction_permission

        product_list = []
        for product in products:
            product_list.append(GetProductPreviewSerializer(product).data)

        return Response({
            "list": product_list,
            "edit": can_edit,
        })


class GetCompanyProductsView(AppCompanyAPIView):
    

    def get(self, request):
        relation: UserCompanyRelation = request.user
        company = relation.company
        products = Product.objects.filter(company=company)

        # user_relations = UserCompanyRelation.objects.filter(user=user, company=company)
        # has_access = user_relations.exists()
        # if not has_access:
        #     return Response(**NOT_HAVE_PERMISSIONS)

        can_edit = relation.product_interaction_permission

        product_list = []
        for product in products:
            product_list.append(GetProductPreviewSerializer(product).data)

        return Response({
            "list": product_list,
            "edit": can_edit,
        })


class GetCompanyFactoryProductsView(AppCompanyAPIView):
    

    def get(self, request):
        relation: UserCompanyRelation = request.user
        company = relation.company

        can_edit = relation.product_interaction_permission

        product_list = []

        products = Product.objects.filter(company=company)
        for product in products:
            product_list.append(GetProductPreviewSerializer(product).data)

        relations = FactoryCompanyRelation.objects.filter(company=company)
        for relat in relations:
            factory = relat.factory
            products = Product.objects.filter(factory=factory)
            for product in products:
                product_list.append(GetProductPreviewSerializer(product).data)

        return Response({
            "list": product_list,
            "edit": can_edit,
        })


class AddFileView(AppCompanyAPIView):
    

    def post(self, request):
        relation: UserCompanyRelation = request.user
        user = relation.user

        product_id = request.data.get('product')
        product = get_object_or_404(Product, id=product_id)
        # has_edit_access = check_product_edit_permission(user, product)
        if not relation.product_interaction_permission:
            return Response(**NOT_HAVE_PERMISSIONS)

        if ProductFile.objects.filter(product=product).count() >= 5:
            return Response(
                data={"detail": "Максимальное число файлов для продукта: 5"},
                status=status.HTTP_400_BAD_REQUEST
            )

        description = request.data.get('description', "")
        name = request.data.get('name', None)

        for filename in request.FILES.keys():
            try:
                document = add_file(request.FILES[filename], user=user,
                                    description=description, name=name)
                ProductFile.objects.create(document=document,
                                           product=product)
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


class DeleteFileView(AppCompanyAPIView):

    def post(self, request):
        relation: UserCompanyRelation = request.user
        file_id = int(request.data.get('id', None))

        file = get_object_or_404(ProductFile, id=file_id)
        product = file.product

        # has_edit_access = check_product_edit_permission(user, product)
        if not relation.product_interaction_permission:
            return Response(**NOT_HAVE_PERMISSIONS)

        file.product = None
        file.save()
        return Response({"product": product.id})


class ChangeImageDescriptionView(AppCompanyAPIView):
    

    def post(self, request):
        relation: UserCompanyRelation = request.user
        user = relation.user
        # user = User.objects.get(username="anya")
        image_id = request.data.get('image')
        image = get_object_or_404(ProductImage, id=image_id)
        # product = image.product

        # has_edit_access = check_product_edit_permission(user, product)
        if not relation.product_interaction_permission:
            return Response(**NOT_HAVE_PERMISSIONS)

        data = request.data
        serializer = ChangeImageDescriptionSerializer(image, data=data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"id": image.id})


class ChangeFileInfoView(AppCompanyAPIView):
    

    def post(self, request):
        relation: UserCompanyRelation = request.user
        file_id = request.data.get('file')

        file = get_object_or_404(ProductFile, id=file_id)
        product = file.product
        document = file.document

        # has_edit_access = check_product_edit_permission(user, product)
        if not relation.product_interaction_permission:
            return Response(**NOT_HAVE_PERMISSIONS)

        data = request.data
        serializer = UpdateFileSerializer(document, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        new_info = UpdateFileSerializer(document).data

        return Response({"file_data": new_info})


class AddProductsFileForProcessingView(AppCompanyAPIView):
    

    def post(self, request):
        relation: UserCompanyRelation = request.user
        user = relation.user

        factory_id = request.data.get("factory", None)
        # company_id = request.data.get("company", None)
        company_id = relation.company_id
        # has_access = check_product_create_permission(user, company_id=company_id, factory_id=factory_id)
        if not relation.product_interaction_permission:
            return Response(**NOT_HAVE_PERMISSIONS)

        if company_id is None and factory_id is None:
            # TODO: deprecated?
            return Response(
                data={
                    "detail": "Продукт должен быть привязан к заводу или к компании",
                    "company": "Нужно выбрать завод или компанию",
                    "factory": "Нужно выбрать завод или компанию",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        data_params = dict()
        if company_id:
            company = get_object_or_404(Company, id=company_id)
            data_params["company"] = company

            if ProductsProcessingFile.objects.filter(
                    company=company,
                    status=PRODUCTS_FILE_CHECK_STATUS.IN_PROGRESS,
            ).count() >= 5:
                return Response(
                    data={"detail": "Максимальное число файлов в обработке: 5"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if factory_id:
            factory = get_object_or_404(Factory, id=factory_id)
            data_params["factory"] = factory

            if ProductsProcessingFile.objects.filter(
                    factory=factory,
                    status=PRODUCTS_FILE_CHECK_STATUS.IN_PROGRESS,
            ).count() >= 5:
                return Response(
                    data={"detail": "Максимальное число файлов в обработке: 5"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        annotation = request.data.get('annotation', "")

        for filename in request.FILES.keys():
            try:
                name = request.data.get('name', request.FILES[filename].name)
                file = add_file_to_processing(
                    request.FILES[filename],
                    user,
                    name=name,
                    annotation=annotation,
                    **data_params,
                )

                return Response(ProductsProcessingFileSerializer(file).data)

                # return Response({
                #     "name": file.name,
                #     "link": file.link,
                # })

            except ValueError as v:
                return Response(
                    data={"detail": str(v)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            data={"detail": "Нет файла"},
            status=status.HTTP_400_BAD_REQUEST
        )


class ShowProductsFileForProcessingView(AppCompanyAPIView):
    

    def get(self, request):
        relation: UserCompanyRelation = request.user
        company_id = relation.company_id
        factory_id = int(request.GET.get("factory", None))
        # has_access = check_product_create_permission(user, company_id=company_id, factory_id=factory_id)
        if not relation.product_interaction_permission:
            return Response(**NOT_HAVE_PERMISSIONS)

        if company_id is None and factory_id is None:
            # TODO: deprecated or NOT?
            return Response(
                data={
                    "detail": "Продукт должен быть привязан к заводу или к компании",
                    "company": "Нужно выбрать завод или компанию",
                    "factory": "Нужно выбрать завод или компанию",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if company_id:
            company = get_object_or_404(Company, id=company_id)
            queryset = ProductsProcessingFile.objects.filter(company=company)

            return Response({"list": [ProductsProcessingFileSerializer(p).data for p in queryset]})

        if factory_id:
            factory = get_object_or_404(Factory, id=factory_id)
            queryset = ProductsProcessingFile.objects.filter(factory=factory)

            return Response({"list": [ProductsProcessingFileSerializer(p).data for p in queryset]})

        return Response(
            data={"detail": "Нет информации"},
            status=status.HTTP_400_BAD_REQUEST
        )


class CreateUpdateProductRatingView(AppCompanyAPIView):
    

    def post(self, request):

        relation: UserCompanyRelation = request.user
        user = relation.user
        company = relation.company

        rating = request.data.get("rating")

        print("RATING: ", rating)

        if rating > 5 or rating < 1:
            return Response(
                data={"detail": "Недопустимое значение"},
                status=status.HTTP_400_BAD_REQUEST
            )

        product_id = request.data.get("product")
        product = get_object_or_404(Product, id=product_id)
        description = request.data.get("description", None)
        product_rating, _ = ProductRating.objects.get_or_create(company=company,
                                                                product=product)

        product_rating.rating = rating

        if description is not None:
            product_rating.description = description

        product_rating.save()
        return Response({"id": product_rating.id})


class DeleteProductRatingView(AppCompanyAPIView):
    

    def post(self, request):

        relation: UserCompanyRelation = request.user
        user = relation.user
        company = relation.company

        product_id = request.data.get("product")
        product = get_object_or_404(Product, id=product_id)
        product_rating = get_object_or_404(ProductRating,
                                           company=company,
                                           product=product)
        product_rating.delete()
        return Response({"detail": "Ok"})


class GetProductRatingListView(AppCompanyAPIView):
    

    def get(self, request):
        product_id = request.GET["product"]
        product = get_object_or_404(Product, id=product_id)
        ratings = ProductRating.objects.filter(product=product)

        pagination = LimitOffsetPagination()
        pagination.max_limit = 20
        result_page = pagination.paginate_queryset(ratings, request=request)
        serializer = ProductRatingSerializer(result_page, many=True)

        return pagination.get_paginated_response(serializer.data)


class MyProductRatingView(AppCompanyAPIView):
    

    def get(self, request):

        relation: UserCompanyRelation = request.user
        user = relation.user
        company = relation.company

        product_id = request.GET["product"]
        product = get_object_or_404(Product, id=product_id)
        rating = ProductRating.objects.filter(company=company, product=product).first()
        if rating:
            data = ProductRatingSerializer(rating).data
        else:
            data = None

        return Response({"rating": data})


# class GetProductCompanyProducerView(AppCompanyAPIView):
#     
#
#     def post(self, request):
#         relation: UserCompanyRelation = request.user

class SetProductCompanyProducersView(AppCompanyAPIView):
    """
    Настройка компании производителя для товара
    """
    

    def post(self, request):
        company_id = request.data.get("company", None)
        product_id = request.data.get("product", None)

        company = CompanyProducer.objects.get(id=company_id)
        Product.objects.filter(id=product_id).update(company_producer=company)
        return Response(status=status.HTTP_200_OK)


class CreateProductCompanyProducersView(AppCompanyAPIView):
    """
        Создание компании производителя для товара
    """
    

    def post(self, request):
        company_text = request.data.get("company_text", None).strip()
        inn = request.data.get("inn", None).strip()
        return create_company_producer(inn, company_text)


class SetProductFactoryProducersView(AppCompanyAPIView):
    """
        Настройка завода производителя для товара
    """
    

    def post(self, request):
        relation: UserCompanyRelation = request.user
        factory_id = request.data.get("factory", None)
        factory_text = request.data.get("factory_text", None)

        if factory_id is not None:
            factory = get_object_or_404(Factory, id=factory_id)
            FactoryProducer.objects.create(name=factory.name, factory=factory)
            return Response(status=status.HTTP_200_OK)

        if factory_text is not None:
            FactoryProducer.objects.create(name=factory_text)
            return Response(status=status.HTTP_200_OK)


class CreateProductFactoryProducersView(AppCompanyAPIView):
    """
        Создание компании производителя для товара
    """
    

    def post(self, request):
        company_id = request.data.get("company_producer", None)
        name = request.data.get("name", None).strip()
        return create_factory_producer(company_id, name)


class UpdateAvailableProductView(AppCompanyAPIView):
    """
        Обновление статуса доступности
    """

    

    def post(self, request):
        product_id = request.data.get("product_id", None)
        available = request.data.get("is_available", None)

        Product.objects.filter(id=product_id).update(is_available=available)

        return Response(200)
