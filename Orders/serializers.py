from rest_framework import serializers
from rest_framework.authtoken.models import Token
import json

import Orders.constants.order_chain_status as ORDER_CHAIN_STATUS


from Orders.models import ProductRequest, OrderChain, ProductRequestFile, ProductRequestImage
from Products.serializers import GetProductPreviewSerializer
from Users.models import UserFactoryRelation, UserCompanyRelation
from Users.serializers import UserContactsSerializer


class UpdateAllProductRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRequest
        fields = ["amount", "description", "preferable_time", "preferable_price"]


class CreateUpdateProductRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRequest
        fields = ['customer', 'user', 'product', 'request', 'amount', 'status',
                  'delivery_type']


class CreateProductRequestFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRequestFile
        fields = '__all__'


class CreateProductRequestImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRequestImage
        fields = '__all__'


class GetProdRequestSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderChain
        fields = ['product_request', 'status']

    def to_representation(self, instance: OrderChain):
        serializer = super().to_representation(instance)
        if instance.product_request:
            description = instance.product_request.description
            if len(description) > 100:
                serializer['description'] = description[:100] + "..."
            else:
                serializer['description'] = description
            product = instance.product_request.product
            if product is not None:
                serializer["product"] = GetProductPreviewSerializer(product).data
        return serializer


class GetOrderChainPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderChain
        fields = ['id', 'product_request', 'status', 'time']

    def to_representation(self, instance: OrderChain):
        serializer = super().to_representation(instance)
        if instance.product_request:
            serializer['product_request_id'] = instance.product_request.id
            serializer['customer'] = {"id": instance.product_request.customer.id,
                                      "name": instance.product_request.customer.name}
            serializer['amount'] = instance.product_request.amount
            description = instance.product_request.description
            if description is not None and len(description) > 100:
                serializer['description'] = description[:100] + "..."
            else:
                serializer['description'] = description
            product = instance.product_request.product
            if product is not None:
                serializer["product"] = GetProductPreviewSerializer(product).data
        return serializer


class AllParamsOrderChain(serializers.ModelSerializer):
    class Meta:
        model = OrderChain
        fields = '__all__'

    def to_representation(self, instance: OrderChain):
        serializer = super().to_representation(instance)
        if instance.product_request:
            serializer['product_request_id'] = instance.product_request.id
            serializer['customer'] = {"id": instance.product_request.customer.id,
                                      "name": instance.product_request.customer.name}
            serializer['amount'] = instance.product_request.amount
            description = instance.product_request.description
            if description is not None and len(description) > 100:
                serializer['description'] = description[:100] + "..."
            else:
                serializer['description'] = description
            product = instance.product_request.product
            if product is not None:
                serializer["product"] = product.id
        return serializer


class GetRequestProductPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRequest
        fields = '__all__'

    def to_representation(self, instance: ProductRequest):
        serializer = super().to_representation(instance)
        # if instance.customer:
        #     serializer["customer"] = instance.customer.name
        if instance.description is not None and len(instance.description) > 100:
            serializer['description'] = instance.description[:100] + "..."
        else:
            serializer['description'] = instance.description
        if instance.product is not None:
            serializer["product"] = GetProductPreviewSerializer(instance.product).data
            chain = OrderChain.objects.get(product_request=instance)
            serializer["status"] = chain.status
            if chain.status == ORDER_CHAIN_STATUS.CONFIRMED:
                if chain.factory_executor:
                    users = UserFactoryRelation.objects.filter(factory=chain.factory_executor, proposal_permission=True)
                    serializer["contacts"] = [{
                        'name': chain.factory_executor.name,
                        'users': list(map(lambda x: UserContactsSerializer(x.user).data, list(users))),
                        'email': chain.factory_executor.email,
                    }]
                else:
                    users = UserCompanyRelation.objects.filter(company=chain.company_executor, proposal_permission=True)
                    serializer["contacts"] = [{
                        'name': chain.company_executor.name,
                        'users': list(map(lambda x: UserContactsSerializer(x.user).data, list(users))),
                        'email': chain.company_executor.email,
                    }]

        return serializer
    
    
    
class GetMoreInfoByCreatedProductRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRequest
        fields = '__all__'
        
    def to_representation(self, instance: ProductRequest):
        serializer = super().to_representation(instance)
        
        if instance.customer is not None:
            serializer["customer"] = dict({"id": instance.customer.id,
                                           "name": instance.customer.name})
            
        serializer["user"] = dict({"id": instance.user.id,
                                   "username": instance.user.username})

        
        chains = OrderChain.objects.filter(product_request=instance)
        confirmed_chains = []
        for chain in chains:
            if chain.status == ORDER_CHAIN_STATUS.CONFIRMED:
                confirmed_chains.append(chain)
        serializer["chains"] = []
        for chain in confirmed_chains:
            serializer["chains"].append(AllParamsOrderChain(chain).data)
        if instance.product is not None:
            serializer["product"] = instance.product.id

        return serializer
    
    
class GetRequestInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRequest
        fields = ["id", "customer", "user", "request_time",
                  "request", "amount", "description", 
                  "preferable_time", "preferable_price",
                  "delivery_type", "address"]
        
    def to_representation(self, instance: ProductRequest):
        
        serializer = super().to_representation(instance)
        
        serializer["customer"] = dict({"id": instance.customer.id,
                                       "name": instance.customer.name})
            
        serializer["user"] = dict({"id": instance.user.id,
                                   "username": instance.user.username})

        return serializer
