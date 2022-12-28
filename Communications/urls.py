from django.urls import path
from Communications import views

urlpatterns = [
    path("create/order/chat/", views.CreateOrderChatView.as_view()),
    path("send/chat/message/", views.SendOrderMessageView.as_view()),
    path("receive/chat/message/", views.ReceiveOrderMessageView.as_view()),
    path("read/order/messages/", views.ReadOrderMessagesView.as_view()),
]
