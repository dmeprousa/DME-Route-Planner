"""
Page 2: Select Drivers
Choose available drivers and configure start time/location
"""

import streamlit as st
from components.database import Database
from components.driver_manager import DriverManager

st.set_page_config(page_title="Select Drivers", page_icon="👥", layout="wide")

st.title("👥 Select Drivers")
st.caption("Choose who's working today and configure their routes")

# Initialize session state
if 'selected_drivers' not in st.session_state:
    st.session_state.selected_drivers = []
if 'driver_config' not in st.session_state:
    st.session_state.driver_config = {}

# Load drivers from database
try:
    with st.spinner("Loading drivers..."):
        db = Database()
        all_drivers = db.get_drivers(status='active')
    
    st.success(f"✅ Loaded {len(all_drivers)} active drivers from database")
    
except Exception as e:
    st.error(f"Error loading drivers: {str(e)}")
    st.info("Make sure you have credentials.json and .env configured correctly")
    all_drivers = []

st.divider()

if all_drivers:
    # Driver selection
    st.subheader("📋 Available Drivers")
    
    selected_driver_ids = []
    
    # Create grid layout
    cols = st.columns(3)
    
    for i, driver in enumerate(all_drivers):
        with cols[i % 3]:
            driver_id = driver.get('driver_id')
            driver_name = driver.get('driver_name', 'Unknown')
            primary_areas = driver.get('primary_areas', 'N/A')
            cities = driver.get('cities_covered', 'N/A')
            
            # Checkbox for selection
            is_selected = st.checkbox(
                f"**{driver_name}**",
                key=f"driver_{driver_id}",
                value=driver_id in [d.get('driver_id') for d in st.session_state.selected_drivers]
            )
            
            if is_selected:
                selected_driver_ids.append(driver_id)
                
                st.caption(f"📍 {primary_areas}")
                st.caption(f"🏙️ {cities}")
                
                # Configuration
                with st.expander("⚙️ Configure"):
                    start_time = st.text_input(
                        "Start Time",
                        value=st.session_state.driver_config.get(driver_id, {}).get('start_time', '09:00 AM'),
                        key=f"time_{driver_id}"
                    )
                    start_location = st.text_input(
                        "Start Location",
                        value=st.session_state.driver_config.get(driver_id, {}).get('start_location', driver.get('start_location', 'Office')),
                        key=f"loc_{driver_id}"
                    )
                    
                    # Update config
                    if driver_id not in st.session_state.driver_config:
                        st.session_state.driver_config[driver_id] = {}
                    st.session_state.driver_config[driver_id]['start_time'] = start_time
                    st.session_state.driver_config[driver_id]['start_location'] = start_location
    
    st.divider()
    
    # Update selected drivers
    st.session_state.selected_drivers = [d for d in all_drivers if d.get('driver_id') in selected_driver_ids]
    
    # Summary
    st.metric("Selected Drivers", len(st.session_state.selected_drivers))
    
    if st.session_state.selected_drivers:
        st.success(f"✅ Selected: {', '.join([d.get('driver_name') for d in st.session_state.selected_drivers])}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🤖 Next: Optimize Routes →", type="primary", use_container_width=True):
                st.switch_page("pages/3_🤖_Optimize_Routes.py")
        with col2:
            if st.button("📦 Back to Orders", use_container_width=True):
                st.switch_page("pages/1_📦_Input_Orders.py")
        with col3:
            if st.button("🏠 Home", use_container_width=True):
                st.switch_page("app.py")
    else:
        st.warning("⚠️ Please select at least one driver")

else:
    st.warning("No active drivers found in database")

st.divider()

# Add new driver section
with st.expander("➕ Add New Driver"):
    st.subheader("Add Driver to Database")
    
    with st.form("new_driver_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("Driver Name *")
            new_phone = st.text_input("Phone", placeholder="760-123-4567")
            new_email = st.text_input("Email")
            new_vehicle = st.selectbox("Vehicle Type", ["Van", "Truck", "SUV", "Car"])
            
        with col2:
            new_areas = st.text_input("Primary Areas", placeholder="Orange County, Long Beach")
            new_cities = st.text_input("Cities Covered", placeholder="Irvine, Anaheim, Garden Grove")
            new_zips = st.text_input("Zip Prefixes", placeholder="92, 90")
            new_start_loc = st.text_input("Default Start Location", placeholder="Office")
        
        new_notes = st.text_area("Notes (optional)")
        
        submitted = st.form_submit_button("➕ Add Driver", type="primary", use_container_width=True)
        
        if submitted:
            if new_name:
                try:
                    driver_data = {
                        'driver_name': new_name,
                        'phone': new_phone,
                        'email': new_email,
                        'status': 'active',
                        'primary_areas': new_areas,
                        'cities_covered': new_cities,
                        'zip_prefixes': new_zips,
                        'vehicle_type': new_vehicle,
                        'start_location': new_start_loc,
                        'notes': new_notes
                    }
                    
                    db = Database()
                    driver_id = db.add_driver(driver_data)
                    
                    st.success(f"✅ Added driver: {new_name} (ID: {driver_id})")
                    st.info("Refresh the page to see the new driver")
                    
                except Exception as e:
                    st.error(f"Error adding driver: {str(e)}")
            else:
                st.error("Driver name is required")

# Sidebar
with st.sidebar:
    st.header("💡 Tips")
    st.write("""
    **Driver Selection:**
    - Check drivers who are working today
    - Configure start time and location
    - AI will use coverage areas for smart assignment
    
    **Configuration:**
    - Start time: When driver begins work
    - Start location: Where they start from
    - These affect route optimization
    """)
    
    st.divider()
    
    st.header("📊 Session Info")
    st.write(f"Orders: {len(st.session_state.get('orders', []))}")
    st.write(f"Drivers: {len(st.session_state.selected_drivers)}")
