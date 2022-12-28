from Organizations.models import Company, Factory
from Users.models import User, UserCompanyRelation, UserFactoryRelation

import Users.constants.user_company_permissions as COMPANY_PERMISSIONS
import Users.constants.factory_permissions as FACTORY_PERMISSIONS
import Users.constants.user_organization_role as USER_ORGANIZATION_ROLE


def get_list_of_subordinate_users(user: User, company: Company):
    users = []
    search_set = set()
    search_set.add(user)
    counter = 0
    while len(search_set) and counter < 10:
        counter += 1
        creator = search_set.pop()
        queryset = UserCompanyRelation.objects.filter(
            creator=creator,
            company=company,
        )
        for relation in queryset:
            search_set.add(relation.user)
            users.append(relation.user)
    return users


def get_list_of_users_in_factory(factory: Factory):
    users = []
    queryset = UserFactoryRelation.objects.filter(factory=factory)
    for relation in queryset:
        users.append(relation.user)
    return users


def get_list_of_subordinate_users_with_creators(user: User, company: Company):
    users = []
    search_set = set()
    search_set.add(user)
    counter = 0
    while len(search_set) and counter < 10:
        counter += 1
        creator = search_set.pop()
        queryset = UserCompanyRelation.objects.filter(
            creator=creator,
            company=company,
        )
        for relation in queryset:
            search_set.add(relation.user)
            users.append({
                "u": relation.user,
                "c": creator,
            })
    return users


def can_user_edit_another_user(editor: User, user: User):
    if not user.organization_account:
        return False
    company = UserCompanyRelation.objects.get(user=user).company
    subordinate_users = get_list_of_subordinate_users(editor, company)

    if user not in subordinate_users:
        return False
    return True


def get_user_factory_permissions(user_company_relation: UserFactoryRelation):
    permissions = []
    if user_company_relation.product_interaction_permission:
        permissions.append(FACTORY_PERMISSIONS.PRODUCT_INTERACTION_PERMISSION)
    if user_company_relation.create_orders_permission:
        permissions.append(FACTORY_PERMISSIONS.CREATE_ORDERS_PERMISSION)
    if user_company_relation.factory_info_permission:
        permissions.append(FACTORY_PERMISSIONS.FACTORY_INFO_PERMISSION)
    if user_company_relation.add_users_permission:
        permissions.append(FACTORY_PERMISSIONS.ADD_USERS_PERMISSION)
    if user_company_relation.proposal_permission:
        permissions.append(FACTORY_PERMISSIONS.PROPOSAL_PERMISSION)
    return permissions


def get_user_company_permissions(user_company_relation: UserCompanyRelation):
    permissions = []
    if user_company_relation.product_interaction_permission:
        permissions.append(COMPANY_PERMISSIONS.PRODUCT_INTERACTION_PERMISSION)
    if user_company_relation.ordering_permission:
        permissions.append(COMPANY_PERMISSIONS.ORDERING_PERMISSION)
    if user_company_relation.company_info_permission:
        permissions.append(COMPANY_PERMISSIONS.COMPANY_INFO_PERMISSION)
    if user_company_relation.factory_permission:
        permissions.append(COMPANY_PERMISSIONS.FACTORY_PERMISSION)
    if user_company_relation.add_users_permission:
        permissions.append(COMPANY_PERMISSIONS.ADD_USERS_PERMISSION)
    if user_company_relation.proposal_permission:
        permissions.append(COMPANY_PERMISSIONS.PROPOSAL_PERMISSION)
    return permissions


def get_russian_company_role(role_number: UserCompanyRelation.role):
    role = ""
    if role_number == USER_ORGANIZATION_ROLE.OWNER:
        role = "Владелец"
    elif role_number == USER_ORGANIZATION_ROLE.STAFF:
        role = "Сотрудник"
    elif role_number == USER_ORGANIZATION_ROLE.MANAGER:
        role = "Менеджер"
    return role
