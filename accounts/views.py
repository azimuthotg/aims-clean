# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import User

@csrf_protect
def login_view(request):
    """
    View สำหรับหน้า Login
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'เข้าสู่ระบบสำเร็จ')
            return redirect('dashboard:home')
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
    """Redirect ไป dashboard โดยตรง (portal ไม่ได้ใช้แล้ว)"""
    return redirect('dashboard:home')

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

# User Management Views
def can_manage_users(user):
    """ตรวจสอบสิทธิ์การจัดการผู้ใช้"""
    return user.is_authenticated and user.can_manage_users()

@login_required
@user_passes_test(can_manage_users, login_url='/dashboard/')
def user_management(request):
    """หน้าจัดการผู้ใช้งาน"""
    # Search functionality
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    
    # Base queryset
    users = User.objects.all()
    
    # Apply filters
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(department__icontains=search_query)
        )
    
    if role_filter:
        users = users.filter(user_role=role_filter)
    
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(users, 20)  # 20 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'ldap_users': User.objects.filter(is_ldap_user=True).count(),
        'super_admins': User.objects.filter(user_role='super_admin').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'user_roles': User.USER_ROLES,
        'stats': stats,
    }
    
    return render(request, 'accounts/user_management.html', context)

@login_required
@user_passes_test(can_manage_users, login_url='/dashboard/')
def user_detail(request, user_id):
    """หน้ารายละเอียดผู้ใช้"""
    user_obj = get_object_or_404(User, id=user_id)
    
    context = {
        'user_obj': user_obj,
        'can_edit': request.user.user_role == 'super_admin' or request.user == user_obj,
    }
    
    return render(request, 'accounts/user_detail.html', context)

@login_required
@user_passes_test(can_manage_users, login_url='/dashboard/')
def user_edit(request, user_id):
    """แก้ไขข้อมูลผู้ใช้"""
    user_obj = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Update basic info
        user_obj.first_name = request.POST.get('first_name', '')
        user_obj.last_name = request.POST.get('last_name', '')
        user_obj.email = request.POST.get('email', '')
        user_obj.phone = request.POST.get('phone', '')
        user_obj.department = request.POST.get('department', '')
        user_obj.division = request.POST.get('division', '')
        user_obj.position = request.POST.get('position', '')
        user_obj.notes = request.POST.get('notes', '')
        
        # Only super admin can change roles and status
        if request.user.user_role == 'super_admin':
            user_obj.user_role = request.POST.get('user_role', user_obj.user_role)
            user_obj.is_active = request.POST.get('is_active') == 'on'
            user_obj.is_staff = request.POST.get('is_staff') == 'on'
            
            # Update system access
            if not user_obj.system_access:
                user_obj.system_access = user_obj.get_default_system_access()
            if not user_obj.system_roles:
                user_obj.system_roles = user_obj.get_default_system_roles()
            
            # Update system access permissions
            user_obj.system_access['aims'] = True  # Always true
            user_obj.system_access['dashboard'] = request.POST.get('system_access_dashboard') == 'on'
            user_obj.system_access['document'] = request.POST.get('system_access_document') == 'on'
            user_obj.system_access['planning'] = request.POST.get('system_access_planning') == 'on'
            user_obj.system_access['library'] = False  # Not ready yet
            user_obj.system_access['finance'] = False  # Not ready yet
            
            # Update system roles
            user_obj.system_roles['aims'] = user_obj.user_role  # Use current AIMS role
            user_obj.system_roles['dashboard'] = request.POST.get('system_roles_dashboard', 'viewer')
            user_obj.system_roles['document'] = request.POST.get('system_roles_document', 'viewer')  
            user_obj.system_roles['planning'] = request.POST.get('system_roles_planning', 'viewer')
        
        user_obj.save()
        messages.success(request, f'อัพเดทข้อมูลของ {user_obj.get_full_name()} เรียบร้อยแล้ว')
        return redirect('user_detail', user_id=user_obj.id)
    
    context = {
        'user_obj': user_obj,
        'user_roles': User.USER_ROLES,
        'is_super_admin': request.user.user_role == 'super_admin',
    }
    
    return render(request, 'accounts/user_edit.html', context)

@login_required
@user_passes_test(can_manage_users, login_url='/dashboard/')
def add_user(request):
    """เพิ่มผู้ใช้ใหม่"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_role = request.POST.get('user_role', 'academic_service')
        is_ldap_user = request.POST.get('is_ldap_user') == 'on'
        
        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, f'ชื่อผู้ใช้ "{username}" มีอยู่ในระบบแล้ว')
            return render(request, 'accounts/add_user.html', {
                'user_roles': User.USER_ROLES,
                'form_data': request.POST
            })
        
        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_role=user_role,
            is_ldap_user=is_ldap_user,
            department=request.POST.get('department', ''),
            division=request.POST.get('division', ''),
            position=request.POST.get('position', ''),
            phone=request.POST.get('phone', ''),
            notes=request.POST.get('notes', ''),
        )
        
        # Set password only for non-LDAP users
        if not is_ldap_user:
            password = request.POST.get('password')
            if password:
                user.set_password(password)
                user.save()
        
        messages.success(request, f'เพิ่มผู้ใช้ "{user.get_full_name()}" เรียบร้อยแล้ว')
        return redirect('user_detail', user_id=user.id)
    
    context = {
        'user_roles': User.USER_ROLES,
    }
    
    return render(request, 'accounts/add_user.html', context)

@login_required
def update_last_activity(request):
    """อัพเดทกิจกรรมล่าสุดของผู้ใช้"""
    if request.user.is_authenticated:
        User.objects.filter(id=request.user.id).update(last_activity=timezone.now())
    return JsonResponse({'status': 'ok'})