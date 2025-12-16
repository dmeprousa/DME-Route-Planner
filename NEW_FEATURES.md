# 🎯 NEW FEATURES & WORKFLOW UPDATES

## تحديث: 16 ديسمبر 2025

---

## ✨ الميزات الجديدة (New Features)

### 1️⃣ **Image AI Parsing** 📸
**الوصف**: رفع صور الأوردرات والنظام يقراها أوتوماتيك  
**الاستخدام**:
- اذهب إلى صفحة "Input Orders"
- اختر Tab "📸 Upload Image"
- ارفع صورة (screenshot, فاكس, صورة موبايل)
- اضغط "Parse Image with AI"
- النظام هيستخرج العناوين والتفاصيل تلقائياً

**التقنية**: Google Gemini Vision API

---

### 2️⃣ **Multi-Device Sync** 📱💻
**الوصف**: بياناتك محفوظة في Google Sheets - شغلك يظهر على أي جهاز

**كيف يعمل؟**
- كل أوردر تضيفه يتحفظ فوراً في Google Sheet
- Sheet جديد اسمه `PENDING_ORDERS`
- لو فتحت من الموبايل أو جهاز تاني، هتلاقي نفس الأوردرات

**الفايدة**:
- Sofia ممكن تضيف أوردرات من المكتب
- Cyrus يشوفها ويوزعها من الموبايل
- كل حد يشوف شغل الآخر Live

---

### 3️⃣ **Selective Routing** ✅
**الوصف**: اختار العناوين اللي عايز توزعها بس

**الطريقة**:
1. في صفحة "Input Orders"، هتلاقي جدول بكل الأوردرات
2. كل أوردر فيه **Checkbox**
3. حدد العناوين اللي عايز توزعها دلوقتي
4. اضغط **"✈️ Send Selected to Routes"**
5. بس العناوين المحددة تروح للـ Drivers

**اللوجيك**:
- لو معملتش select لحاجة، كل الأوردرات هتروح (Fallback)
- لو حددت 4 من 10، بس الـ 4 هيروحوا
- الباقي يفضل في "Pending"

---

### 4️⃣ **Incremental Planning** 🔄
**الوصف**: ضيف أوردرات جديدة من غير ما تأثر على اللي قبلها

**السيناريو**:
1. الصبح: ضفت 4 عناوين ووزعتهم على Driver A و Driver B
2. الضهر: جالك 3 عناوين جداد
3. بدل ما تعيد التوزيع كله، حدد الـ 3 الجداد بس
4. وزعهم على Driver C أو أضفهم لـ A/B

**النتيجة**: شغل سلس، مفيش confusion

---

## 📊 **الهيكل الجديد (New Structure)**

### Google Sheets Tabs:

| Tab Name | Purpose | Who Uses It |
|----------|---------|-------------|
| `PENDING_ORDERS` | العناوين المنتظرة (لسه ماتوزعتش) | User adds orders here |
| `ORDERS` | كل الأوردرات (حتى اللي اتوزعت) | System tracks history |
| `ROUTES` | الروتات السابقة | History & Analytics |
| `DRIVERS` | بيانات السائقين | System reads driver info |

---

## 🔄 **الـ Workflow الجديد (New Workflow)**

### الطريقة القديمة:
```
1. Add Orders → 2. Select Drivers → 3. Optimize → 4. Done
(كل الأوردرات بتروح مرة واحدة)
```

### الطريقة الجديدة ⭐:
```
1. Add Orders (Text/File/Image) 
   ↓
2. Orders saved to PENDING_ORDERS (Google Sheets)
   ↓
3. Select which orders to route (Checkbox)
   ↓
4. Send Selected → Select Drivers → Optimize
   ↓
5. Unselected orders remain in Pending
   ↓
6. Add more orders later → Repeat from step 3
```

---

## 🎨 **التحسينات (Improvements)**

### ✅ **Before (قبل)**:
- الداتا بتضيع لو عملت Refresh
- لازم توزع كل الأوردرات مرة واحدة
- مفيش Image Support
- مفيش Sync بين الأجهزة

### ✨ **After (بعد)**:
- ✅ الداتا محفوظة في Cloud (Google Sheets)
- ✅ توزيع تدريجي (Incremental)
- ✅ رفع صور وقراءتها بالAI
- ✅ Multi-device sync

---

## 🔐 **User Isolation**

كل User عنده داتاه الخاصة:
- Sofia's pending orders ≠ Cyrus's pending orders
- الـ Username بيتسجل مع كل Order
- في `PENDING_ORDERS`، فيه عمود `username`

---

## 🚀استخدام الميزات الجديدة (Usage Guide)**

### 📸 **Example: رفع صورة وتوزيعها**

```
1. Sofia بتصور فاتورة من الفاكس
2. بتفتح التطبيق → Input Orders → Tab "Upload Image"
3. بترفع الصورة
4. AI بيقراها ويطلع 3 عناوين
5. Sofia بتحدد (✅) أول عنوانين بس
6. بتضغط "Send Selected (2) to Routes"
7. بتوزعهم على Driver Ahmed
8. العنوان الثالث يفضل في Pending لبكره
```

---

## 📂 **الملفات الجديدة (New Files)**

| File | Purpose |
|------|---------|
| `utils/sheets_manager.py` | إدارة الاتصال بـ Google Sheets |
| `requirements.txt` | أضفنا `Pillow` لقراءة الصور |
| `components/order_input.py` | أضفنا دالة `parse_image()` |

---

## ⚙️ **Setup Requirements**

### Google Sheets:
تأكد إن عندك Tab اسمه `PENDING_ORDERS` في الشيت بتاعك:

**Columns**:
```
username | added_at | selected | order_type | customer_name | customer_phone | address | city | zip_code | items | time_window_start | time_window_end | special_notes
```

(النظام هيعملها أوتوماتيك لو مش موجودة)

### Environment Variables:
في `.env` أو Streamlit Secrets:
```toml
GEMINI_API_KEY = "your-google-gemini-api-key"
GOOGLE_SHEETS_CREDENTIALS = {...}
```

---

## 🐛 **Troubleshooting**

### Problem: الصور مش بتتقرا
**Solution**: تأكد إن `GEMINI_API_KEY` موجود وصحيح

### Problem: الداتا مش بتتحفظ
**Solution**: تأكد إن Google Sheets credentials صحيحة

### Problem: الـ Selected Orders مش رايحة للـ Drivers
**Solution**: تأكد إنك ضاغط "Send Selected" مش "Next"

---

## 🎯 **Next Steps** (الخطوات القادمة)

### المتبقي (To-Do):
- [ ] Route History Dashboard (تحليلات أفضل)
- [ ] WhatsApp Auto-Send for images
- [ ] Driver Mobile App (Optional)
- [ ] Real-time GPS tracking

---

## 📞 **Support**

إذا كان فيه أي مشكلة:
1. شوف الـ Logs في Streamlit Cloud
2. تأكد من الـ Secrets
3. تأكد إن Google Sheet structure صحيح

---

**Last Updated**: December 16, 2025  
**Version**: 2.1 (Image AI + Sync)
