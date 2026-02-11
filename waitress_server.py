"""
AIMS Project - Waitress WSGI Server
สำหรับ Production Deployment บน Windows Server

Usage:
    python waitress_server.py

Configuration:
    - Host: 0.0.0.0 (รับ connection จากทุก IP)
    - Port: 8005 (หรือกำหนดใน environment variable)
    - Threads: 4 (ปรับตามจำนวน CPU cores)
"""

import os
import sys

# เพิ่ม project path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ตั้งค่า Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aims_project.settings')

# โหลด environment variables จาก .env
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, '.env'))
    print("✅ Loaded .env file")
except ImportError:
    print("⚠️ python-dotenv not installed, using system environment variables")

# Import Django และ Waitress
import django
django.setup()

from waitress import serve
from aims_project.wsgi import application

# Configuration
HOST = os.getenv('WAITRESS_HOST', '0.0.0.0')
PORT = int(os.getenv('WAITRESS_PORT', '8005'))
THREADS = int(os.getenv('WAITRESS_THREADS', '4'))

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 AIMS Dashboard - Production Server")
    print("=" * 60)
    print(f"📍 Host: {HOST}")
    print(f"🔌 Port: {PORT}")
    print(f"🧵 Threads: {THREADS}")
    print(f"📂 Base Dir: {BASE_DIR}")
    print("=" * 60)
    print(f"🌐 Server running at http://{HOST}:{PORT}/")
    print("   Press Ctrl+C to stop")
    print("=" * 60)

    try:
        serve(
            application,
            host=HOST,
            port=PORT,
            threads=THREADS,
            url_scheme='http',
            ident='AIMS-Server'
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)
