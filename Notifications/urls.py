from django.urls import path
from Notifications import views


urlpatterns = [
    path("telegram/receive/", views.ReceiveTelegramNotificationsView.as_view()),
    path("telegram/admin/receive/", views.ReceiveTelegramAdminNotificationsView.as_view()),
    #path("telegram/user/receive/", views.ReceiveTelegramUserNotificationsView.as_view()),
    #path("email/send/new/user/", views.SendEmailAboutNewUserView.as_view()),
    path("telegram/send/request/", views.SendRequestForChainView.as_view()),
    path("telegram/accept/chain/", views.AcceptChainView.as_view()),
    path("telegram/reject/chain/", views.RejectChainView.as_view()),
    path('system/notifications/user/create/', views.SystemNotificationUserView.as_view()),
    path('system/notifications/user/read/', views.ReadSystemNotificationView.as_view()),
    path('system/notifications/user/list/', views.ListNotificationByUserView.as_view()),
    path('system/notifications/user/full/', views.SystemNotificationFullView.as_view()),
]