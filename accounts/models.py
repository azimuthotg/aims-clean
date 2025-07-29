# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User model ที่ขยายจาก Django AbstractUser
    เพื่อเก็บข้อมูลเพิ่มเติมของผู้ใช้งานจาก LDAP
    """
    personnel_id = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    personnel_type = models.CharField(max_length=50, blank=True, null=True)
    is_academic_service = models.BooleanField(default=False)  # เป็นเจ้าหน้าที่สำนักวิทยบริการหรือไม่
    ldap_data = models.JSONField(blank=True, null=True)  # เก็บข้อมูลทั้งหมดที่ได้จาก LDAP

    def __str__(self):
        return f"{self.username} ({self.get_full_name() or 'No Name'})"