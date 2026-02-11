"""
URL configuration for aims_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

# ฟังก์ชันสำหรับ redirect เมื่อเข้า root URL
def redirect_to_login_or_portal(request):
    if request.user.is_authenticated:
        return redirect('portal')  # ถ้า login แล้วให้ไปที่ portal
    else:
        return redirect('login')  # ถ้ายังไม่ login ให้ไปที่หน้า login

urlpatterns = [
    path('', redirect_to_login_or_portal, name='home'),  # เพิ่ม root URL pattern
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('executive/', include('dashboard_system.urls')),  # Executive Dashboard System v2.0
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
