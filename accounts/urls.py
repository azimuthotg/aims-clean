from django.urls import path
from . import views, api_views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('portal/', views.portal_view, name='portal'),

    # User Management
    path('users/', views.user_management, name='user_management'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('update-activity/', views.update_last_activity, name='update_last_activity'),
    
    # SSO API Endpoints
    path('api/sso/generate-token/', api_views.generate_sso_token_api, name='api_generate_sso_token'),
    path('api/sso/verify-token/', api_views.verify_sso_token_api, name='api_verify_sso_token'),
    path('api/sso/refresh-token/', api_views.refresh_sso_token_api, name='api_refresh_sso_token'),
    path('api/sso/check-access/', api_views.check_system_access_api, name='api_check_system_access'),
    path('api/user/systems/', api_views.get_user_systems_api, name='api_user_systems'),
    path('api/user/profile/', api_views.get_user_profile_api, name='api_user_profile'),
    path('api/system/access/', api_views.SystemAccessView.as_view(), name='api_system_access'),
]