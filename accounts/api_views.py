# accounts/api_views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.views import View
from .jwt_utils import SSOTokenManager
from .models import User

@csrf_exempt
@require_http_methods(["POST"])
def generate_sso_token_api(request):
    """API สำหรับสร้าง SSO Token"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({
                'success': False,
                'error': 'Username and password required'
            }, status=400)
        
        # ตรวจสอบ credential
        user = authenticate(username=username, password=password)
        if not user:
            return JsonResponse({
                'success': False,
                'error': 'Invalid credentials'
            }, status=401)
        
        # สร้าง SSO Token
        token = SSOTokenManager.generate_sso_token(user)
        
        return JsonResponse({
            'success': True,
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.get_full_name(),
                'role': user.user_role,
                'accessible_systems': user.get_accessible_systems()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt  
@require_http_methods(["POST"])
def verify_sso_token_api(request):
    """API สำหรับตรวจสอบ SSO Token"""
    try:
        data = json.loads(request.body)
        token = data.get('token')
        
        if not token:
            return JsonResponse({
                'success': False,
                'error': 'Token required'
            }, status=400)
        
        # ตรวจสอบ token
        payload = SSOTokenManager.verify_sso_token(token)
        
        if 'error' in payload:
            return JsonResponse({
                'success': False,
                'error': payload['error']
            }, status=401)
        
        return JsonResponse({
            'success': True,
            'valid': True,
            'user_data': payload
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET", "POST"])  
def check_system_access_api(request):
    """API สำหรับตรวจสอบสิทธิ์เข้าระบบเฉพาะ"""
    try:
        if request.method == 'GET':
            token = request.GET.get('token')
            system_code = request.GET.get('system')
        else:
            data = json.loads(request.body)
            token = data.get('token')
            system_code = data.get('system')
        
        if not token or not system_code:
            return JsonResponse({
                'success': False,
                'error': 'Token and system code required'
            }, status=400)
        
        # ตรวจสอบสิทธิ์
        access_result = SSOTokenManager.check_system_access(token, system_code)
        
        return JsonResponse({
            'success': True,
            'access_result': access_result
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_user_systems_api(request):
    """API สำหรับดึงรายการระบบที่ผู้ใช้เข้าได้"""
    try:
        user = request.user
        systems = user.get_accessible_systems()
        
        return JsonResponse({
            'success': True,
            'systems': systems,
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.get_full_name(),
                'role': user.user_role
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required  
@require_http_methods(["GET"])
def get_user_profile_api(request):
    """API สำหรับดึงข้อมูลโปรไฟล์ผู้ใช้"""
    try:
        user = request.user
        
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
                'department': user.department,
                'division': user.division,
                'division_display': user.get_division_display_thai(),
                'position': user.position,
                'phone': user.phone,
                'user_role': user.user_role,
                'role_display': user.get_role_display_thai(),
                'is_ldap_user': user.is_ldap_user,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'date_joined': user.date_joined.isoformat(),
                'system_access': user.system_access,
                'system_roles': user.system_roles,
                'accessible_systems': user.get_accessible_systems()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def refresh_sso_token_api(request):
    """API สำหรับต่ออายุ SSO Token"""
    try:
        data = json.loads(request.body)
        old_token = data.get('token')
        
        if not old_token:
            return JsonResponse({
                'success': False,
                'error': 'Token required'
            }, status=400)
        
        # ต่ออายุ token
        new_token = SSOTokenManager.refresh_token(old_token)
        
        if not new_token:
            return JsonResponse({
                'success': False,
                'error': 'Failed to refresh token'
            }, status=401)
        
        return JsonResponse({
            'success': True,
            'token': new_token
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

class SystemAccessView(View):
    """Class-based view สำหรับจัดการสิทธิ์ระบบ"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """ดึงข้อมูลสิทธิ์ระบบทั้งหมด"""
        try:
            # ตรวจสอบ token
            token = request.GET.get('token') or request.COOKIES.get('sso_token')
            if not token:
                return JsonResponse({
                    'success': False,
                    'error': 'Token required'
                }, status=401)
            
            user = SSOTokenManager.get_user_from_token(token)
            if not user:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid token'
                }, status=401)
            
            return JsonResponse({
                'success': True,
                'system_access': user.system_access,
                'system_roles': user.system_roles,
                'accessible_systems': user.get_accessible_systems()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def post(self, request):
        """อัพเดทสิทธิ์ระบบ (สำหรับ admin)"""
        try:
            data = json.loads(request.body)
            token = data.get('token')
            target_user_id = data.get('user_id')
            new_system_access = data.get('system_access')
            new_system_roles = data.get('system_roles')
            
            if not token:
                return JsonResponse({
                    'success': False,
                    'error': 'Token required'
                }, status=401)
            
            # ตรวจสอบสิทธิ์ admin
            admin_user = SSOTokenManager.get_user_from_token(token)
            if not admin_user or not admin_user.can_manage_users():
                return JsonResponse({
                    'success': False,
                    'error': 'Admin access required'
                }, status=403)
            
            # อัพเดทสิทธิ์
            target_user = User.objects.get(id=target_user_id)
            if new_system_access:
                target_user.system_access = new_system_access
            if new_system_roles:
                target_user.system_roles = new_system_roles
            target_user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'System access updated successfully'
            })
            
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'User not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)