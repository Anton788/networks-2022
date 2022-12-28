from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from django.utils import timezone
from Users.models import UserCompanyRelationAuthToken
from django.utils.translation import gettext_lazy as _


class UserCompanyTokenAuthentication(TokenAuthentication):
    model = UserCompanyRelationAuthToken

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token: UserCompanyRelationAuthToken = model.objects.select_related('user', 'user__user', 'user__company').\
                get(key=key)
            if token.expired and token.expired < timezone.datetime.now(tz=timezone.utc):
                token.delete()
                raise model.DoesNotExist
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.user.is_active or not token.user.company.is_active:
            raise exceptions.AuthenticationFailed(_('User or company inactive or deleted.'))

        return token.user, token
