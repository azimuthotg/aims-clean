# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

@csrf_protect
def login_view(request):
    """
    View สำหรับหน้า Login
    """
    if request.user.is_authenticated:
        return redirect('portal')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'เข้าสู่ระบบสำเร็จ')
            return redirect('portal')
        else:
            messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง หรือคุณไม่มีสิทธิ์ในการเข้าใช้งานระบบนี้')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    """
    View สำหรับการออกจากระบบ
    """
    logout(request)
    messages.info(request, 'ออกจากระบบแล้ว')
    return redirect('login')

@login_required
def portal_view(request):
    """
    View สำหรับหน้า Portal
    """
    if not request.user.is_authenticated:
        return redirect('login')
        
    return render(request, 'accounts/portal.html')

@csrf_exempt
def test_ldap_api(request):
    """
    View สำหรับทดสอบการเชื่อมต่อกับ LDAP API
    ใช้สำหรับการ Debug เท่านั้น และควรลบออกในโหมด Production
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'Username and password are required'}, status=400)
            
        api_url = "https://api.npu.ac.th/v2/ldap/auth_and_get_personnel/"
        headers = {
            "Authorization": f"Bearer {settings.LDAP_API_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "userLdap": username,
            "passLdap": password
        }
        
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        
        return JsonResponse({
            'status_code': response.status_code,
            'response': response.json()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)