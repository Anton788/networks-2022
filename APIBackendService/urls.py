from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="NeoChainer API",
      default_version='v1',
      description="NeoChainer API documentation",
      contact=openapi.Contact(email="anton.ilin080599@yandex.ru"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

api = [
    path('users/', include('Users.urls')),
    path('products/', include('Products.urls')),
    path('organizations/', include('Organizations.urls')),
    path('notifications/', include('Notifications.urls')),
    path('orders/', include('Orders.urls')),
    path('communications/', include('Communications.urls')),
    path('documents/', include('Documents.urls')),
    # path('content/', include('Content.urls')),
    # path('payments/', include('Payment.urls')),
    # path('statistics/', include('Statistics.urls')),
    # path('games/', include('Games.urls')),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api)),
    # path('dashboard/', include('Dashboard.urls')),
]

admin.site.site_header = 'NeoChainer Administration'
admin.site.site_title = 'NeoChainer Admin'
# admin.site.site_url = '/dashboard'
