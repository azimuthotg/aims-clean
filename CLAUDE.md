# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AIMS (Academic Information Management System) is a Django web application for academic staff and student data management at NPU (Nakhon Phanom University). The system features dual-dashboard architecture with LDAP authentication and advanced analytics capabilities.

## System Architecture

**3-App Structure:**
- `accounts/` - LDAP Authentication & User Management System
- `dashboard/` - Operational Dashboards (Staff, Student, Service Statistics)
- `dashboard_system/` - Executive Dashboard v2.0 (Management Analytics)

**Key Features:**
- LDAP integration with NPU API
- Dual-dashboard system (Operational + Executive)
- PWA support with offline capabilities
- Push notifications system
- Advanced data analytics with ApexCharts
- Export functionality (Excel, CSV, PDF)

## URL Structure

**Main Routes:**
```
/                           → Portal/Login redirect
/accounts/                  → Authentication System
  ├── login/               → LDAP Login
  ├── portal/              → User Portal
  └── users/               → User Management (Admin)

/dashboard/                 → Operational Dashboards
  ├── staff/              → Staff Analytics
  ├── student/            → Student Analytics
  └── service-statistics/ → Service Performance

/executive/                 → Executive Dashboard v2.0
  ├── analytics/          → Advanced Analytics
  ├── insights/           → Management Insights
  └── reports/            → Reports Center

/admin/                     → Django Admin Interface
```

## Development Environment

### Environment Setup
```bash
# Activate virtual environment
source aims_env/bin/activate  # Linux/Mac
# or aims_env\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Environment Variables (.env)
```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,202.29.55.213

# Database Configuration
DB_ENGINE=django.db.backends.mysql
DB_NAME=aims
DB_USER=your-db-username
DB_PASSWORD=your-db-password
DB_HOST=202.29.55.213
DB_PORT=3306

# External API Database (for analytics)
API_DB_HOST=202.29.55.213
API_DB_PORT=3306
API_DB_USER=your-api-db-username
API_DB_PASSWORD=your-api-db-password
API_DB_NAME=api

# LDAP Authentication
LDAP_API_URL=https://api.npu.ac.th/v2/ldap/auth_and_get_personnel/
LDAP_API_TOKEN=your-ldap-jwt-token

# Google Sheets Integration
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials/control-room-440116-7cd01a8c02bd.json
GOOGLE_SHEETS_SPREADSHEET_ID=1Z64aIUqfH2SMc__m3brPINUE6kqgQq_ii0OC8uXiae8
```

## Core Components

### Authentication System (`accounts/`)

**Custom User Model Extensions:**
```python
# accounts/models.py
class User(AbstractUser):
    # LDAP Integration Fields
    personnel_id = models.CharField(max_length=20)
    department = models.CharField(max_length=100)
    division = models.CharField(max_length=50, choices=DIVISION_CHOICES)
    position = models.CharField(max_length=100)
    is_academic_service = models.BooleanField(default=False)
    ldap_data = models.JSONField()
    
    # User Role Management
    USER_ROLES = [
        ('super_admin', 'Super Admin'),
        ('staff_admin', 'Staff Admin'),
        ('academic_service', 'Academic Service'),
        ('read_only', 'Read Only'),
    ]
    user_role = models.CharField(choices=USER_ROLES, default='academic_service')
    
    # Multi-System Access Control
    system_access = models.JSONField(default=dict)  # System permissions
    system_roles = models.JSONField(default=dict)   # Roles in each system
```

**LDAP Authentication Backend:**
```python
# accounts/authentication.py
class LDAPBackend:
    def authenticate(self, request, username=None, password=None):
        # NPU LDAP API integration
        # Creates/updates User model with personnel data
        # Restricts access to Academic Service staff only
```

**Key Views:**
- `login_view` - LDAP authentication
- `portal_view` - User portal with system access
- `user_management` - Admin user management interface

### Operational Dashboards (`dashboard/`)

**Data Sources:**
- Staff data: MySQL `api.staff_info` table
- Student data: MySQL `api.students_info` table
- Service statistics: Google Sheets API

**Key Features:**
```python
# dashboard/database_utils.py
def get_staff_summary():     # Staff analytics data
def get_student_summary():   # Student analytics data
def get_faculty_detail():    # Faculty drill-down data
def get_level_detail():      # Education level drill-down

# dashboard/sheets_utils.py
def get_service_statistics(): # Google Sheets integration
```

**Dashboard Types:**
- **Staff Dashboard** - Department, type, gender analytics
- **Student Dashboard** - Faculty, program, level analytics
- **Service Statistics** - Google Sheets based performance metrics

### Executive Dashboard v2.0 (`dashboard_system/`)

**Advanced Analytics Platform:**
```python
# dashboard_system/views.py
def dashboard_home():        # All-in-one executive overview
def executive_summary():     # KPI API endpoint  
def advanced_analytics():    # Predictive analytics
def management_insights():   # AI-powered insights
def reports_center():        # Report generation
```

**Features:**
- Combined staff + student + service analytics
- Executive KPI overview
- Management insights with recommendations
- Advanced reporting capabilities
- API endpoints for data integration

## Technology Stack

### Frontend Framework
- **AdminLTE 3.2** - Professional admin dashboard template
- **Bootstrap 5.3.2** - Responsive CSS framework
- **ApexCharts** - Modern interactive charts
- **Font Awesome 6.5.1** - Icons

### Backend Framework
- **Django 5.0.6** - Python web framework
- **MySQL 8.0** - Primary database
- **Google Sheets API** - External data source

### UI/UX Features
- **Academic Blue Theme** (#2563eb primary color)
- **Dark/Light Mode Toggle** with localStorage persistence
- **Chart Export System** (PNG, SVG, CSV, Print)
- **PWA Support** (Offline, Push Notifications, Installable)
- **Mobile Responsive Design**

## Database Configuration

### Primary Database (Django)
```python
# aims_project/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'aims',
        'HOST': '202.29.55.213',
        'PORT': '3306',
    }
}
```

### Analytics Database (External)
```python
# dashboard/database_utils.py
# Separate MySQL connection for analytics queries
# Tables: staff_info, students_info (read-only)
```

## Security Implementation

### Current Security Measures
- LDAP authentication via NPU API
- JWT token-based API authentication
- Role-based access control
- CSRF protection enabled
- Secure database connections

### Security Notes for Production
```python
# Recommended for production deployment:
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## PWA Implementation

### Manifest Configuration
```json
// static/manifest.json
{
  "name": "AIMS Dashboard",
  "short_name": "AIMS",
  "theme_color": "#2563eb",
  "background_color": "#ffffff",
  "display": "fullscreen",
  "icons": [...],
  "shortcuts": [...]
}
```

### Service Worker Features
```javascript
// static/sw.js
// - Offline support and caching
// - Push notifications
// - Background sync
// - App update notifications
```

## Testing and Development

### Key Testing URLs
```
http://localhost:8000/                     → Portal/Login
http://localhost:8000/accounts/portal/     → User Portal
http://localhost:8000/accounts/users/      → User Management
http://localhost:8000/dashboard/staff/     → Staff Dashboard
http://localhost:8000/dashboard/student/   → Student Dashboard
http://localhost:8000/dashboard/service-statistics/ → Service Stats
http://localhost:8000/executive/           → Executive Dashboard
http://localhost:8000/admin/               → Django Admin
```

### Database Testing
```python
# Test database connections
python manage.py shell
>>> from dashboard.database_utils import get_db_connection
>>> get_db_connection()

# Test Google Sheets API
>>> from dashboard.sheets_utils import test_sheets_connection
>>> test_sheets_connection()
```

## User Role Management

### Role Hierarchy
```python
USER_ROLES = [
    ('super_admin', 'Super Admin'),        # Full system access
    ('staff_admin', 'Staff Admin'),        # User management + data access
    ('academic_service', 'Academic Service'), # Standard dashboard access
    ('read_only', 'Read Only'),            # View-only access
]
```

### Permission Methods
```python
user.can_manage_users()      # User management permissions
user.can_view_all_data()     # Full data access permissions
user.get_accessible_systems() # Available systems for user
```

## Deployment Guidelines

### Development Server
```bash
python manage.py runserver
```

### Production Considerations
1. **Environment Variables** - Use .env file for sensitive data
2. **Database Optimization** - Configure connection pooling
3. **Static Files** - Configure proper static file serving
4. **Security Headers** - Implement security middleware
5. **HTTPS Configuration** - Enable SSL/TLS
6. **Monitoring** - Set up logging and monitoring

## API Endpoints

### Authentication APIs
```
POST /accounts/api/sso/generate-token/  → Generate SSO token
POST /accounts/api/sso/verify-token/    → Verify token
POST /accounts/api/user/systems/        → Get user systems
```

### Dashboard APIs
```
GET  /executive/api/executive-summary/  → Executive KPIs
POST /dashboard/push/subscribe/         → Push notification subscription
```

## Troubleshooting

### Common Issues

**1. openpyxl Import Error:**
```python
# If openpyxl is not available, imports are commented out in dashboard/views.py
# Install: pip install openpyxl
```

**2. Database Connection:**
```python
# Test connection via admin or shell
# Check .env database credentials
```

**3. LDAP Authentication:**
```python
# Test LDAP API endpoint
# Verify LDAP_API_TOKEN in .env
```

**4. Google Sheets Integration:**
```python
# Verify credentials/control-room-440116-7cd01a8c02bd.json exists
# Check GOOGLE_SHEETS_SPREADSHEET_ID in .env
```

## Development Commands

### Django Management
```bash
# Database operations
python manage.py makemigrations
python manage.py migrate
python manage.py shell

# User management  
python manage.py createsuperuser
python manage.py collectstatic

# System checks
python manage.py check
python manage.py check --deploy
```

### Useful Development Scripts
```bash
# Test environment variables
python test_env_vars.py

# Fix user roles (if needed)
python fix_user_roles.py
```

## Project Status

**Current Status:** Production-ready with advanced dashboard system

**Key Achievements:**
- ✅ LDAP Authentication System
- ✅ Dual Dashboard Architecture  
- ✅ Advanced Analytics with ApexCharts
- ✅ PWA Implementation with Push Notifications
- ✅ Modern UI with AdminLTE 3
- ✅ Export Functionality
- ✅ Mobile Responsive Design
- ✅ User Role Management System

**Architecture:** Single Django project with 3 specialized apps, optimized for academic data visualization and management.