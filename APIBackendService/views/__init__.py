from rest_framework import exceptions, viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
import datetime

from Notifications.constants import ADMIN_INFO
from Notifications.telegram import alert_admin_tg_message
from APIBackendService.constants import DOMAIN
from Organizations.authentication import CompanyTokenAuthentication
from Organizations.permissions import IsCompanyAuthenticated
from Users.authentication import UserCompanyTokenAuthentication
from Users.permissions import IsUserCompanyAuthenticated


class BaseAppAPIView(APIView):
    """
    Base APIView for app with:
     - alert about exceptions
     - ...
    """
    author = None  # ADMIN_INFO.UNDEFINED

    def get_author_name(self):
        if self.author is None:
            return "неизвестен"
        return f"@{self.author.TG_USERNAME}"

    def handle_exception(self, exc):

        if isinstance(exc, (exceptions.APIException,)):
            return super().handle_exception(exc)

        try:
            try:
                if self.request.method == "GET":
                    params = "(in query)"  # str(self.request.query_params.dict())
                else:
                    params = str(self.request.data)
                if len(params) > 200:
                    params = params[:200] + "..."
            except Exception as e:
                params = f"‼ Ошибка получения параметров запроса: {e}"

            def string_process(s):
                return str(s)  # .replace('_', '\\_')

            user = string_process(self.request.user)
            err = string_process(exc)
            path = string_process(self.request.get_full_path())

            text = f"🆘 Ошибка в выполнении View\n\n" \
                   f"<b>Author</b>: {self.get_author_name()}\n" \
                   f"<b>Method</b>: {self.request.method}\n" \
                   f"<b>Path</b>: {DOMAIN}{path}\n" \
                   f"<b>Data</b>: {string_process(params)}\n" \
                   f"<b>Class</b>: {string_process(self.__class__.__name__)}\n" \
                   f"<b>UTC</b>: {string_process(datetime.datetime.utcnow())}\n" \
                   f"<b>User</b>: {user}\n" \
                   f"<b>Error type</b>: {string_process(exc.__class__.__name__)}\n" \
                   f"<b>Error</b>: {err}"

            # print(text)
            alert_admin_tg_message(text, parse_mode='HTML')
        except:
            pass

        return super().handle_exception(exc)


class BaseAppReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
        Base ReadOnlyModelViewSet for app with:
         - alert about exceptions
         - ...
    """

    author = None

    def get_author_name(self):
        if self.author is None:
            return "неизвестен"
        return f"@{self.author.TG_USERNAME}"

    def handle_exception(self, exc):

        if isinstance(exc, (exceptions.APIException,)):
            return super().handle_exception(exc)

        try:
            try:
                if self.request.method == "GET":
                    params = "(in query)"  # str(self.request.query_params.dict())
                else:
                    params = str(self.request.data)
                if len(params) > 200:
                    params = params[:200] + "..."
            except Exception as e:
                params = f"‼ Ошибка получения параметров запроса: {e}"

            def string_process(s):
                return str(s).replace('_', '\\_')

            try:
                user_str = self.request.user
            except:
                user_str = "<anon>"

            user = string_process(user_str)
            err = string_process(exc)
            path = string_process(self.request.get_full_path())

            text = f"🆘 Ошибка в выполнении ReadOnlyModelViewSet\n\n" \
                   f"*Author*: {self.get_author_name()}\n" \
                   f"*Method*: {self.request.method}\n" \
                   f"*Path*: {DOMAIN}{path}\n" \
                   f"*Data*: {string_process(params)}\n" \
                   f"*Class*: {string_process(self.__class__.__name__)}\n" \
                   f"*UTC*: {datetime.datetime.utcnow()}\n" \
                   f"*User*: {user}\n" \
                   f"*Error type*: {string_process(exc.__class__.__name__)}\n" \
                   f"*Error*: {err}"

            # print(text)
            alert_admin_tg_message(text, parse_mode='HTML')
        except:
            pass

        return super().handle_exception(exc)


class AppUsersAPIView(BaseAppAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class AppCompanyAPIView(BaseAppAPIView):
    authentication_classes = [UserCompanyTokenAuthentication]
    permission_classes = [IsUserCompanyAuthenticated]
