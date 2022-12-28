from rest_framework.authentication import TokenAuthentication
from Organizations.models import CompanyAuthToken


class CompanyTokenAuthentication(TokenAuthentication):
    model = CompanyAuthToken
