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
import time

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.db import connection
from django.http import JsonResponse

# ฟังก์ชันสำหรับ redirect เมื่อเข้า root URL
def redirect_to_login_or_portal(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    else:
        return redirect('login')

# Health endpoint สำหรับ NMS Agent monitoring — เช็ก DB ด้วย SELECT 1 (public)
def health(request):
    t0 = time.monotonic()
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        db_status = 'ok'
    except Exception as e:
        db_status = f'error: {e}'
    db_ms = round((time.monotonic() - t0) * 1000)
    status = 'ok' if db_status == 'ok' else 'degraded'
    return JsonResponse(
        {'status': status, 'db': db_status, 'db_ms': db_ms},
        status=200 if status == 'ok' else 503,
    )

urlpatterns = [
    path('health/', health, name='health'),  # NMS monitoring
    path('', redirect_to_login_or_portal, name='home'),  # เพิ่ม root URL pattern
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('executive/', include('dashboard_system.urls')),  # Executive Dashboard System v2.0
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
