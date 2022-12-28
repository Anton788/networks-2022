from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token

import json
import requests
import meilisearch

from APIBackendService.views import AppCompanyAPIView
from Products.models import Product
from Products.serializers import GetProductPreviewSerializer, ProductTableSerializer, ProductFilterSearchSerializer
from Products.utils.search import search_index, add_product_names_to_index, add_products_to_products_index, \
    search_index_filter
from Users.models import User

from Products.constants.search_constants import (
    MEILISEARCH_ADDRESS,
    PRODUCT_NAME_INDEX,
    PRODUCTS_INDEX,
)

from django.utils.crypto import get_random_string


class SearchProductNameView(AppCompanyAPIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):

        q = request.GET.get("q", "")
        search_result = search_index(q, limit=10, index_name=PRODUCT_NAME_INDEX)
        # print(search_result)
        return Response(list(map(lambda x: x['name'], search_result['hits'])))


class SearchProductsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        price_left = request.GET.get("price_left", None)
        price_right = request.GET.get("price_right", None)
        condition = request.GET.get("condition", None)
        region = request.GET.get("region", None)
        country = request.GET.get("country", None)
        limit = request.GET.get("limit", 2)
        q = request.GET.get("q", "")

        custom_filter = []
        attributes = set()
        attributes.add("is_available")
        custom_filter.append("is_available = 1")
        if price_left is not None:
            attributes.add("price")
            custom_filter.append(f"price >= {price_left}")
        if price_right is not None:
            attributes.add("price")
            custom_filter.append(f"price <= {price_right}")
        if condition is not None:
            attributes.add("condition")
            conditions = condition.split(',')
            arr_props = []
            for cond in conditions:
                arr_props.append(f"condition = {cond}")
            custom_filter.append(arr_props)
        if region is not None:
            attributes.add("region")
            custom_filter.append(f"region = {region}")
        if country is not None:
            attributes.add("country")
            custom_filter.append(f"country = {region}")
        list_attributes = list(attributes)
        offset = int(request.GET.get("offset", 0))
        search_result = search_index_filter(q, limit=int(limit), offset=offset, index_name=PRODUCTS_INDEX, attributes=list_attributes, custom_filter=custom_filter)
        # print(search_result)
        ids = list(map(lambda x: x['id'], search_result['hits']))
        products = []
        for product_id in ids:
            products.append(GetProductPreviewSerializer(Product.objects.get(id=product_id)).data)
        total = search_result["nbHits"]
        left = total - len(products) - offset
        return Response({
            "total": total,
            "left": left,
            "products": products,
        })


class CustomSearchProductView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        produts = []
        product_tuple = ProductFilterSearchSerializer(request.query_params)
        for prod in Product.objects.filter(**product_tuple.data):
            produts.append(prod.id)

        return Response({"res": produts})

