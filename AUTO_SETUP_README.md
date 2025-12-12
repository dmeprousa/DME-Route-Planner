# 🚀 إعداد Google Sheet التلقائي

## ✨ الحل السريع!

بدل ما تعمل كل شيء يدوي، شغل هذا السكريبت وهو يعمل كل شيء تلقائياً!

---

## 📋 ماذا يفعل السكريبت؟

السكريبت `setup_google_sheet.py` يقوم بـ:

### ✅ إنشاء الأوراق:
- ينشئ ورقة ORDERS (إذا مش موجودة)
- ينشئ ورقة ROUTES (إذا مش موجودة)
- ينشئ ورقة DRIVERS (إذا مش موجودة)

### ✅ إضافة العناوين:
- يضيف 19 عمود في ORDERS
- يضيف 11 عمود في ROUTES
- يضيف 13 عمود في DRIVERS

### ✅ بيانات تجريبية:
- يضيف 3 سائقين تجريبيين ب:
  - معلومات كاملة
  - مناطق مختلفة (Orange County, LA, San Diego)
  - أرقام جوالات وبريد إلكتروني
  - حالة active

### ✅ التحقق:
- يتحقق من صحة كل شيء
- يعرض لك النتائج

---

## 🎯 كيف تستخدمه؟

### الخطوة 1: تأكد من الإعداد الأساسي

تحتاج:
- ✅ ملف `credentials.json` موجود
- ✅ ملف `.env` فيه GOOGLE_SHEET_ID
- ✅ اتصال بالإنترنت

### الخطوة 2: شغل السكريبت

```bash
python setup_google_sheet.py
```

**هذا كل شيء!** 🎉

---

## 📺 ماذا سيحدث؟

```
======================================================================
🚀 DME Route Planner - Automatic Google Sheet Setup
   إعداد Google Sheet التلقائي
======================================================================

Step 1: Connecting to Google Sheets...
✅ Connected successfully!

Step 2: Checking existing worksheets...
Existing sheets: Sheet1

Step 3: Creating/verifying required worksheets...
Creating worksheet: ORDERS...
✅ Created ORDERS
Creating worksheet: ROUTES...
✅ Created ROUTES
Creating worksheet: DRIVERS...
✅ Created DRIVERS

Step 4: Setting up headers...
Setting up ORDERS...
✅ ORDERS: Headers set (19 columns)
Setting up ROUTES...
✅ ROUTES: Headers set (11 columns)
Setting up DRIVERS...
✅ DRIVERS: Headers set (13 columns)

Step 5: Adding sample driver data...
No drivers found. Adding sample drivers...
✅ Added driver: Ahmed Ali
✅ Added driver: Mohammed Hassan
✅ Added driver: Ali Mansour

✅ Added 3 sample drivers

Step 6: Verifying setup...
✅ ORDERS: 19 columns - Perfect!
✅ ROUTES: 11 columns - Perfect!
✅ DRIVERS: 13 columns - Perfect!

✅ Found 3 drivers in database

Driver list:
  - Ahmed Ali (active) - Orange County
  - Mohammed Hassan (active) - Los Angeles County
  - Ali Mansour (active) - San Diego County

======================================================================
✅ ✅ ✅ SETUP COMPLETE! ALL SYSTEMS GO! ✅ ✅ ✅
✅ ✅ ✅ اكتمل الإعداد! كل شيء جاهز! ✅ ✅ ✅

Your Google Sheet is ready to use!

Next steps:
1. Run: streamlit run app.py
2. Start adding orders!
======================================================================
```

---

## 🎁 السائقين التجريبيين

السكريبت يضيف 3 سائقين:

### 1. Ahmed Ali
- **المنطقة:** Orange County
- **المدن:** Irvine, Anaheim, Santa Ana, Garden Grove
- **الرموز البريدية:** 92, 92806, 92807
- **السيارة:** Van
- **نقطة البداية:** Irvine Office

### 2. Mohammed Hassan
- **المنطقة:** Los Angeles County
- **المدن:** Long Beach, Torrance, Carson, Lakewood
- **الرموز البريدية:** 90, 90501, 90502, 90805
- **السيارة:** Truck
- **نقطة البداية:** Long Beach Office

### 3. Ali Mansour
- **المنطقة:** San Diego County
- **المدن:** San Diego, Chula Vista, El Cajon
- **الرموز البريدية:** 92, 91910, 91911
- **السيارة:** Van
- **نقطة البداية:** San Diego Office

---

## ⚠️ إذا شغلت السكريبت مرة ثانية:

السكريبت **ذكي**! راح:
- ✅ يتخطى الأوراق الموجودة
- ✅ ما يضيف سائقين مرتين
- ✅ فقط يصلح أي مشاكل موجودة

---

## 🔧 إذا حصلت مشكلة:

### المشكلة: `credentials.json not found`
**الحل:** 
```bash
# تأكد أن الملف موجود
ls credentials.json
```

### المشكلة: `GOOGLE_SHEET_ID not found`
**الحل:**
```bash
# تأكد أن .env موجود
cat .env
# يجب أن يحتوي على:
# GOOGLE_SHEET_ID=1mwSH2hFmggSjxBnkqbIZARylMd_3fXtrF2M0pTgrJe0
```

### المشكلة: `Failed to connect`
**الحل:**
1. أول مرة؟ راح يفتح لك صفحة للمصادقة
2. سجل دخول بحسابك
3. اسمح بالوصول
4. شغل السكريبت مرة ثانية

---

## ✅ بعد التشغيل الناجح:

```bash
# تحقق من كل شيء
python verify_setup.py

# شغل التطبيق
streamlit run app.py
```

---

## 🆚 الفرق بين السكريبتين:

| السكريبت | الوظيفة |
|----------|---------|
| `setup_google_sheet.py` | **يعدّل** Google Sheet ويضيف كل شيء |
| `verify_setup.py` | **يتحقق** فقط من الإعداد (ما يعدّل شيء) |

---

## 📞 محتاج مساعدة؟

- شغل: `python verify_setup.py` للتحقق
- راجع: `GOOGLE_SHEET_SETUP_AR.md` للتفاصيل
- اتصل: 760-879-1071

---

**الخلاصة:** بدل ما تنسخ والصق يدوي، شغل `setup_google_sheet.py` وخليه يعمل كل شيء! 🚀
