from django.urls import path
from Users import views

urlpatterns = [
    path('auth/', views.AuthView.as_view()),
    # path('information/user/main/', views.UserMainInfoView.as_view()),
    path('user/', views.InformationUserView.as_view()),
    path('user/password/<str:user_id>/', views.UpdateUserPasswordView.as_view()),
    path('company/token/<str:company_id>/', views.GetCompanyRelationTokenView.as_view()),
    # path('notifications/token/add/', views.NotificationTokenView.as_view()),
    # path('notifications/token/delete/', views.NotificationTokenInactiveView.as_view()),
    # path('notifications/test/', views.TestNotificationsView.as_view()),
]
