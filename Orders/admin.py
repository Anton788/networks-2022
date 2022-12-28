from django.contrib import admin
from .models import OrderChain, ProductRequest
# Register your models here.


@admin.register(OrderChain)
class OrderChainAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_executor', 'time', 'price', 'status')


@admin.register(ProductRequest)
class ProductRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'request_time', 'product', 'status')
