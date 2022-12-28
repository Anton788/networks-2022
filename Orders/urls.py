from django.urls import path
from Orders.views import orders

urlpatterns = [
    path('request/create/', orders.CreateProductRequestView.as_view()),
    path('receive/list/active/', orders.ReceivedProductRequestListView.as_view()),
    path('receive/info/', orders.GetMoreInfoByReceivedProductRequestView.as_view()),
    path('created/info/', orders.GetMoreInfoByCreatedProductRequestView.as_view()),
    path('request/info/', orders.GetRequestInfoView.as_view()),
    path('created/list/active/', orders.CreatedProductRequestListView.as_view()),
    path('request/reject/', orders.RejectProductRequestView.as_view()),
    path('request/accept/', orders.AcceptProductRequestView.as_view()),
    path('request/complex/create/', orders.CreateAnonymousProductRequestView.as_view()),
    path('request/info/update/', orders.UpdateInformationAnonymousProductRequestView.as_view()),
    path('request/image/update/', orders.AddImagesAnonymousProductRequestView.as_view()),
    path('request/file/update/', orders.AddFilesAnonymousProductRequestView.as_view()),
    path('request/complex/complete/', orders.CompleteAnonymousProductRequestView.as_view()),
    path('request/complete/', orders.CompleteProductRequestView.as_view()),
    path('request/statistic/sent/', orders.SentProductRequestStatisticsView.as_view()),
    path('request/statistic/received/', orders.ReceivedProductRequestStatisticsView.as_view()),
]
