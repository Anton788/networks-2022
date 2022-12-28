from django.urls import path
from Organizations import views

urlpatterns = [
    path('company/create/', views.CompanyCreateView.as_view()),
    path('company/update/', views.CompanyUpdateView.as_view()),
    path('company/get/', views.CompanyGetView.as_view()),
    path('company/permissions/', views.CompanyPermissionsForUserView.as_view()),
    path('company/permissions/update/', views.UpdateCompanyUserPermissionsView.as_view()),
    path('company/users/add/', views.CompanyAddUsersView.as_view()),
    path('company/users/subordinate/', views.CompanyShowSubordinateUsersView.as_view()),
    path('company/list/', views.CompaniesListView.as_view()),
    path('company/search/', views.SearchCompanyByNameView.as_view()),
    path('company/factories/list/', views.FactoriesForCompanyListView.as_view()),
    path('company/address/create/', views.CompanyAddressCreateView.as_view()),
    path('company/address/update/', views.CompanyAddressUpdateView.as_view()),
    path('company/file/add/', views.AddCompanyApprovementFileView.as_view()),
    path('company/file/delete/', views.DeleteCompanyApprovementFileView.as_view()),
    path('company/file/update/', views.UpdateCompanyApprovementFileView.as_view()),

    # =============== PARTNERS ====================
    path('company/partners/add/', views.AddPartnerRelationsCompanyView.as_view()),
    path('company/partners/request/list/', views.PotentialPartnersListView.as_view()),
    path('company/partners/request/amount/', views.PotentialPartnersAmountView.as_view()),
    path('company/partners/list/', views.ActualPartnersListView.as_view()),
    path('company/partners/confirm/', views.ConfirmPartnersView.as_view()),
    path('company/partners/reject/', views.RejectPartnersView.as_view()),
    path('company/partners/file/add/', views.AddRelationshipFileView.as_view()),
    path('company/partners/file/delete/', views.DeleteRelationshipFileView.as_view()),
    path('company/partners/file/update/', views.UpdateRelationshipFileView.as_view()),

    # ============== FACTORIES ====================
    path('factory/create/', views.FactoryCreateView.as_view()),
    path('factory/update/', views.FactoryUpdateView.as_view()),
    path('factory/get/', views.FactoryGetView.as_view()),
    path('factory/list/', views.FactoriesListView.as_view()),

    path('factory/users/add/', views.FactoryAddUsersView.as_view()),
    path('factory/users/subordinate/', views.FactoryShowSubordinateUsersView.as_view()),
    
    # ============== INVITATION LINKS ====================
    path("email/invitation/link/", views.SendInvitationLinkView.as_view()),
    path("accept/invitation/link/", views.AcceptInvitationLinkView.as_view()),
    path("invitation/company/info/", views.GetCompanyFromInvitationLinkView.as_view()),
    path("invite/company/", views.InviteCompanyView.as_view()),
    
    # ============== OKVED ====================
    path("add/okved/", views.AddOkvedToTableView.as_view()),
    path("okved/search/", views.SearchOkvedView.as_view()),
]
