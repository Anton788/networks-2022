from math import ceil

from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework import status

from APIBackendService.views import AppUsersAPIView
from Notifications.constants import ADMIN_INFO, USER_NOTIFICATION_STATUS
from Notifications.models import SystemNotification, UserNotification
from Notifications.serializers import GetUserSystemNotificationSerializer, GetSystemNotificationSerializer
from Users.models import User


class SystemNotificationUserView(AppUsersAPIView):
    """
    Создание системного уведомления
    """
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        try:
            title = request.data["title"]
            description = request.data["description"]
            text = request.data["text"]
        except:
            return Response(status=status.HTTP_200_OK, data={"detail": "Некорректный запрос. Поля указаны неверно."})
        notification = SystemNotification.objects.create(title=title,
                                          description=description,
                                          text=text)
        # users = User.objects.all()
        # for user in users:
        #     UserNotification.objects.create(user=user, status=0, notification=notification)
        return Response(status=status.HTTP_200_OK)


class ReadSystemNotificationView(AppUsersAPIView):
    """
    Чтение системного уведомления (изменение статуса на прочитано)
    """
    
    def post(self, request):
        try:
            notif_id = request.query_params["id"]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "Некорректный запрос.(не указан идентификатор уведомления)"})
        UserNotification.objects.filter(id=notif_id, user=request.user).update(status=USER_NOTIFICATION_STATUS.READ)
        return Response(status=status.HTTP_200_OK)


class ListNotificationByUserView(AppUsersAPIView):
    """
    Возвращение списка всех уведомление для пользователя.
    Используется пагинация LimitOffsetPagination, поэтому параметры в запросе limit и offset соответственно
    """
    pagination_class = LimitOffsetPagination
    

    def get(self, request):
        pagination = LimitOffsetPagination()
        pagination.max_limit = 10
        result_page = pagination.paginate_queryset(UserNotification.objects.filter(user_id=request.user.id), request=request)
        serializer = GetUserSystemNotificationSerializer(result_page, many=True)
        return pagination.get_paginated_response(serializer.data)


class SystemNotificationFullView(AppUsersAPIView):
    """
    Полное сообщение (раскрытие сообщения при клике на него)
    """
    

    def get(self, request):
        try:
            notif_id = request.query_params["id"]
        except:
            return Response({"Error": "Некорректный запрос. (не указан идентификатор уведомления)"})
        notification = get_object_or_404(UserNotification, id=notif_id)
        if not notification.user.id == request.user.id:
            return Response(data={"detail": "No access rights"}, status=status.HTTP_400_BAD_REQUEST)
        UserNotification.objects.filter(id=notif_id, user=request.user).update(status=USER_NOTIFICATION_STATUS.READ)
        res = GetSystemNotificationSerializer(notification.notification).data
        return Response(res)
