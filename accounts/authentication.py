import requests
import json
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class LDAPBackend:
    """
    Custom Authentication Backend สำหรับตรวจสอบข้อมูลผู้ใช้จาก LDAP API
    """
    
    def authenticate(self, request, username=None, password=None):
        """
        ตรวจสอบสิทธิ์ผ่าน LDAP API และสร้างหรืออัปเดตข้อมูลผู้ใช้ในฐานข้อมูล
        """
        if not username or not password:
            return None
            
        # ข้อมูลสำหรับส่งไปยัง API
        api_url = "https://api.npu.ac.th/v2/ldap/auth_and_get_personnel/"
        headers = {
            "Authorization": f"Bearer {settings.LDAP_API_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "userLdap": username,
            "passLdap": password
        }
        
        try:
            # ส่งคำขอไปยัง API
            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()  # ตรวจสอบ HTTP errors
            
            # ตรวจสอบข้อมูลที่ได้รับ
            data = response.json()
            
            # ตรวจสอบว่า login สำเร็จหรือไม่ (ตามรูปแบบ response จริง)
            if data.get('success', False):
                # ข้อมูลหลักของบุคลากร
                personnel_info = data.get('personnel_info', {})
                # ข้อมูลเพิ่มเติม
                additional_info = data.get('additional_info', {})
                
                # รวมข้อมูลทั้งหมด
                personnel_data = {**personnel_info, **additional_info}
                
                # ตรวจสอบว่าเป็นเจ้าหน้าที่สำนักวิทยบริการหรือไม่
                is_academic_service = self._check_is_academic_service(personnel_data)
                
                # สร้างหรืออัปเดตข้อมูลผู้ใช้
                user, created = User.objects.update_or_create(
                    username=username,
                    defaults={
                        'first_name': personnel_info.get('prefixfullname', '') + personnel_info.get('staffname', ''),
                        'last_name': personnel_info.get('staffsurname', ''),
                        'personnel_id': personnel_info.get('staffid', ''),
                        'department': personnel_info.get('departmentname', ''),
                        'position': additional_info.get('position', ''),
                        'personnel_type': personnel_info.get('sfftypenameT', ''),
                        'is_academic_service': is_academic_service,
                        'ldap_data': data,
                    }
                )
                
                # ถ้าเป็นการสร้างผู้ใช้ใหม่ ตั้งค่า password ที่ไม่สามารถใช้ login ผ่าน Django ได้
                if created:
                    user.set_unusable_password()
                    user.save()
                
                # ถ้าเป็นเจ้าหน้าที่สำนักวิทยบริการ จึงอนุญาตให้เข้าใช้งานระบบ
                if is_academic_service:
                    return user
            
            return None
                
        except requests.exceptions.RequestException as e:
            print(f"LDAP API Error: {e}")
            return None
    
    def _check_is_academic_service(self, personnel_data):
        """
        ตรวจสอบว่าเป็นเจ้าหน้าที่สำนักวิทยบริการหรือไม่
        ปรับตามข้อมูลจริงที่ได้รับจาก API
        """
        # ตามข้อมูลที่ได้รับจาก API
        department = personnel_data.get('departmentname', '').lower()
        return 'สำนักวิทยบริการ' in department
    
    def get_user(self, user_id):
        """
        ดึงข้อมูลผู้ใช้จาก ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None