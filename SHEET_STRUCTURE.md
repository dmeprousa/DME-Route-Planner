# 📊 Google Sheet Structure - هيكل Google Sheet

## 🔗 Your Sheet
**ID:** `1mwSH2hFmggSjxBnkqbIZARylMd_3fXtrF2M0pTgrJe0`

---

## 📋 Required Tabs (يجب إنشاء 3 أوراق بالضبط)

### 1️⃣ ORDERS (19 columns)
```
order_id | date | created_at | status | order_type | customer_name | customer_phone | address | city | zip_code | items | time_window_start | time_window_end | special_notes | assigned_driver | route_id | stop_number | eta | updated_at
```

### 2️⃣ ROUTES (11 columns)
```
route_id | date | driver_name | start_location | total_stops | total_distance_miles | total_drive_time_min | estimated_finish | route_status | sent_at | created_at
```

### 3️⃣ DRIVERS (13 columns)
```
driver_id | driver_name | phone | email | status | primary_areas | cities_covered | zip_prefixes | vehicle_type | start_location | notes | created_at | updated_at
```

---

## ⚠️ Important Notes

1. **Tab names must be EXACT:** `ORDERS`, `ROUTES`, `DRIVERS` (all caps)
2. **Headers in row 1** (first row)
3. **Data starts from row 2**
4. **Add at least 1 driver** in DRIVERS tab to start

---

## 📝 Sample Driver (نموذج سائق)

```
DRV-001 | Ahmed Ali | 760-879-1071 | ahmed@example.com | active | Orange County | Irvine, Anaheim | 92, 90 | Van | Irvine Office | Available weekdays | 2024-12-13 | 2024-12-13
```

---

## 🚀 After Setup

Once your Google Sheet is ready with the 3 tabs and correct headers:

```bash
streamlit run app.py
```

That's it! The app will read from and write to your Google Sheet automatically.

---

**Need help?** Check `SETUP.md` for full setup instructions.
