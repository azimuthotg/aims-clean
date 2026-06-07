# 📋 AIMS — ดัชนีเอกสารทั้งหมด

ระบบสารสนเทศเพื่อการจัดการข้อมูลวิชาการ (Academic Information Management System)
มหาวิทยาลัยนครพนม (NPU)

- **Production:** https://lib.npu.ac.th/aims/
- **Repository:** https://github.com/azimuthotg/aims-clean
- **Stack:** Django 5.0 + MySQL + Oracle (sync) + Tailwind CSS + ApexCharts

---

## 📚 เอกสารหลัก

| เอกสาร | รายละเอียด |
|---|---|
| [CLAUDE.md](../CLAUDE.md) | คู่มือสถาปัตยกรรมระบบ + คำสั่งพัฒนา (สำหรับ Claude Code) |
| [doc/deploy-guide.md](deploy-guide.md) | คู่มือ Deploy บน Production (IIS + ARR + Waitress) |
| [deploy/DEPLOY.md](../deploy/DEPLOY.md) | ขั้นตอน deploy เพิ่มเติม |
| [docs/server_deployment_guide.md](../docs/server_deployment_guide.md) | คู่มือติดตั้งบน server |

---

## 🚀 Timeline การพัฒนา (Progress Logs)

| วันที่ | บันทึก | สรุปงาน |
|---|---|---|
| 2026-05-07 | [progress-2026-05-07.md](progress-2026-05-07.md) | Sync Monitor, ปรับ sync staff/student, Rewrite Executive Dashboard (Tailwind), ย้ายไป Windows Task Scheduler, Thai date format |
| 2026-06-07 | [progress-2026-06-07.md](progress-2026-06-07.md) | สร้าง INDEX.md (ดัชนีเอกสาร), ทบทวนสถานะโปรเจกต์ |

> งานหลังวันที่ 7 พ.ค. (Search Feature + Timezone Fix ~25 พ.ค.) ยังไม่มี progress log แยก — ดูได้จาก git log

---

## 🏗️ โครงสร้างระบบ (3 Apps)

| App | หน้าที่ |
|---|---|
| `accounts/` | LDAP Authentication & User Management |
| `dashboard/` | Operational Dashboards (Staff, Student, Service Stats, Search, Sync Monitor) |
| `dashboard_system/` | Executive Dashboard v2.0 (Management Analytics) |

---

## 🔑 ฟีเจอร์สำคัญ

| ฟีเจอร์ | สถานะ | หมายเหตุ |
|---|---|---|
| LDAP Authentication (NPU API) | ✅ | |
| Staff / Student / Service Dashboard | ✅ | Tailwind CSS |
| Executive Dashboard v2.0 | ✅ | Tailwind CSS |
| Search (Staff/Student + LINE userId) | ✅ | JOIN `apiapp_userprofile` |
| Sync Monitor | ✅ | UI + manual trigger + history |
| Auto Sync (Windows Task Scheduler) | ✅ | staff 02:00 / students 02:30 |
| PWA + Push Notifications | ✅ | |
| Export Excel | ✅ | ครบทุกหน้า |

---

## 🗄️ แหล่งข้อมูล (Data Sources)

| ข้อมูล | ต้นทาง | ปลายทาง |
|---|---|---|
| บุคลากร (staff_info) | MySQL 202.29.55.29 | MySQL 202.29.55.213 (api) |
| นักศึกษา (students_info) | Oracle 202.29.55.15 (thick mode) | MySQL 202.29.55.213 (api) |
| สถิติงานบริการ | Google Sheets API | — |

---

*อัปเดตล่าสุด: 7 มิถุนายน 2569 (สร้าง INDEX.md + progress log)*
