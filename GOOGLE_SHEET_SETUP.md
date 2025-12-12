# 📊 Google Sheet Setup Guide - تعليمات إعداد جداول Google

## 🔗 Sheet Link
**Sheet ID:** `1mwSH2hFmggSjxBnkqbIZARylMd_3fXtrF2M0pTgrJe0`
**URL:** https://docs.google.com/spreadsheets/d/1mwSH2hFmggSjxBnkqbIZARylMd_3fXtrF2M0pTgrJe0/edit

---

## ✅ Required Tabs (الأوراق المطلوبة)

يجب إنشاء 3 أوراق بالضبط بهذه الأسماء (الأسماء حساسة لحالة الأحرف):

1. **ORDERS** (بأحرف كبيرة)
2. **ROUTES** (بأحرف كبيرة)
3. **DRIVERS** (بأحرف كبيرة)

---

## 📋 Tab 1: ORDERS

### Header Row (الصف الأول - العناوين)
```
order_id | date | created_at | status | order_type | customer_name | customer_phone | address | city | zip_code | items | time_window_start | time_window_end | special_notes | assigned_driver | route_id | stop_number | eta | updated_at
```

### Column Details (تفاصيل الأعمدة)

| Column # | Column Name | Description | Example |
|----------|-------------|-------------|---------|
| A (1) | order_id | معرف الطلب | ORD-20241213-001 |
| B (2) | date | تاريخ الطلب | 2024-12-13 |
| C (3) | created_at | وقت الإنشاء | 2024-12-13T10:30:00 |
| D (4) | status | حالة الطلب | pending / completed |
| E (5) | order_type | نوع الطلب | Delivery / Pickup |
| F (6) | customer_name | اسم العميل | John Smith |
| G (7) | customer_phone | رقم الهاتف | 760-555-1234 |
| H (8) | address | العنوان | 123 Main St |
| I (9) | city | المدينة | Irvine |
| J (10) | zip_code | الرمز البريدي | 92618 |
| K (11) | items | المعدات | Hospital Bed, Oxygen |
| L (12) | time_window_start | بداية الوقت | 10:00 AM |
| M (13) | time_window_end | نهاية الوقت | 2:00 PM |
| N (14) | special_notes | ملاحظات | Call before arrival |
| O (15) | assigned_driver | السائق المعين | (فارغ في البداية) |
| P (16) | route_id | معرف المسار | (فارغ في البداية) |
| Q (17) | stop_number | رقم التوقف | (فارغ في البداية) |
| R (18) | eta | الوقت المتوقع | (فارغ في البداية) |
| S (19) | updated_at | آخر تحديث | (فارغ في البداية) |

### ⚠️ Important Notes for ORDERS
- الصف الأول (Row 1) = العناوين فقط
- البيانات تبدأ من الصف الثاني (Row 2)
- الأعمدة من A إلى S (19 عمود)
- الأعمدة O, P, Q, R, S تملأ تلقائياً عند التحسين

---

## 🚚 Tab 2: ROUTES

### Header Row (الصف الأول - العناوين)
```
route_id | date | driver_name | start_location | total_stops | total_distance_miles | total_drive_time_min | estimated_finish | route_status | sent_at | created_at
```

### Column Details (تفاصيل الأعمدة)

| Column # | Column Name | Description | Example |
|----------|-------------|-------------|---------|
| A (1) | route_id | معرف المسار | ROUTE-20241213-JOHN |
| B (2) | date | التاريخ | 2024-12-13 |
| C (3) | driver_name | اسم السائق | John Smith |
| D (4) | start_location | نقطة البداية | Irvine Office |
| E (5) | total_stops | عدد التوقفات | 5 |
| F (6) | total_distance_miles | المسافة بالأميال | 45.2 |
| G (7) | total_drive_time_min | وقت القيادة بالدقائق | 120 |
| H (8) | estimated_finish | وقت الانتهاء المتوقع | 2:30 PM |
| I (9) | route_status | حالة المسار | planned / in_progress / completed |
| J (10) | sent_at | وقت الإرسال | (فارغ في البداية) |
| K (11) | created_at | وقت الإنشاء | 2024-12-13T10:30:00 |

### ⚠️ Important Notes for ROUTES
- الصف الأول (Row 1) = العناوين فقط
- البيانات تبدأ من الصف الثاني (Row 2)
- الأعمدة من A إلى K (11 عمود)
- هذه البيانات تحفظ تلقائياً عند حفظ المسارات

---

## 👥 Tab 3: DRIVERS

### Header Row (الصف الأول - العناوين)
```
driver_id | driver_name | phone | email | status | primary_areas | cities_covered | zip_prefixes | vehicle_type | start_location | notes | created_at | updated_at
```

### Column Details (تفاصيل الأعمدة)

| Column # | Column Name | Description | Example |
|----------|-------------|-------------|---------|
| A (1) | driver_id | معرف السائق | DRV-001 |
| B (2) | driver_name | اسم السائق | John Smith |
| C (3) | phone | رقم الهاتف | 760-555-1234 |
| D (4) | email | البريد الإلكتروني | john@example.com |
| E (5) | status | الحالة | active / inactive |
| F (6) | primary_areas | المناطق الرئيسية | Orange County |
| G (7) | cities_covered | المدن المغطاة | Irvine, Anaheim, Santa Ana |
| H (8) | zip_prefixes | بدايات الرموز البريدية | 92, 90 |
| I (9) | vehicle_type | نوع السيارة | Van / Truck / SUV |
| J (10) | start_location | نقطة البداية | Irvine Office |
| K (11) | notes | ملاحظات | Available weekdays |
| L (12) | created_at | تاريخ الإنشاء | 2024-12-13 |
| M (13) | updated_at | آخر تحديث | 2024-12-13 |

### ⚠️ Important Notes for DRIVERS
- الصف الأول (Row 1) = العناوين فقط
- البيانات تبدأ من الصف الثاني (Row 2)
- الأعمدة من A إلى M (13 عمود)
- يجب إضافة السائقين يدوياً أو من خلال التطبيق

---

## 📝 Sample Data (بيانات تجريبية)

### Sample Driver Data
```
DRV-001 | John Smith | 760-555-1234 | john@example.com | active | Orange County | Irvine, Anaheim | 92 | Van | Irvine Office | Weekday driver | 2024-12-13 | 2024-12-13
DRV-002 | Mike Johnson | 760-555-5678 | mike@example.com | active | Los Angeles | Long Beach, Torrance | 90 | Truck | Long Beach Office | Weekend available | 2024-12-13 | 2024-12-13
```

### Sample Order Data
```
ORD-20241213-001 | 2024-12-13 | 2024-12-13T10:00:00 | pending | Delivery | ABC Hospital | 760-555-9999 | 123 Main St | Irvine | 92618 | Hospital Bed | 10:00 AM | 2:00 PM | Call before | | | | | 
ORD-20241213-002 | 2024-12-13 | 2024-12-13T10:05:00 | pending | Pickup | XYZ Clinic | 760-555-8888 | 456 Oak Ave | Anaheim | 92805 | Oxygen Tank | 1:00 PM | 5:00 PM | Ring doorbell | | | | | 
```

---

## 🔍 Verification Checklist (قائمة التحقق)

### Step 1: Check Tab Names
- [ ] يوجد تاب اسمه **ORDERS** بالضبط (حروف كبيرة)
- [ ] يوجد تاب اسمه **ROUTES** بالضبط (حروف كبيرة)
- [ ] يوجد تاب اسمه **DRIVERS** بالضبط (حروف كبيرة)

### Step 2: Check ORDERS Tab
- [ ] الصف الأول يحتوي على 19 عمود
- [ ] العمود A = order_id
- [ ] العمود B = date
- [ ] العمود S = updated_at
- [ ] لا توجد أعمدة إضافية

### Step 3: Check ROUTES Tab
- [ ] الصف الأول يحتوي على 11 عمود
- [ ] العمود A = route_id
- [ ] العمود B = date
- [ ] العمود K = created_at
- [ ] لا توجد أعمدة إضافية

### Step 4: Check DRIVERS Tab
- [ ] الصف الأول يحتوي على 13 عمود
- [ ] العمود A = driver_id
- [ ] العمود B = driver_name
- [ ] العمود M = updated_at
- [ ] لا توجد أعمدة إضافية
- [ ] يوجد سائق واحد على الأقل في الصف 2

---

## 🛠️ Common Issues & Solutions

### ❌ Issue 1: "Worksheet 'DRIVERS' not found"
**Solution:** تأكد من أن اسم التاب بالضبط `DRIVERS` بحروف كبيرة، ليس `Drivers` أو `drivers`

### ❌ Issue 2: "Error reading drivers"
**Solution:** تأكد من أن:
- الصف الأول يحتوي على أسماء الأعمدة بالضبط
- يوجد على الأقل سائق واحد في الصف 2
- جميع الأعمدة المطلوبة موجودة

### ❌ Issue 3: Missing columns
**Solution:** راجع عدد الأعمدة:
- ORDERS = 19 عمود
- ROUTES = 11 عمود
- DRIVERS = 13 عمود

### ❌ Issue 4: Extra columns
**Solution:** احذف أي أعمدة إضافية بعد الأعمدة المطلوبة

---

## 📸 Visual Guide

### How to Set Up (كيفية الإعداد):

1. **افتح Google Sheet**
   - اذهب إلى الرابط
   - تأكد من تسجيل الدخول

2. **قم بإنشاء/إعادة تسمية الأوراق**
   - انقر بزر الماوس الأيمن على اسم الورقة
   - اختر "Rename"
   - اكتب الاسم الصحيح بحروف كبيرة

3. **أدخل العناوين**
   - انسخ العناوين من الأعلى
   - الصق في الصف الأول
   - استخدم Tab أو السهم للانتقال بين الخلايا

4. **أضف بيانات السائقين**
   - اذهب إلى تاب DRIVERS
   - أدخل معلومات السائقين في الصف 2 وما بعده

5. **احفظ واختبر**
   - Google Sheets يحفظ تلقائياً
   - قم بتشغيل التطبيق للاختبار

---

## 🧪 Test Your Setup

بعد الإعداد، شغل هذا الكود للاختبار:

```python
from components.database import Database

# Test connection
db = Database()

# Test drivers
drivers = db.get_drivers()
print(f"Found {len(drivers)} drivers")
for driver in drivers:
    print(f"- {driver['driver_name']}")
```

إذا نجح، يجب أن ترى:
```
Found 2 drivers
- John Smith
- Mike Johnson
```

---

## 📞 Need Help?

إذا واجهت مشاكل:
1. تأكد من أن أسماء التابات صحيحة (ORDERS, ROUTES, DRIVERS)
2. تأكد من أن العناوين في الصف الأول
3. تأكد من عدد الأعمدة الصحيح
4. تأكد من وجود بيانات في DRIVERS

**Contact:**
- Phone: 760-879-1071
- Check: `QUICKSTART.md` for more help

---

**Last Updated:** 2024-12-13  
**Version:** 1.0
