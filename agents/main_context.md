# AIMS Development Context

## Project Overview
**AIMS (Academic Information Management System)** is a Django web application for academic staff and student data management at NPU (Nakhon Phanom University).

## Current System Status
- **Framework**: Django with AdminLTE3 UI
- **Charts**: ApexCharts (modern interactive charts)
- **PWA**: Progressive Web App capabilities
- **Authentication**: LDAP integration with NPU API
- **Database**: MySQL with separate `aims` and `api` databases
- **Features**: Staff/Student dashboards, Service statistics, Dark/Light mode

## Database Structure
```sql
-- API Database Tables
- api.staff_info (staff data)
- api.students_info (student data)

-- Django Database Tables  
- accounts_user (LDAP user authentication)
- Additional Django app tables
```

## Current Features
### ✅ Completed Features
- [x] AdminLTE 3 UI Framework with Academic Blue theme
- [x] ApexCharts interactive visualizations  
- [x] Dark/Light mode toggle with persistence
- [x] Chart export (PNG, SVG, Print, CSV)
- [x] Progressive Web App (PWA) with offline support
- [x] Responsive design for mobile/desktop
- [x] Environment variables for security
- [x] Push notifications (95% complete)

### 📊 Current Dashboard Pages
1. **Staff Dashboard** (`/dashboard/staff/`)
   - Staff overview statistics
   - Department breakdown
   - Basic charts with ApexCharts

2. **Student Dashboard** (`/dashboard/student/`)
   - Student enrollment numbers
   - Faculty distribution
   - Academic year comparisons

3. **Service Statistics** (`/dashboard/service/`)
   - Google Sheets integration
   - Service usage data
   - Library and resource statistics

## Technology Stack
- **Backend**: Django 4.x with Python
- **Frontend**: AdminLTE3 + Bootstrap 5.3.2 + ApexCharts
- **Database**: MySQL (202.29.55.213:3306)
- **Authentication**: LDAP API (https://api.npu.ac.th/v2/ldap/auth_and_get_personnel/)
- **External APIs**: Google Sheets API
- **PWA**: Service Worker + Manifest

## File Structure
```
aims_project/
├── manage.py
├── aims_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── models.py (Custom User with LDAP fields)
│   ├── authentication.py (LDAPBackend)
│   └── templates/
├── dashboard/
│   ├── views.py (Staff/Student/Service dashboards)
│   ├── database_utils.py (MySQL connections)
│   ├── sheets_utils.py (Google Sheets API)
│   └── templates/
├── smart_form/ (minimal implementation)
├── static/
│   ├── adminlte/ (AdminLTE3 assets)
│   ├── js/ (ApexCharts, custom scripts)
│   └── css/ (custom themes)
└── templates/ (base templates)
```

## Current Users & Access
- **Target Users**: Academic Service staff at NPU (`สำนักวิทยบริการ`)
- **Authentication**: Only authorized Academic Service staff can access
- **Usage**: Internal data analysis and reporting

## Development Goals
### Primary Objectives
1. **Enhanced Data Analytics**: More interactive charts, drill-down capabilities
2. **Advanced Reporting**: Automated report generation (PDF, Excel)
3. **Data Integration**: Better data source connections beyond Google Sheets
4. **User Experience**: Improved analytics workflow for staff

### Success Metrics
- Faster data analysis for Academic Service staff
- More comprehensive reporting capabilities
- Better data visualization and insights
- Reduced manual report generation time

## Known Technical Details
- **Environment**: Development mode with DEBUG=True
- **Security**: Environment variables implemented for sensitive data
- **Performance**: PWA caching and offline support
- **Mobile**: Fully responsive design
- **Exports**: Chart exports working (PNG, SVG, CSV, Print)

## Next Development Phase
Focus on **academic data analysis improvements** for Academic Service staff, not enterprise-level scaling.

## Contact & Context
- **Institution**: Nakhon Phanom University (NPU)
- **Department**: Academic Service (`สำนักวิทยบริการ`)
- **Purpose**: Internal data analysis and reporting system
- **Scale**: Department-level usage, not university-wide enterprise system