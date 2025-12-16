"""
Page 2: Select Drivers (Updated)
Simply select drivers from a dropdown and configure their start details. (Auto-Saves)
"""

import sys
import os
# Add project root to path for proper imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
from components.database import Database
from components.session_manager import SessionManager
from components.user_session import UserSession

st.set_page_config(page_title="Select Drivers", page_icon="👥", layout="wide")

# Require authentication
UserSession.require_auth()

st.title("👥 Select Drivers")

# Check if we have orders to route
if 'orders_for_routing' in st.session_state and st.session_state.orders_for_routing:
    orders_count = len(st.session_state.orders_for_routing)
    st.success(f"🚚 Ready to assign {orders_count} orders to drivers")
elif 'orders' in st.session_state and st.session_state.orders:
    # Fallback to all orders if no specific selection
    st.session_state.orders_for_routing = st.session_state.orders
    orders_count = len(st.session_state.orders)
    st.info(f"📦 Using all {orders_count} orders")
else:
    st.warning("⚠️ No orders to route. Please add orders first.")
    if st.button("📦 Go to Input Orders"):
        st.switch_page("pages/1_📦_Input_Orders.py")
    st.stop()

st.divider()

# Initialize session state if clean start
if 'selected_drivers' not in st.session_state:
    st.session_state.selected_drivers = []
if 'driver_config' not in st.session_state:
    st.session_state.driver_config = {}

# Load drivers
try:
    db = Database()
    all_drivers = db.get_drivers(status='active')
except Exception as e:
    st.error(f"Error loading drivers: {str(e)}")
    all_drivers = []

if all_drivers:
    # 1. Driver Selection (Dropdown)
    driver_names = [d.get('driver_name') for d in all_drivers]
    
    # Pre-select based on session state
    current_selected_names = [d.get('driver_name') for d in st.session_state.selected_drivers]
    
    selected_names = st.multiselect(
        "Who is driving today?",
        options=driver_names,
        default=current_selected_names,
        placeholder="Select drivers..."
    )
    
    # Update logic
    current_selection = [d for d in all_drivers if d.get('driver_name') in selected_names]
    st.session_state.selected_drivers = current_selection
    
    # Save State Immediately
    if len(current_selection) != len(current_selected_names):
        SessionManager.save_state()

    # 2. Configuration with Current Location Support
    if current_selection:
        st.subheader("⚙️ Driver Configuration")
        st.caption("Configure start time and location for each driver")
        
        # Process each driver individually for better UX
        for d in current_selection:
            d_id = d.get('driver_id', '')
            d_name = d.get('driver_name')
            existing_conf = st.session_state.driver_config.get(d_id, {})
            
            with st.expander(f"🚚 {d_name}", expanded=True):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    start_time = st.text_input(
                        "Start Time",
                        value=existing_conf.get('start_time', '09:00 AM'),
                        key=f"time_{d_id}"
                    )
                    
                    vehicle = d.get('vehicle_type', 'Van')
                    st.info(f"🚐 Vehicle: {vehicle}")
                
                with col2:
                    # Current Location Feature
                    location_type = st.radio(
                        "Starting from:",
                        options=["Office", "Current Location"],
                        index=0 if existing_conf.get('location_type', 'Office') == 'Office' else 1,
                        key=f"loc_type_{d_id}",
                        horizontal=True
                    )
                    
                    if location_type == "Office":
                        start_location = d.get('start_location', 'Office')
                        st.info(f"🏢 Office: {start_location}")
                        current_address = None
                    else:
                        current_address = st.text_input(
                            "📍 Current Address (where driver is now)",
                            value=existing_conf.get('current_address', ''),
                            placeholder="123 Main St, City, CA 90001",
                            key=f"curr_addr_{d_id}"
                        )
                        start_location = current_address if current_address else d.get('start_location', 'Office')
                        
                        if current_address:
                            st.success(f"✅ Will route from: {current_address}")
                        else:
                            st.warning("⚠️ Enter current address or it will default to office")
                
                # Save to config
                st.session_state.driver_config[d_id] = {
                    'start_time': start_time,
                    'start_location': start_location,
                    'location_type': location_type,
                    'current_address': current_address,
                    'office_location': d.get('start_location', 'Office')
                }
        
        # Save state
        SessionManager.save_state()

        st.divider()
        
        # Navigation
        col1, col2 = st.columns([1, 4])
        with col1:
             if st.button("🤖 Optimize Routes →", type="primary", use_container_width=True):
                st.switch_page("pages/3_🤖_Optimize_Routes.py")

else:
    st.warning("No active drivers found. Please add drivers in the database.")

st.divider()

# Quick Add Driver
with st.expander("➕ Add New Driver to Database"):
    with st.form("quick_add_driver"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Name")
        with c2:
            phone = st.text_input("Phone")
        
        if st.form_submit_button("Add Driver"):
            if name:
                try:
                    db = Database()
                    db.add_driver({'driver_name': name, 'phone': phone, 'status': 'active'})
                    st.success(f"Added {name}! Refresh to see in list.")
                except Exception as e:
                    st.error(str(e))

# Show user info at the bottom of the sidebar
UserSession.show_user_info_sidebar()
