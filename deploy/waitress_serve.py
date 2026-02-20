"""
AIMS Project -- Waitress Entry Point
ใช้สำหรับ Production บน Windows Server (NSSM Service)

รัน: python deploy/waitress_serve.py
หรือผ่าน NSSM service ชื่อ AIMS
"""

import os
import sys

# Force UTF-8 output (ป้องกัน UnicodeEncodeError บน Windows cp1252)
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# เพิ่ม project root เข้า Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Load .env ก่อน import Django
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, '.env'))
    print("[OK] .env loaded")
except ImportError:
    print("[WARN] python-dotenv not installed -- using system environment variables")

# ตั้งค่า Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aims_project.settings')

# อ่าน config จาก .env
host    = os.getenv('WAITRESS_HOST', '127.0.0.1')
port    = int(os.getenv('WAITRESS_PORT', '8001'))
threads = int(os.getenv('WAITRESS_THREADS', '8'))

print(f"[START] AIMS on {host}:{port} ({threads} threads)")
print(f"  FORCE_SCRIPT_NAME = '{os.getenv('FORCE_SCRIPT_NAME', '')}'")
print(f"  DEBUG             = {os.getenv('DEBUG', 'False')}")

from waitress import serve
from aims_project.wsgi import application

serve(
    application,
    host=host,
    port=port,
    threads=threads,
    url_scheme='https',
)
