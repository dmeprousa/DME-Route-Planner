"""
Automatic Google Sheet Setup Script
سكريبت إعداد Google Sheet التلقائي

This script will automatically set up your Google Sheet with:
- Create/verify ORDERS, ROUTES, DRIVERS tabs
- Add correct headers to each tab
- Add sample driver data
- Verify everything is correct

يقوم هذا السكريبت بإعداد Google Sheet تلقائياً:
- إنشاء/التحقق من أوراق ORDERS, ROUTES, DRIVERS
- إضافة العناوين الصحيحة لكل ورقة
- إضافة بيانات تجريبية للسائقين
- التحقق من صحة كل شيء
"""

import os
from dotenv import load_dotenv
from components.database import Database

# Load environment
load_dotenv()

print("=" * 70)
print("🚀 DME Route Planner - Automatic Google Sheet Setup")
print("   إعداد Google Sheet التلقائي")
print("=" * 70)
print()

# Step 1: Connect to Google Sheets
print("Step 1: Connecting to Google Sheets...")
print("الخطوة 1: الاتصال بـ Google Sheets...")

try:
    db = Database()
    print("✅ Connected successfully!")
    print("✅ تم الاتصال بنجاح!")
    print()
except Exception as e:
    print(f"❌ Failed to connect: {str(e)}")
    print("❌ فشل الاتصال")
    print()
    print("Make sure:")
    print("1. credentials.json exists")
    print("2. You have authenticated (run once to get OAuth)")
    print("3. Google Sheets API is enabled")
    exit(1)

# Define required structure
REQUIRED_TABS = {
    'ORDERS': [
        'order_id', 'date', 'created_at', 'status', 'order_type', 
        'customer_name', 'customer_phone', 'address', 'city', 'zip_code', 
        'items', 'time_window_start', 'time_window_end', 'special_notes', 
        'assigned_driver', 'route_id', 'stop_number', 'eta', 'updated_at'
    ],
    'ROUTES': [
        'route_id', 'date', 'driver_name', 'start_location', 'total_stops', 
        'total_distance_miles', 'total_drive_time_min', 'estimated_finish', 
        'route_status', 'sent_at', 'created_at'
    ],
    'DRIVERS': [
        'driver_id', 'driver_name', 'phone', 'email', 'status', 
        'primary_areas', 'cities_covered', 'zip_prefixes', 'vehicle_type', 
        'start_location', 'notes', 'created_at', 'updated_at'
    ]
}

# Sample driver data
SAMPLE_DRIVERS = [
    {
        'driver_id': 'DRV-001',
        'driver_name': 'Ahmed Ali',
        'phone': '760-879-1071',
        'email': 'ahmed@hospiceprodme.com',
        'status': 'active',
        'primary_areas': 'Orange County',
        'cities_covered': 'Irvine, Anaheim, Santa Ana, Garden Grove',
        'zip_prefixes': '92, 92806, 92807',
        'vehicle_type': 'Van',
        'start_location': 'Irvine Office',
        'notes': 'Available weekdays 8 AM - 5 PM',
        'created_at': '2024-12-13',
        'updated_at': '2024-12-13'
    },
    {
        'driver_id': 'DRV-002',
        'driver_name': 'Mohammed Hassan',
        'phone': '760-555-5678',
        'email': 'mohammed@hospiceprodme.com',
        'status': 'active',
        'primary_areas': 'Los Angeles County',
        'cities_covered': 'Long Beach, Torrance, Carson, Lakewood',
        'zip_prefixes': '90, 90501, 90502, 90805',
        'vehicle_type': 'Truck',
        'start_location': 'Long Beach Office',
        'notes': 'Available weekdays and Saturdays',
        'created_at': '2024-12-13',
        'updated_at': '2024-12-13'
    },
    {
        'driver_id': 'DRV-003',
        'driver_name': 'Ali Mansour',
        'phone': '760-555-9012',
        'email': 'ali@hospiceprodme.com',
        'status': 'active',
        'primary_areas': 'San Diego County',
        'cities_covered': 'San Diego, Chula Vista, El Cajon',
        'zip_prefixes': '92, 91910, 91911',
        'vehicle_type': 'Van',
        'start_location': 'San Diego Office',
        'notes': 'Bilingual (English/Arabic)',
        'created_at': '2024-12-13',
        'updated_at': '2024-12-13'
    }
]

# Step 2: Get existing worksheets
print("Step 2: Checking existing worksheets...")
print("الخطوة 2: فحص الأوراق الموجودة...")
print()

existing_sheets = [ws.title for ws in db.spreadsheet.worksheets()]
print(f"Existing sheets: {', '.join(existing_sheets)}")
print(f"الأوراق الموجودة: {', '.join(existing_sheets)}")
print()

# Step 3: Create missing worksheets
print("Step 3: Creating/verifying required worksheets...")
print("الخطوة 3: إنشاء/التحقق من الأوراق المطلوبة...")
print()

for tab_name in REQUIRED_TABS.keys():
    if tab_name not in existing_sheets:
        print(f"Creating worksheet: {tab_name}...")
        print(f"إنشاء ورقة: {tab_name}...")
        db.spreadsheet.add_worksheet(title=tab_name, rows=1000, cols=20)
        print(f"✅ Created {tab_name}")
    else:
        print(f"✅ {tab_name} already exists")

print()

# Step 4: Set up headers for each worksheet
print("Step 4: Setting up headers...")
print("الخطوة 4: إعداد العناوين...")
print()

for tab_name, headers in REQUIRED_TABS.items():
    print(f"Setting up {tab_name}...")
    
    try:
        ws = db.spreadsheet.worksheet(tab_name)
        
        # Check if headers already exist
        existing_headers = ws.row_values(1)
        
        if existing_headers == headers:
            print(f"✅ {tab_name}: Headers already correct")
        else:
            # Clear first row and set headers
            ws.clear()
            ws.insert_row(headers, 1)
            print(f"✅ {tab_name}: Headers set ({len(headers)} columns)")
            
    except Exception as e:
        print(f"❌ Error setting up {tab_name}: {str(e)}")

print()

# Step 5: Add sample drivers (only if DRIVERS sheet is empty)
print("Step 5: Adding sample driver data...")
print("الخطوة 5: إضافة بيانات تجريبية للسائقين...")
print()

try:
    ws = db.spreadsheet.worksheet('DRIVERS')
    existing_data = ws.get_all_values()
    
    # Check if there's data beyond headers
    if len(existing_data) <= 1:
        print("No drivers found. Adding sample drivers...")
        print("لا يوجد سائقين. جاري إضافة سائقين تجريبيين...")
        
        for driver in SAMPLE_DRIVERS:
            row = [driver.get(header, '') for header in REQUIRED_TABS['DRIVERS']]
            ws.append_row(row)
            print(f"✅ Added driver: {driver['driver_name']}")
        
        print()
        print(f"✅ Added {len(SAMPLE_DRIVERS)} sample drivers")
        print(f"✅ تمت إضافة {len(SAMPLE_DRIVERS)} سائقين تجريبيين")
    else:
        print(f"✅ DRIVERS sheet already has data ({len(existing_data)-1} drivers)")
        print(f"✅ ورقة DRIVERS تحتوي على بيانات ({len(existing_data)-1} سائقين)")
    
except Exception as e:
    print(f"❌ Error adding drivers: {str(e)}")

print()

# Step 6: Verify setup
print("Step 6: Verifying setup...")
print("الخطوة 6: التحقق من الإعداد...")
print()

all_good = True

for tab_name, headers in REQUIRED_TABS.items():
    try:
        ws = db.spreadsheet.worksheet(tab_name)
        actual_headers = ws.row_values(1)
        
        if actual_headers == headers:
            print(f"✅ {tab_name}: {len(headers)} columns - Perfect!")
        else:
            print(f"⚠️  {tab_name}: Headers mismatch")
            all_good = False
            
    except Exception as e:
        print(f"❌ {tab_name}: Error - {str(e)}")
        all_good = False

print()

# Check drivers
try:
    drivers = db.get_drivers(status='')
    print(f"✅ Found {len(drivers)} drivers in database")
    print(f"✅ تم العثور على {len(drivers)} سائقين")
    
    if len(drivers) > 0:
        print()
        print("Driver list:")
        print("قائمة السائقين:")
        for driver in drivers:
            print(f"  - {driver['driver_name']} ({driver['status']}) - {driver['primary_areas']}")
    
except Exception as e:
    print(f"❌ Error reading drivers: {str(e)}")
    all_good = False

print()
print("=" * 70)

if all_good:
    print("✅ ✅ ✅ SETUP COMPLETE! ALL SYSTEMS GO! ✅ ✅ ✅")
    print("✅ ✅ ✅ اكتمل الإعداد! كل شيء جاهز! ✅ ✅ ✅")
    print()
    print("Your Google Sheet is ready to use!")
    print("Google Sheet جاهز للاستخدام!")
    print()
    print("Next steps:")
    print("1. Run: streamlit run app.py")
    print("2. Start adding orders!")
    print()
    print("الخطوات التالية:")
    print("1. شغل: streamlit run app.py")
    print("2. ابدأ بإضافة الطلبات!")
else:
    print("⚠️  SETUP COMPLETED WITH WARNINGS")
    print("⚠️  اكتمل الإعداد مع تحذيرات")
    print()
    print("Please review the warnings above and fix any issues.")
    print("راجع التحذيرات أعلاه وصلح أي مشاكل.")

print("=" * 70)
print()
print(f"🔗 Google Sheet URL:")
print(f"   https://docs.google.com/spreadsheets/d/{os.getenv('GOOGLE_SHEET_ID')}/edit")
