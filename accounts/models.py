# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    """
    Custom User model ที่ขยายจาก Django AbstractUser
    เพื่อเก็บข้อมูลเพิ่มเติมของผู้ใช้งานจาก LDAP
    """
    # LDAP fields
    personnel_id = models.CharField(max_length=20, blank=True, null=True, verbose_name="รหัสบุคลากร")
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name="หน่วยงาน")
    
    # แผนกภายใน สำนักวิทยบริการ
    DIVISION_CHOICES = [
        ('', '--กรุณาเลือกแผนก--'),
        ('information_services', 'แผนกบริการสารสนเทศฯ'),
        ('technical', 'แผนกเทคนิคฯ'),
        ('policy_planning', 'แผนกนโยบายและแผน'),
        ('general_admin', 'แผนกบริหารงานทั่วไป'),
    ]
    
    division = models.CharField(
        max_length=50, 
        choices=DIVISION_CHOICES, 
        blank=True, 
        null=True,
        verbose_name="แผนก"
    )
    
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name="ตำแหน่ง")
    personnel_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="ประเภทบุคลากร")
    is_academic_service = models.BooleanField(default=False, verbose_name="สำนักวิทยบริการ")
    ldap_data = models.JSONField(blank=True, null=True, verbose_name="ข้อมูล LDAP")
    
    # User management fields
    USER_ROLES = [
        ('super_admin', 'Super Admin'),
        ('staff_admin', 'Staff Admin'),
        ('academic_service', 'Academic Service'),
        ('read_only', 'Read Only'),
    ]
    
    user_role = models.CharField(
        max_length=20, 
        choices=USER_ROLES, 
        default='academic_service',
        verbose_name="บทบาทผู้ใช้"
    )
    
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="เบอร์โทรศัพท์")
    profile_image = models.URLField(blank=True, null=True, verbose_name="รูปโปรไฟล์")
    last_activity = models.DateTimeField(default=timezone.now, verbose_name="กิจกรรมล่าสุด")
    is_ldap_user = models.BooleanField(default=True, verbose_name="ผู้ใช้ LDAP")
    notes = models.TextField(blank=True, null=True, verbose_name="หมายเหตุ")
    
    # Multi-System Support Fields
    system_access = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="ระบบที่เข้าได้",
        help_text="ระบบที่ผู้ใช้สามารถเข้าใช้งานได้"
    )
    
    system_roles = models.JSONField(
        default=dict,
        blank=True, 
        verbose_name="บทบาทในแต่ละระบบ",
        help_text="บทบาทของผู้ใช้ในแต่ละระบบ"
    )
    
    class Meta:
        verbose_name = "ผู้ใช้งาน"
        verbose_name_plural = "ผู้ใช้งาน"
        ordering = ['-last_login', 'username']

    def __str__(self):
        return f"{self.username} ({self.get_full_name() or 'No Name'})"
    
    def get_role_display_thai(self):
        """แสดงบทบาทเป็นภาษาไทย"""
        role_thai = {
            'super_admin': 'ผู้ดูแลระบบ',
            'staff_admin': 'ผู้ดูแลบุคลากร', 
            'academic_service': 'เจ้าหน้าที่สำนักวิทยบริการ',
            'read_only': 'ผู้ใช้ทั่วไป'
        }
        return role_thai.get(self.user_role, self.user_role)
    
    def get_division_display_thai(self):
        """แสดงชื่อแผนกเป็นภาษาไทย"""
        if not self.division:
            return "ไม่ระบุแผนก"
        
        division_thai = {
            'information_services': 'แผนกบริการสารสนเทศฯ',
            'technical': 'แผนกเทคนิคฯ',
            'policy_planning': 'แผนกนโยบายและแผน',
            'general_admin': 'แผนกบริหารงานทั่วไป'
        }
        return division_thai.get(self.division, self.division)
    
    def can_manage_users(self):
        """ตรวจสอบสิทธิ์จัดการผู้ใช้"""
        return self.user_role in ['super_admin', 'staff_admin']
    
    def can_view_all_data(self):
        """ตรวจสอบสิทธิ์ดูข้อมูลทั้งหมด"""
        return self.user_role in ['super_admin', 'staff_admin', 'academic_service']
    
    # Multi-System Methods
    def get_default_system_access(self):
        """ค่าเริ่มต้นของระบบที่เข้าได้"""
        return {
            'aims': True,           # ทุกคนเข้า AIMS Hub ได้
            'dashboard': False,     # Port 8010
            'document': False,      # Port 8011  
            'planning': False,      # Port 8012
            'library': False,       # Port 8013 (Future)
            'finance': False        # Port 8014 (Future)
        }
    
    def get_default_system_roles(self):
        """ค่าเริ่มต้นของบทบาทในแต่ละระบบ"""
        return {
            'aims': self.user_role,  # ใช้ role เดิมใน AIMS
            'dashboard': 'viewer',   # viewer, analyst, admin  
            'document': 'viewer',    # viewer, uploader, approver, admin
            'planning': 'viewer',    # viewer, creator, approver, admin
        }
    
    def can_access_system(self, system_code):
        """ตรวจสอบว่าสามารถเข้าระบบได้หรือไม่"""
        if not self.system_access:
            self.system_access = self.get_default_system_access()
            self.save()
        return self.system_access.get(system_code, False)
    
    def get_system_role(self, system_code):
        """ดึงบทบาทในระบบเฉพาะ"""
        if not self.system_roles:
            self.system_roles = self.get_default_system_roles()
            self.save()
        return self.system_roles.get(system_code, 'viewer')
    
    def get_accessible_systems(self):
        """ดึงรายการระบบที่เข้าได้พร้อมข้อมูล"""
        if not self.system_access:
            self.system_access = self.get_default_system_access()
            self.save()
            
        systems = []
        system_info = {
            'aims': {'name': 'AIMS Hub', 'icon': 'fas fa-home', 'port': 8000},
            'dashboard': {'name': 'ระบบสถิติ', 'icon': 'fas fa-chart-bar', 'port': 8010},
            'document': {'name': 'ระบบสารบรรณ', 'icon': 'fas fa-file-alt', 'port': 8011},
            'planning': {'name': 'ระบบแผน', 'icon': 'fas fa-project-diagram', 'port': 8012},
            'library': {'name': 'ระบบห้องสมุด', 'icon': 'fas fa-book', 'port': 8013}, 
            'finance': {'name': 'ระบบการเงิน', 'icon': 'fas fa-money-bill', 'port': 8014}
        }
        
        for system_code, has_access in self.system_access.items():
            if has_access and system_code in system_info:
                info = system_info[system_code]
                systems.append({
                    'code': system_code,
                    'name': info['name'],
                    'icon': info['icon'],
                    'port': info['port'],
                    'role': self.get_system_role(system_code),
                    'url': f'http://localhost:{info["port"]}' if system_code != 'aims' else '/'
                })
        
        return systems
    
    def save(self, *args, **kwargs):
        """Override save เพื่อตั้งค่าเริ่มต้น"""
        # ตั้งค่าเริ่มต้นหากยังไม่มี
        if not self.system_access:
            self.system_access = self.get_default_system_access()
        if not self.system_roles:
            self.system_roles = self.get_default_system_roles()
        
        super().save(*args, **kwargs)