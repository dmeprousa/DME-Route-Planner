# 📋 ملخص سريع - إعداد Google Sheet

## ✅ ما تم إنشاؤه لك:

### ملفات مساعدة:
1. **GOOGLE_SHEET_SETUP.md** - دليل كامل بالإنجليزية
2. **GOOGLE_SHEET_SETUP_AR.md** - دليل كامل بالعربية ✨
3. **verify_setup.py** - سكريبت للتحقق من الإعداد

### ملفات CSV جاهزة في `templates/`:
1. **ORDERS_headers.csv** - عناوين ورقة الطلبات
2. **ROUTES_headers.csv** - عناوين ورقة المسارات
3. **DRIVERS_sample_data.csv** - عناوين وبيانات تجريبية

---

## 🚀 خطوات سريعة (5 دقائق):

### 1. افتح Google Sheet
🔗 https://docs.google.com/spreadsheets/d/1mwSH2hFmggSjxBnkqbIZARylMd_3fXtrF2M0pTgrJe0/edit

### 2. أنشئ 3 أوراق:
- **ORDERS** (بحروف كبيرة)
- **ROUTES** (بحروف كبيرة)
- **DRIVERS** (بحروف كبيرة)

### 3. في ورقة ORDERS:
انسخ والصق هذا في الصف الأول:
```
order_id	date	created_at	status	order_type	customer_name	customer_phone	address	city	zip_code	items	time_window_start	time_window_end	special_notes	assigned_driver	route_id	stop_number	eta	updated_at
```

### 4. في ورقة ROUTES:
انسخ والصق هذا في الصف الأول:
```
route_id	date	driver_name	start_location	total_stops	total_distance_miles	total_drive_time_min	estimated_finish	route_status	sent_at	created_at
```

### 5. في ورقة DRIVERS:
انسخ والصق هذا في الصف الأول:
```
driver_id	driver_name	phone	email	status	primary_areas	cities_covered	zip_prefixes	vehicle_type	start_location	notes	created_at	updated_at
```

ثم في الصف الثاني، أضف سائق:
```
DRV-001	Ahmed Ali	760-879-1071	ahmed@hospiceprodme.com	active	Orange County	Irvine, Anaheim	92, 90	Van	Irvine Office	متاح	2024-12-13	2024-12-13
```

---

## 🔍 تحقق من الإعداد:

شغل السكريبت للتحقق:
```bash
python verify_setup.py
```

إذا كل شيء ✅ = جاهز!  
إذا فيه ❌ = افتح **GOOGLE_SHEET_SETUP_AR.md** لحل المشكلة

---

## ⚠️ تذكير مهم:

### الأخطاء الشائعة:
1. ❌ اسم الورقة `Drivers` → ✅ يجب `DRIVERS`
2. ❌ عدد أعمدة خاطئ → ✅ راجع الأعداد أعلاه
3. ❌ ما فيه سائقين → ✅ أضف سائق واحد على الأقل

---

## 📱 المساعدة:

- **دليل كامل بالعربية:** افتح `GOOGLE_SHEET_SETUP_AR.md`
- **دليل بالإنجليزية:** افتح `GOOGLE_SHEET_SETUP.md`
- **ملفات جاهزة:** مجلد `templates/`
- **تحقق:** شغل `python verify_setup.py`

---

**بالتوفيق! 🎉**

بعد الإعداد، شغل:
```bash
streamlit run app.py
```
