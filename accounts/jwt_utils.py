# accounts/jwt_utils.py
import jwt
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from typing import Dict, Optional

User = get_user_model()

class SSOTokenManager:
    """JWT Token Manager สำหรับ SSO ระหว่างระบบ"""
    
    @staticmethod
    def get_jwt_secret():
        """ดึง JWT Secret Key"""
        return getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
    
    @staticmethod
    def generate_sso_token(user: User, expires_hours: int = 8) -> str:
        """สร้าง SSO Token สำหรับผู้ใช้"""
        
        payload = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.get_full_name(),
            'user_role': user.user_role,
            'department': user.department,
            'division': user.division,
            'system_access': user.system_access or user.get_default_system_access(),
            'system_roles': user.system_roles or user.get_default_system_roles(),
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=expires_hours),
            'iss': 'aims-hub',  # Issuer
            'aud': 'aims-systems'  # Audience
        }
        
        return jwt.encode(payload, SSOTokenManager.get_jwt_secret(), algorithm='HS256')
    
    @staticmethod
    def verify_sso_token(token: str) -> Optional[Dict]:
        """ตรวจสอบ SSO Token"""
        try:
            payload = jwt.decode(
                token, 
                SSOTokenManager.get_jwt_secret(), 
                algorithms=['HS256'],
                audience='aims-systems',
                issuer='aims-hub'
            )
            return payload
        except jwt.ExpiredSignatureError:
            return {'error': 'Token has expired'}
        except jwt.InvalidTokenError:
            return {'error': 'Invalid token'}
        except Exception as e:
            return {'error': f'Token verification failed: {str(e)}'}
    
    @staticmethod
    def refresh_token(token: str) -> Optional[str]:
        """ต่ออายุ Token หากใกล้หมดอายุ"""
        payload = SSOTokenManager.verify_sso_token(token)
        
        if 'error' in payload:
            return None
            
        try:
            user = User.objects.get(id=payload['user_id'])
            # สร้าง token ใหม่
            return SSOTokenManager.generate_sso_token(user)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_from_token(token: str) -> Optional[User]:
        """ดึงข้อมูลผู้ใช้จาก Token"""
        payload = SSOTokenManager.verify_sso_token(token)
        
        if 'error' in payload:
            return None
            
        try:
            return User.objects.get(id=payload['user_id'])
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def check_system_access(token: str, system_code: str) -> Dict:
        """ตรวจสอบสิทธิ์เข้าระบบเฉพาะ"""
        payload = SSOTokenManager.verify_sso_token(token)
        
        if 'error' in payload:
            return {'allowed': False, 'error': payload['error']}
        
        system_access = payload.get('system_access', {})
        system_roles = payload.get('system_roles', {})
        
        if not system_access.get(system_code, False):
            return {
                'allowed': False, 
                'error': f'No access to {system_code} system'
            }
        
        return {
            'allowed': True,
            'user_id': payload['user_id'],
            'username': payload['username'],
            'role': system_roles.get(system_code, 'viewer'),
            'user_data': {
                'email': payload.get('email'),
                'full_name': payload.get('full_name'),
                'department': payload.get('department'),
                'division': payload.get('division'),
                'user_role': payload.get('user_role')
            }
        }

class SSOMiddleware:
    """Middleware สำหรับตรวจสอบ SSO Token"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # ดึง token จาก cookie หรือ header
        token = self._get_token_from_request(request)
        
        if token:
            user_data = SSOTokenManager.verify_sso_token(token)
            if 'error' not in user_data:
                request.sso_user_data = user_data
                request.sso_token = token
        
        response = self.get_response(request)
        return response
    
    def _get_token_from_request(self, request):
        """ดึง token จาก request"""
        # จาก Cookie
        token = request.COOKIES.get('sso_token')
        if token:
            return token
            
        # จาก Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header[7:]  # ตัด "Bearer " ออก
            
        return None