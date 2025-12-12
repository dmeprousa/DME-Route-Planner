"""
Google Sheet Verification Script
تحقق من إعداد Google Sheet

Run this to verify your Google Sheet is set up correctly.
شغل هذا السكريبت للتحقق من إعداد Google Sheet
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("🔍 DME Route Planner - Google Sheet Verification")
print("   تحقق من إعداد Google Sheet")
print("=" * 60)
print()

# Step 1: Check environment variables
print("1️⃣ Checking environment variables...")
print("   فحص متغيرات البيئة...")

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')

if GEMINI_API_KEY:
    print("   ✅ GEMINI_API_KEY found")
else:
    print("   ❌ GEMINI_API_KEY not found in .env file")

if GOOGLE_SHEET_ID:
    print(f"   ✅ GOOGLE_SHEET_ID: {GOOGLE_SHEET_ID}")
else:
    print("   ❌ GOOGLE_SHEET_ID not found in .env file")

print()

# Step 2: Check credentials file
print("2️⃣ Checking credentials.json...")
print("   فحص ملف credentials.json...")

if os.path.exists('credentials.json'):
    print("   ✅ credentials.json found")
    with open('credentials.json', 'r') as f:
        content = f.read()
        if len(content) > 100:
            print("   ✅ File appears to have valid content")
        else:
            print("   ⚠️  File seems too small, verify content")
else:
    print("   ❌ credentials.json not found")
    print("      Download from Google Cloud Console")

print()

# Step 3: Try connecting to Google Sheets
print("3️⃣ Attempting to connect to Google Sheets...")
print("   محاولة الاتصال بـ Google Sheets...")

try:
    from components.database import Database
    
    print("   🔄 Initializing database connection...")
    db = Database()
    print("   ✅ Successfully connected to Google Sheets!")
    print()
    
    # Step 4: Check worksheets
    print("4️⃣ Checking worksheets...")
    print("   فحص الأوراق...")
    
    required_sheets = ['ORDERS', 'ROUTES', 'DRIVERS']
    available_sheets = [ws.title for ws in db.spreadsheet.worksheets()]
    
    print(f"   Available sheets: {', '.join(available_sheets)}")
    print()
    
    for sheet_name in required_sheets:
        if sheet_name in available_sheets:
            print(f"   ✅ {sheet_name} sheet found")
        else:
            print(f"   ❌ {sheet_name} sheet NOT found")
            print(f"      Create a sheet named exactly '{sheet_name}'")
    
    print()
    
    # Step 5: Check DRIVERS sheet structure
    print("5️⃣ Checking DRIVERS sheet structure...")
    print("   فحص هيكل ورقة DRIVERS...")
    
    try:
        ws = db.spreadsheet.worksheet('DRIVERS')
        headers = ws.row_values(1)
        
        required_headers = [
            'driver_id', 'driver_name', 'phone', 'email', 'status',
            'primary_areas', 'cities_covered', 'zip_prefixes', 
            'vehicle_type', 'start_location', 'notes', 
            'created_at', 'updated_at'
        ]
        
        print(f"   Found {len(headers)} columns")
        print(f"   Required: {len(required_headers)} columns")
        
        if len(headers) == len(required_headers):
            print("   ✅ Correct number of columns")
        else:
            print(f"   ❌ Wrong number of columns")
            print(f"      Expected {len(required_headers)}, found {len(headers)}")
        
        print()
        print("   Checking column names:")
        for i, req_header in enumerate(required_headers):
            if i < len(headers) and headers[i] == req_header:
                print(f"   ✅ Column {i+1}: {req_header}")
            else:
                actual = headers[i] if i < len(headers) else "(missing)"
                print(f"   ❌ Column {i+1}: Expected '{req_header}', found '{actual}'")
        
        print()
        
        # Check for drivers
        drivers = db.get_drivers(status='')
        print(f"   Found {len(drivers)} drivers in database")
        
        if len(drivers) > 0:
            print("   ✅ At least one driver found")
            print()
            print("   Driver list:")
            for driver in drivers:
                print(f"   - {driver.get('driver_name')} ({driver.get('status')})")
        else:
            print("   ⚠️  No drivers found")
            print("      Add at least one driver to DRIVERS sheet")
        
    except Exception as e:
        print(f"   ❌ Error checking DRIVERS: {str(e)}")
    
    print()
    
    # Step 6: Check ORDERS sheet structure
    print("6️⃣ Checking ORDERS sheet structure...")
    print("   فحص هيكل ورقة ORDERS...")
    
    try:
        ws = db.spreadsheet.worksheet('ORDERS')
        headers = ws.row_values(1)
        
        required_count = 19
        
        if len(headers) == required_count:
            print(f"   ✅ Correct number of columns ({required_count})")
        else:
            print(f"   ❌ Wrong number of columns")
            print(f"      Expected {required_count}, found {len(headers)}")
        
        # Check first and last column
        if len(headers) > 0:
            if headers[0] == 'order_id':
                print(f"   ✅ First column: order_id")
            else:
                print(f"   ❌ First column should be 'order_id', found '{headers[0]}'")
        
        if len(headers) >= required_count:
            if headers[required_count-1] == 'updated_at':
                print(f"   ✅ Last column: updated_at")
            else:
                print(f"   ❌ Last column should be 'updated_at', found '{headers[required_count-1]}'")
        
    except Exception as e:
        print(f"   ❌ Error checking ORDERS: {str(e)}")
    
    print()
    
    # Step 7: Check ROUTES sheet structure
    print("7️⃣ Checking ROUTES sheet structure...")
    print("   فحص هيكل ورقة ROUTES...")
    
    try:
        ws = db.spreadsheet.worksheet('ROUTES')
        headers = ws.row_values(1)
        
        required_count = 11
        
        if len(headers) == required_count:
            print(f"   ✅ Correct number of columns ({required_count})")
        else:
            print(f"   ❌ Wrong number of columns")
            print(f"      Expected {required_count}, found {len(headers)}")
        
        # Check first and last column
        if len(headers) > 0:
            if headers[0] == 'route_id':
                print(f"   ✅ First column: route_id")
            else:
                print(f"   ❌ First column should be 'route_id', found '{headers[0]}'")
        
        if len(headers) >= required_count:
            if headers[required_count-1] == 'created_at':
                print(f"   ✅ Last column: created_at")
            else:
                print(f"   ❌ Last column should be 'created_at', found '{headers[required_count-1]}'")
        
    except Exception as e:
        print(f"   ❌ Error checking ROUTES: {str(e)}")

except Exception as e:
    print(f"   ❌ Failed to connect: {str(e)}")
    print()
    print("   Common issues:")
    print("   - credentials.json is missing or invalid")
    print("   - First time? You need to authenticate")
    print("   - Check that Google Sheets API is enabled")

print()
print("=" * 60)
print("✅ Verification Complete!")
print("   اكتمل التحقق!")
print("=" * 60)
print()
print("Next steps:")
print("1. Fix any ❌ errors shown above")
print("2. Make sure DRIVERS sheet has at least one driver")
print("3. Run: streamlit run app.py")
print()
print("الخطوات التالية:")
print("1. صلح أي أخطاء ❌ ظاهرة أعلاه")
print("2. تأكد من أن ورقة DRIVERS فيها سائق واحد على الأقل")
print("3. شغل: streamlit run app.py")
