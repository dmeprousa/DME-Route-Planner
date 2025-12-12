"""
Page 1: Input Orders
Parse orders from text, file upload, or manual entry
"""

import streamlit as st
from datetime import date
from components.order_input import OrderInput
from utils.validators import validate_order
import pandas as pd

st.set_page_config(page_title="Input Orders", page_icon="📦", layout="wide")

st.title("📦 Input Orders")
st.caption("Add delivery/pickup orders for today")

# Initialize session state
if 'orders' not in st.session_state:
    st.session_state.orders = []

# Show current count
st.metric("Orders Loaded", len(st.session_state.orders))

st.divider()

# Input method tabs
tab1, tab2, tab3 = st.tabs(["📝 Paste Text", "📄 Upload File", "✍️ Manual Entry"])

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
                if errors:
                    with st.expander("⚠️ Validation Errors"):
                        for error in errors:
                            st.warning(error)
                
                st.rerun()
                
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

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
                st.success("✅ Order added!")
                st.rerun()
            else:
                st.error(f"❌ {msg}")

st.divider()

# Display current orders
if st.session_state.orders:
    st.subheader("📋 Current Orders")
    
    df = pd.DataFrame(st.session_state.orders)
    st.dataframe(df, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🗑️ Clear All Orders", use_container_width=True):
            st.session_state.orders = []
            st.rerun()
    with col2:
        if st.button("👥 Next: Select Drivers →", type="primary", use_container_width=True):
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
