"""
Page 1: Input Orders
Parse orders from text, file upload, or manual entry
"""

import sys
import os
# Add project root to path for proper imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from datetime import date
from components.order_input import OrderInput
from components.user_session import UserSession
from utils.validators import validate_order
from utils.sheets_manager import SheetsManager
import pandas as pd

st.set_page_config(page_title="Input Orders", page_icon="📦", layout="wide")

# Require authentication
UserSession.require_auth()

st.title("📦 Input Orders")
st.caption("Add delivery/pickup orders for today")

# Initialize Sheets Manager
sheets = SheetsManager()

# Initialize session state and load from Google Sheets
if 'orders' not in st.session_state:
    # Load pending orders from Google Sheets
    current_user = UserSession.get_current_user()
    if current_user and sheets.spreadsheet:
        pending = sheets.load_pending_orders(current_user)
        st.session_state.orders = pending
    else:
        st.session_state.orders = []

# Show current count
st.metric("Orders Pending", len(st.session_state.orders))

st.divider()

# Input method tabs
# Input method tabs
tab1, tab2, tab_img, tab3 = st.tabs(["📝 Paste Text", "📄 Upload File", "📸 Upload Image", "✍️ Manual Entry"])

with tab1:
    st.subheader("Paste Order Text")
    st.write("Paste order information and AI will extract the details")
    
    text_input = st.text_area(
        "Paste orders here",
        height=200,
        placeholder="Example:\nDelivery to John Smith, 123 Main St, Long Beach, CA 90805\nItems: Hospital Bed, Oxygen Concentrator\nTime: 10 AM - 2 PM"
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🤖 Parse with AI", type="primary", use_container_width=True):
            if text_input:
                try:
                    with st.spinner("Parsing with AI..."):
                        parser = OrderInput()
                        parsed_orders = parser.parse_text(text_input)
                        
                        # Validate and add
                        added = 0
                        errors = []
                        for order in parsed_orders:
                            is_valid, msg = validate_order(order)
                            if is_valid:
                                st.session_state.orders.append(order)
                                added += 1
                            else:
                                errors.append(f"Invalid order: {msg}")
                        
                        if added > 0:
                            st.success(f"✅ Added {added} orders!")
                            # Save to Google Sheets
                            current_user = UserSession.get_current_user()
                            if current_user and sheets.spreadsheet:
                                sheets.save_pending_orders(st.session_state.orders, current_user)
                        if errors:
                            for error in errors:
                                st.warning(error)
                        
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error parsing text: {str(e)}")
            else:
                st.warning("Please paste some text first")

with tab2:
    st.subheader("Upload CSV or Excel File")
    st.write("File should contain columns: address, city, items, etc.")
    
    uploaded_file = st.file_uploader(
        "Choose file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload a CSV or Excel file with order data"
    )
    
    if uploaded_file:
        try:
            parser = OrderInput()
            parsed_orders = parser.parse_file(uploaded_file)
            
            st.write(f"Found {len(parsed_orders)} orders in file")
            st.dataframe(pd.DataFrame(parsed_orders), use_container_width=True)
            
            if st.button("✅ Add All Orders", type="primary"):
                added = 0
                errors = []
                for order in parsed_orders:
                    is_valid, msg = validate_order(order)
                    if is_valid:
                        st.session_state.orders.append(order)
                        added += 1
                    else:
                        errors.append(f"Row {added+1}: {msg}")
                
                if added > 0:
                    st.success(f"✅ Added {added} orders!")
                    # Save to Google Sheets
                    current_user = UserSession.get_current_user()
                    if current_user and sheets.spreadsheet:
                        sheets.save_pending_orders(st.session_state.orders, current_user)
                if errors:
                    with st.expander("⚠️ Validation Errors"):
                        for error in errors:
                            st.warning(error)
                
                st.rerun()
                
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

with tab_img:
    st.subheader("Upload Order Image")
    st.write("Upload a screenshot or photo of the order (e.g. from email or fax)")
    
    uploaded_image = st.file_uploader(
        "Choose image",
        type=['png', 'jpg', 'jpeg', 'webp'],
        key="img_uploader",
        help="Upload an image containing order details"
    )
    
    if uploaded_image:
        col_preview, col_action = st.columns([1, 2])
        with col_preview:
            st.image(uploaded_image, caption="Preview", width=200)
            
        with col_action:
            if st.button("🤖 Parse Image with AI", type="primary"):
                try:
                    with st.spinner("Analyzing image... (This relies on Gemini Vision)"):
                        parser = OrderInput()
                        parsed_orders = parser.parse_image(uploaded_image)
                        
                        # Validation & Adding
                        added = 0
                        errors = []
                        for order in parsed_orders:
                            is_valid, msg = validate_order(order)
                            if is_valid:
                                st.session_state.orders.append(order)
                                added += 1
                            else:
                                errors.append(f"Invalid in image: {msg}")
                        
                        if added > 0:
                            st.success(f"✅ Extracted {added} orders from image!")
                            # Save to Google Sheets
                            current_user = UserSession.get_current_user()
                            if current_user and sheets.spreadsheet:
                                sheets.save_pending_orders(st.session_state.orders, current_user)
                            st.balloons()
                            st.rerun()
                        
                        if errors:
                            for err in errors:
                                st.warning(err)
                                
                except Exception as e:
                    st.error(f"Error parsing image: {str(e)}")

with tab3:
    st.subheader("Manual Order Entry")
    
    with st.form("manual_order_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            order_type = st.selectbox("Order Type", ["Delivery", "Pickup", "Exchange"])
            customer_name = st.text_input("Customer Name")
            customer_phone = st.text_input("Phone (optional)", placeholder="760-123-4567")
            address = st.text_input("Street Address *", placeholder="123 Main St")
            
        with col2:
            city = st.text_input("City *", placeholder="Long Beach")
            zip_code = st.text_input("Zip Code", placeholder="90805")
            items = st.text_area("Items/Equipment *", placeholder="Hospital Bed, Oxygen Concentrator")
            special_notes = st.text_area("Special Notes (optional)", placeholder="Call before arrival")
        
        col1, col2 = st.columns(2)
        with col1:
            time_start = st.text_input("Time Window Start (optional)", placeholder="10:00 AM")
        with col2:
            time_end = st.text_input("Time Window End (optional)", placeholder="2:00 PM")
        
        submitted = st.form_submit_button("➕ Add Order", type="primary", use_container_width=True)
        
        if submitted:
            order = {
                'order_type': order_type,
                'customer_name': customer_name,
                'customer_phone': customer_phone,
                'address': address,
                'city': city,
                'zip_code': zip_code,
                'items': items,
                'time_window_start': time_start,
                'time_window_end': time_end,
                'special_notes': special_notes
            }
            
            is_valid, msg = validate_order(order)
            
            if is_valid:
                st.session_state.orders.append(order)
                # Save to Google Sheets
                current_user = UserSession.get_current_user()
                if current_user and sheets.spreadsheet:
                    sheets.save_pending_orders(st.session_state.orders, current_user)
                st.success("✅ Order added!")
                st.rerun()
            else:
                st.error(f"❌ {msg}")

st.divider()

# Display current orders
if st.session_state.orders:
    st.subheader("📋 Current Orders List")
    
    # Prepare DataFrame for Editor
    df = pd.DataFrame(st.session_state.orders)
    
    # Add 'Select' column for checkboxes
    if 'selected_rows' not in st.session_state:
        st.session_state.selected_rows = [False] * len(df)
        
    # Sync length if orders changed
    if len(st.session_state.selected_rows) != len(df):
        st.session_state.selected_rows = [False] * len(df)

    # Control for Select All
    col_a, col_b = st.columns([2, 10])
    with col_a:
        select_all = st.checkbox("Select All Orders")
    
    if select_all:
        df.insert(0, "Selected", True)
    else:
        # Use simple session state management or default to False
        df.insert(0, "Selected", False)

    # Interactive Data Editor
    edited_df = st.data_editor(
        df,
        column_config={
            "Selected": st.column_config.CheckboxColumn(
                "Select",
                help="Select order to delete",
                default=False,
            )
        },
        disabled=df.columns.drop("Selected"), # Disable editing other columns implies view-only except checkbox
        hide_index=True,
        use_container_width=True,
        key="order_editor" 
    )

    # Actions Bar
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        # Calculate selected count
        selected_indices = edited_df[edited_df["Selected"] == True].index.tolist()
        count = len(selected_indices)
        
        if count > 0:
            if st.button(f"🗑️ Delete Selected ({count})", type="primary", use_container_width=True):
                # Remove selected orders (reverse order to avoid index shift issues)
                for index in sorted(selected_indices, reverse=True):
                    del st.session_state.orders[index]
                st.success(f"Deleted {count} orders.")
                st.rerun()
        else:
            if st.button("🗑️ Clear All", use_container_width=True):
                 if st.button("Are you sure? Confirm Clear All"): # Nested button for safety check usually needs persistent state or simpler Confirm dialog
                     pass # Simple logic: just clear if clicked twice or use callback. Let's stick to standard Clear All for now if no selection
                 st.session_state.orders = []
                 st.rerun()


    with col2:
        # Send selected orders to routes
        if count > 0:
            if st.button(f"✈️ Send Selected ({count}) to Routes", type="primary", use_container_width=True):
                # Mark these as "for routing"
                st.session_state.orders_for_routing = [st.session_state.orders[i] for i in selected_indices]
                st.success(f"✅ {count} orders ready for routing!")
                st.switch_page("pages/2_👥_Select_Drivers.py")
        else:
            if st.button("👥 Next: Select Drivers →", use_container_width=True):
                # If nothing selected, send all
                st.session_state.orders_for_routing = st.session_state.orders
                st.switch_page("pages/2_👥_Select_Drivers.py")
    with col3:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.switch_page("app.py")
else:
    st.info("No orders loaded yet. Use one of the methods above to add orders.")

# Sidebar
with st.sidebar:
    st.header("💡 Tips")
    st.write("""
    **Text Parsing:**
    - Works best with clear address info
    - Include time windows if important
    
    **File Upload:**
    - CSV or Excel format
    - Columns: address, city, items, etc.
    
    **Manual Entry:**
    - Required fields marked with *
    - Use 12-hour time format (AM/PM)
    """)

# Show user info at the bottom of the sidebar
UserSession.show_user_info_sidebar()
