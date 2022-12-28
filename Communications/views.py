from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication, BasicAuthentication, SessionAuthentication

from Organizations.models import Company, FactoryCompanyRelation

from APIBackendService.views import AppCompanyAPIView
from Notifications.constants import ADMIN_INFO

from Communications.models import OrderChat, ChatMessage
from Orders.models import OrderChain

import Communications.constants.message_status as MESSAGE_STATUS
import Communications.constants.message_type as MESSAGE_TYPE

from Communications.serializers import ReceivedChatMessageSerializer, ChatMessageSerializer

from rest_framework.pagination import LimitOffsetPagination

from Users.models import (
    User,
    UserFactoryRelation,
    UserCompanyRelation,
)

NOT_HAVE_PERMISSIONS = {
    "data": {"detail": "Нет прав"},
    "status": status.HTTP_400_BAD_REQUEST,
}

    
    
    
    
    
class CreateOrderChatView(AppCompanyAPIView):
    

    def post(self, request):
        relation: UserCompanyRelation = request.user
        user = relation.user
        company = relation.company
        
        chain_id = request.data.get('chain')
        chain = get_object_or_404(OrderChain, id=chain_id)
        company_1 = chain.product_request.customer
        company_2 = chain.company_executor
        
        if company != company_1 and company != company_2:
            return Response(
                data={"detail": "Нет прав на создание данного чата"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        
        chat, created = OrderChat.objects.get_or_create(chain=chain)
        print(created)
        if created:
            text = "Данный чат создан для обсуждения такого-то заказа (ссылка?)"
            greeting_message = ChatMessage.objects.create(chat=chat,
                                                          message_type=MESSAGE_TYPE.MESSAGE,
                                                          text=text)
            chat.companies.set( [company_1, company_2])
            chat.save()
            greeting_message.status = MESSAGE_STATUS.SENT
            greeting_message.save(update_fields=['status'])
        return Response({"chat": chat.id})
    



class SendOrderMessageView(AppCompanyAPIView):
    

    def post(self, request):
        relation: UserCompanyRelation = request.user
        user = relation.user
        company = relation.company
        
        chat_id = request.data.get('chat')
        chat = get_object_or_404(OrderChat, id=chat_id)
        
                
        if company not in chat.companies.all():
            return Response(
                data={"detail": "Нет прав на отправку сообщений в данном чате"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        
        text = request.data.get('text')
        message = ChatMessage.objects.create(text=text,
                                             chat=chat,
                                             sender=company,
                                             status=MESSAGE_STATUS.SENT,
                                             message_type=MESSAGE_TYPE.MESSAGE)
        
        return Response({"message": message.id})

    
    
    
class ReceiveOrderMessageView(AppCompanyAPIView):
    

    def post(self, request):
        relation: UserCompanyRelation = request.user
        user = relation.user
        company = relation.company
        
        chat_id = request.data.get('chat')
        chat = get_object_or_404(OrderChat, id=chat_id)
        
        messages = ChatMessage.objects.filter(chat=chat,
                                              status=MESSAGE_STATUS.SENT).order_by('sent_at')[:10]
        
        for message in messages:
            message.status = MESSAGE_STATUS.RECEIVED
            message.save(update_fields=['status'])
            
        serializer = ReceivedChatMessageSerializer(messages, many=True)
        data = serializer.data
        
        return Response({"messages": data})


class ReadOrderMessagesView(AppCompanyAPIView):
    

    def get(self, request):
        relation: UserCompanyRelation = request.user
        user = relation.user
        company = relation.company

        chat_id = request.data.get('chat')
        chat = get_object_or_404(OrderChat, id=chat_id)

        if company not in chat.companies.all():
            return Response(
                data={"detail": "Нет прав на чтение сообщений в данном чате"},
                status=status.HTTP_400_BAD_REQUEST
            )

        pagination = LimitOffsetPagination()
        pagination.max_limit = 20
        result_page = pagination.paginate_queryset(ChatMessage.objects.filter(chat=chat), request=request)
        serializer = ChatMessageSerializer(result_page, many=True)

        return pagination.get_paginated_response(serializer.data)