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

    # 2. Configuration (Clean Data Editor)
    if current_selection:
        st.subheader("⚙️ Configuration")
        
        # Prepare data for editor
        config_data = []
        for d in current_selection:
            d_id = d.get('driver_id', '')
            # Get existing config or default
            existing_conf = st.session_state.driver_config.get(d_id, {})
            
            config_data.append({
                "Driver Name": d.get('driver_name'),
                "ID": d_id,
                "Start Time": existing_conf.get('start_time', '09:00 AM'),
                "Start Location": existing_conf.get('start_location', d.get('start_location', 'Office')),
                "Vehicle": d.get('vehicle_type', 'Van')
            })
        
        # Display editable table
        edited_df = st.data_editor(
            pd.DataFrame(config_data),
            column_config={
                "ID": st.column_config.TextColumn(disabled=True),
                "Driver Name": st.column_config.TextColumn(disabled=True),
                "Vehicle": st.column_config.TextColumn(disabled=True),
                "Start Time": st.column_config.TextColumn(required=True),
                "Start Location": st.column_config.TextColumn(required=True),
            },
            hide_index=True,
            use_container_width=True,
            key="driver_editor"
        )
        
        # Update session state from editor & Save
        changes_detected = False
        for index, row in edited_df.iterrows():
            d_id = row['ID']
            if d_id:
                new_conf = {
                    'start_time': row['Start Time'],
                    'start_location': row['Start Location']
                }
                if st.session_state.driver_config.get(d_id) != new_conf:
                    st.session_state.driver_config[d_id] = new_conf
                    changes_detected = True
        
        if changes_detected:
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
