import meilisearch
from meilisearch.errors import MeiliSearchApiError
from Products.constants.search_constants import (
    MEILISEARCH_ADDRESS,
    PRODUCT_NAME_INDEX,
    PRODUCTS_INDEX,
)
from Products.models import Product
from Products.serializers import GetProductSearchSerializer
from config import MEILI_MASTER_KEY


def get_meilisearch_client():
    return meilisearch.Client(MEILISEARCH_ADDRESS, MEILI_MASTER_KEY)


def product_name_search(name):
    try:
        client = get_meilisearch_client()

    except:
        return []


def add_documents(documents: list, primary_key='id', index_name=PRODUCT_NAME_INDEX):
    try:
        client = get_meilisearch_client()
        task = client.index(index_name).add_documents(documents, primary_key=primary_key)
    except MeiliSearchApiError as e:
        print("MeiliSearchApiError:", e)


def add_product_names_to_index(product_names: list):
    add_documents(product_names, index_name=PRODUCT_NAME_INDEX)


def add_product_to_product_names_index(product: Product):
    names = [{
        "id": product.id,
        "name": product.name,
    }]
    add_product_names_to_index(names)


def add_product_dicts_to_index(products: list):
    add_documents(products, index_name=PRODUCTS_INDEX)


def add_product_to_products_index(product: Product):
    products = [GetProductSearchSerializer(product).data]
    add_product_dicts_to_index(products)


def add_products_to_products_index(products: list):
    # try:
    product_dicts = [GetProductSearchSerializer(product).data for product in products]
    # except Exception as e:
    #     print("Err:", e)

    # print("GET LIST OF DICTS!", product_dicts[0])
    add_product_dicts_to_index(product_dicts)


def replace_documents(documents, index_name=PRODUCT_NAME_INDEX):
    try:
        client = get_meilisearch_client()
        task = client.index(index_name).add_documents(documents)
    except MeiliSearchApiError as e:
        print("MeiliSearchApiError:", e)


def update_documents(documents, index_name=PRODUCT_NAME_INDEX):
    try:
        client = get_meilisearch_client()
        task = client.index(index_name).update_documents(documents)
    except MeiliSearchApiError as e:
        print("MeiliSearchApiError:", e)


def delete_documents(documents, index_name=PRODUCT_NAME_INDEX):
    """

    :param documents: list of ids !!!!!!!!
    :param index_name:
    :return: None
    """
    try:
        client = get_meilisearch_client()
        task = client.index(index_name).delete_documents(documents)
    except MeiliSearchApiError as e:
        print("MeiliSearchApiError:", e)


def search_index(query, limit=20, offset=0, index_name=PRODUCT_NAME_INDEX):
    try:
        client = get_meilisearch_client()
        search_result = client.index(index_name).search(query, {
            'limit': limit,
            'offset': offset
        })
        return search_result
    except MeiliSearchApiError as e:
        print("MeiliSearchApiError:", e)
    # return search_result  #.hits, search_result.processingTimeMs


def search_index_filter(query, custom_filter, attributes, limit=20, offset=0, index_name=PRODUCTS_INDEX):
    try:
        client = get_meilisearch_client()
        client.index(index_name).update_filterable_attributes(attributes)
        search_result = client.index(index_name).search(query, {
            'limit': limit,
            'offset': offset,
            'filter': custom_filter,
        })
        return search_result
    except MeiliSearchApiError as e:
        print("MeiliSearchApiError:", e)
    # return search_result  #.hits, search_result.processingTimeMs