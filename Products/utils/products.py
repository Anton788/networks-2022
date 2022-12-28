from django.shortcuts import get_object_or_404

from Products.models import (
    Product,
    ProductImage,
)
from Organizations.models import Company

from Users.models import (
    User,
    UserFactoryRelation,
    UserCompanyRelation,
)


def check_product_create_permission(user, company_id=None, factory_id=None):
    # if factory_id:
    #     factory = get_object_or_404(Factory, id=factory_id)
    #     factory_relation_queryset = UserFactoryRelation.objects.filter(user=user, factory=factory)
    #     if (not factory_relation_queryset.exists()) or \
    #             not factory_relation_queryset.first().product_interaction_permission:
    #         return False

    if company_id:
        company = get_object_or_404(Company, id=company_id)
        company_relation_queryset = UserCompanyRelation.objects.filter(user=user, company=company)
        if (not company_relation_queryset.exists()) or \
                not company_relation_queryset.first().product_interaction_permission:
            return False

    return True


def check_product_edit_permission(user, product):
    # factory = product.factory
    company = product.company

    # if factory:
    #     factory_relation_queryset = UserFactoryRelation.objects.filter(user=user, factory=factory)
    #     if (not factory_relation_queryset.exists()) or \
    #             not factory_relation_queryset.first().product_interaction_permission:
    #         return False

    if company:
        company_relation_queryset = UserCompanyRelation.objects.filter(user=user, company=company)
        if (not company_relation_queryset.exists()) or \
                not company_relation_queryset.first().product_interaction_permission:
            return False

    return True
