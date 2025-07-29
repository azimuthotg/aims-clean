from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('portal/', views.portal_view, name='portal'),
    path('test-ldap/', views.test_ldap_api, name='test_ldap_api'),
]