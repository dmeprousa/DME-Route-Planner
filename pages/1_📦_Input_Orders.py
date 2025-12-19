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
import pandas as pd

st.set_page_config(page_title="Input Orders", page_icon="📦", layout="wide")

# Require authentication
UserSession.require_auth()

st.title("📦 Input Orders")
today = date.today()
st.caption(f"Add delivery/pickup orders for **{today.strftime('%A, %B %d, %Y')}**")

# Initialize Database Manager
from components.database import Database
db = Database()

# Date-based session management
if 'current_date' not in st.session_state:
    st.session_state.current_date = today

# Check if date changed - auto-archive old orders
if st.session_state.current_date < today:
    # Date changed! Archive old orders
    if 'orders' in st.session_state and st.session_state.orders:
        # Save old orders to history before clearing
        current_user = UserSession.get_current_user()
        if current_user and sheets.spreadsheet:
            try:
                from components.database import Database
                db = Database()
                old_date = st.session_state.current_date.strftime('%Y-%m-%d')
                
                # Save to ORDERS tab with old date
                for order in st.session_state.orders:
                    order['archived_date'] = old_date
                    order['status'] = 'archived'
                
                db.save_orders(st.session_state.orders, old_date)
                st.success(f"📁 Archived {len(st.session_state.orders)} orders from {old_date}")
            except Exception as e:
                st.warning(f"Could not archive old orders: {str(e)}")
        
        # Clear old orders for fresh start
        st.session_state.orders = []
        st.balloons()
        st.info("🆕 New day! Starting fresh.")
    
    # Update current date
    st.session_state.current_date = today

# Initialize session state and load from Google Sheets
if 'orders' not in st.session_state:
    # Load pending orders for TODAY only from the main ORDERS sheet
    current_user = UserSession.get_current_user()
    if current_user:
        today_str = today.strftime('%Y-%m-%d')
        # Load from the new unified source of truth
        orders = db.get_orders(date=today_str)
        st.session_state.orders = orders if orders is not None else []
    else:
        st.session_state.orders = []

# Show current count and connection status


st.divider()

# Input method selector (replaces tabs - this way selection persists!)
if 'selected_input_method' not in st.session_state:
    st.session_state.selected_input_method = "📸 Upload Image"  # Default to most used

st.subheader("Choose Input Method")
selected_method = st.radio(
    "How do you want to add orders?",
    ["📝 Paste Text", "📄 Upload File", "📸 Upload Image", "✍️ Manual Entry"],
    index=["📝 Paste Text", "📄 Upload File", "📸 Upload Image", "✍️ Manual Entry"].index(st.session_state.selected_input_method),
    horizontal=True,
    key="input_method_selector"
)

# Update session state
st.session_state.selected_input_method = selected_method

st.divider()

# Display selected input method
if selected_method == "📝 Paste Text":
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
                                # Add date to order
                                order['date'] = today.strftime('%Y-%m-%d')
                                from datetime import datetime
                                order['parsed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                order['status'] = 'pending'
                                
                                # CRITICAL: Generate order_id immediately!
                                import uuid
                                order['order_id'] = f"ORD-{today.strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
                                
                                st.session_state.orders.append(order)
                                added += 1
                            else:
                                errors.append(f"Invalid order: {msg}")
                        
                        if added > 0:
                            st.success(f"✅ Added {added} orders!")
                            # Save to Google Sheets (Unified ORDERS Tab)
                            date_str = today.strftime('%Y-%m-%d')
                            try:
                                db.save_orders(st.session_state.orders, date_str)
                                st.success("☁️ Synced to Google Sheets!")
                            except Exception as e:
                                st.warning(f"⚠️ Sync failed: {str(e)}")
                        if errors:
                            for error in errors:
                                st.warning(error)
                        
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error parsing text: {str(e)}")
            else:
                st.warning("Please paste some text first")

elif selected_method == "📄 Upload File":
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
            df = pd.DataFrame(parsed_orders) # Convert to DataFrame for easier processing
            
            st.write(f"Found {len(df)} orders in file")
            st.dataframe(df, use_container_width=True)
            
            if st.button("✅ Add All Orders", type="primary"):
                # Process file with progress
                added = 0
                errors = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                total_rows = len(df)
                for idx, row in df.iterrows():
                    # Update progress
                    progress = (idx + 1) / total_rows
                    progress_bar.progress(progress)
                    status_text.text(f"Processing row {idx+1} of {total_rows}...")
                    
                    order = row.to_dict()
                    is_valid, msg = validate_order(order)
                    if is_valid:
                        # Add date to order
                        order['date'] = today.strftime('%Y-%m-%d')
                        from datetime import datetime
                        order['parsed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        order['status'] = 'pending'
                        
                        # CRITICAL: Generate order_id immediately!
                        import uuid
                        order['order_id'] = f"ORD-{today.strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
                        
                        st.session_state.orders.append(order)
                        added += 1
                    else:
                        errors.append(f"Row {idx+1}: {msg}")
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                if added > 0:
                    st.success(f"✅ Added {added} orders!")
                    # Save to Google Sheets (Unified ORDERS Tab)
                    date_str = today.strftime('%Y-%m-%d')
                    try:
                        db.save_orders(st.session_state.orders, date_str)
                        st.success("☁️ Synced to Google Sheets!")
                    except Exception as e:
                        st.warning(f"⚠️ Sync failed: {str(e)}")
                if errors:
                    with st.expander("⚠️ Validation Errors"):
                        for error in errors:
                            st.warning(error)
                
                st.rerun()
                
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

elif selected_method == "📸 Upload Image":
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
                        
                        # Validate and add with progress
                        added = 0
                        errors = []
                        progress_bar = st.progress(0)
                        
                        total = len(parsed_orders)
                        for idx, order in enumerate(parsed_orders):
                            progress_bar.progress((idx + 1) / total)
                            
                            is_valid, msg = validate_order(order)
                            if is_valid:
                                # Add date to order
                                order['date'] = today.strftime('%Y-%m-%d')
                                from datetime import datetime
                                order['parsed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                order['status'] = 'pending'
                                
                                # CRITICAL: Generate order_id immediately!
                                import uuid
                                order['order_id'] = f"ORD-{today.strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
                                
                                st.session_state.orders.append(order)
                                added += 1
                            else:
                                errors.append(f"Invalid order: {msg}")
                        
                        progress_bar.empty()
                        
                        if added > 0:
                            st.success(f"✅ Extracted {added} orders from image!")
                            # Save to Google Sheets (Unified ORDERS Tab)
                            date_str = today.strftime('%Y-%m-%d')
                            try:
                                db.save_orders(st.session_state.orders, date_str)
                                st.success("☁️ Synced to Google Sheets!")
                            except Exception as e:
                                st.warning(f"⚠️ Sync failed: {str(e)}")
                            st.balloons()
                            st.rerun()
                        
                        if errors:
                            for err in errors:
                                st.warning(err)
                                
                except Exception as e:
                    st.error(f"Error parsing image: {str(e)}")

elif selected_method == "✍️ Manual Entry":
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
                # Add date to order
                order['date'] = today.strftime('%Y-%m-%d')
                from datetime import datetime
                order['parsed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                order['status'] = 'pending'
                
                # CRITICAL: Generate order_id immediately!
                import uuid
                order['order_id'] = f"ORD-{today.strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
                
                st.session_state.orders.append(order)
                
                # Save to Google Sheets (Unified ORDERS Tab)
                date_str = today.strftime('%Y-%m-%d')
                try:
                    db.save_orders(st.session_state.orders, date_str)
                    st.success("✅ Order added and synced!")
                except Exception as e:
                    st.success("✅ Order added!")
                    st.warning(f"⚠️ Failed to sync: {str(e)}")
                st.rerun()
            else:
                st.error(f"❌ Validation failed: {msg}")
                st.info("💡 Please check the form and try again.")

st.divider()

# Display current orders
if st.session_state.orders:
    st.subheader("📋 Daily Workflow")
    
    # Prepare DataFrame for Editor
    df = pd.DataFrame(st.session_state.orders)
    
    # Ensure 'status' column exists and fill n/a
    if 'status' not in df.columns:
        df['status'] = 'pending'
    df['status'] = df['status'].fillna('pending')

    # Ensure other essential columns exist to prevent display errors
    essential_cols = ['customer_name', 'customer_phone', 'time_window', 'special_notes', 'order_type', 'zip_code', 'city', 'items', 'address', 'assigned_driver']
    for col in essential_cols:
        if col not in df.columns:
            df[col] = ""
        # Clean up 'nan' or None values
        df[col] = df[col].replace('nan', '').fillna('')
    
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
    
    # Add helpful info about assigned orders
    assigned_count = len([o for o in st.session_state.orders if o.get('assigned_driver') and o.get('assigned_driver') not in ['Unassigned', 'None', '', None]])
    if assigned_count > 0:
        st.info(f"📌 {assigned_count} order(s) assigned to drivers")

    # Load available drivers for dropdown
    try:
        from components.database import Database
        db = Database()
        all_drivers = db.get_drivers(status='active')
        driver_names = [d.get('name', '') for d in all_drivers if d.get('name')]
        driver_options = ["Unassigned"] + driver_names
    except Exception as e:
        driver_options = ["Unassigned"]
        st.warning(f"Could not load drivers: {str(e)}")

    # Data Editor with column configurations
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "Selected": st.column_config.CheckboxColumn(
                "Select",
                help="Select orders for deletion",
                default=False,
            ),
            "status": st.column_config.SelectboxColumn(
                "Status",
                help="Order status",
                width="medium",
                options=[
                    "pending",
                    "sent_to_driver",
                    "delivered",
                    "failed",
                    "archived"
                ],
                required=True,
            ),

            # Enhanced: Assigned Driver as dropdown
            "assigned_driver": st.column_config.SelectboxColumn(
                "🚚 Assigned Driver",
                help="Select a driver to assign this order",
                width="medium",
                options=driver_options,
                required=False,
            ),
            # NEW: Parsing Time
            "parsed_at": st.column_config.DatetimeColumn(
                "🕒 Parsed At",
                help="Time when order was added",
                format="D MMM, h:mm a",
                width="medium" 
            ),
            # Hide technical columns
            "username": None,
            "added_at": None,
            "created_at": None,
            "date": None,
            "selected": None, # Hide duplicate boolean column if exists
            "original_text": None,
            "order_id": None
        },
        column_order=[
            "Selected", "status", "assigned_driver", "parsed_at", "order_type", 
            "customer_name", "customer_phone", "address", "city", "zip_code", 
            "items", "time_window", "special_notes"
        ],
        disabled=[c for c in df.columns if c not in ["Selected", "status", "assigned_driver"]], # Allow editing driver assignment
        hide_index=True,
        key="order_editor" 
    )
    
    # CRITICAL FIX: Reset index to ensure indices match row positions!
    # Without this, edited_df might have non-sequential indices which breaks deletion
    edited_df = edited_df.reset_index(drop=True)

    # Actions Bar
    
    # Sync status changes back to session state
    # Identify differneces and update
    for index, row in edited_df.iterrows():
        if index < len(st.session_state.orders):
            if st.session_state.orders[index].get('status') != row['status']:
                st.session_state.orders[index]['status'] = row['status']
            
            # Sync assigned driver manual changes
            if st.session_state.orders[index].get('assigned_driver') != row['assigned_driver']:
                 st.session_state.orders[index]['assigned_driver'] = row['assigned_driver']
                 
                 # Auto-update status if driver is assigned
                 driver_val = row['assigned_driver']
                 if driver_val and driver_val not in ["Unassigned", "None", ""]:
                     st.session_state.orders[index]['status'] = 'sent_to_driver'
                     st.rerun()

    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col3:
        if st.button("☁️ Cloud Sync", type="primary", use_container_width=True, help="Push orders to Google Sheets System"):
            try:
                from components.database import Database
                db = Database()
                date_str = today.strftime('%Y-%m-%d')
                db.save_orders(st.session_state.orders, date_str)
                st.toast("✅ Synced to Database!", icon="☁️")
            except Exception as e:
                st.error(f"Sync failed: {str(e)}")
    
    with col1:
        # Calculate selected count
        selected_indices = edited_df[edited_df["Selected"] == True].index.tolist()
        count = len(selected_indices)
        
        # DEBUG: Show what we got from DataFrame
        st.write(f"🔍 **DEBUG:** selected_indices = {selected_indices}")
        st.write(f"🔍 **DEBUG:** count = {count}")
        st.write(f"🔍 **DEBUG:** Total orders in session = {len(st.session_state.orders)}")
        
        # Show selected column values
        if 'Selected' in edited_df.columns:
            selected_values = edited_df['Selected'].tolist()
            st.write(f"🔍 **DEBUG:** Selected column = {selected_values}")
            st.write(f"🔍 **DEBUG:** True count = {selected_values.count(True)}")
        
        if count > 0:
            # Initialize confirm state if not exists
            if 'confirming_delete' not in st.session_state:
                st.session_state.confirming_delete = False
            
            # Store selected ORDER IDs (not indices!) in session state for confirmation
            # This prevents issues with changing indices during rerun
            if 'pending_delete_order_ids' not in st.session_state:
                st.session_state.pending_delete_order_ids = []
                
            if st.button(f"🗑️ Delete Selected ({count})", use_container_width=True):
                st.session_state.confirming_delete = True
                # Extract order_ids from selected orders
                order_ids_to_delete = []
                for idx in selected_indices:
                    if idx < len(st.session_state.orders):
                        order_id = st.session_state.orders[idx].get('order_id')
                        customer_name = st.session_state.orders[idx].get('customer_name', 'Unknown')
                        
                        if order_id:
                            order_ids_to_delete.append(order_id)
                        else:
                            st.error(f"⚠️ Order '{customer_name}' at index {idx} has NO order_id!")
                
                st.session_state.pending_delete_order_ids = order_ids_to_delete
                
                # DEBUG INFO
                st.info(f"🔍 DEBUG: Selected {len(order_ids_to_delete)} orders for deletion")
                st.code(f"IDs: {order_ids_to_delete}")
                st.rerun()
                
            if st.session_state.confirming_delete:
                delete_count = len(st.session_state.pending_delete_order_ids)
                
                # DEBUG: Show what we're about to delete
                st.write("### 🔍 DEBUG INFO (Before Deletion):")
                st.code(f"pending_delete_order_ids = {st.session_state.pending_delete_order_ids}")
                
                # Show all current order IDs for comparison
                current_ids = [o.get('order_id', 'NONE') for o in st.session_state.orders]
                st.code(f"Current order IDs in session = {current_ids}")
                
                st.warning(f"⚠️ You are about to delete {delete_count} orders. This cannot be undone!")
                col_conf1, col_conf2 = st.columns(2)
                with col_conf1:
                    if st.button("✅ Yes, Delete", type="primary", key="btn_confirm_del"):
                        # Show debug info
                        st.info(f"🔍 Order IDs to DELETE: {st.session_state.pending_delete_order_ids}")
                        st.info(f"📦 Current total orders: {len(st.session_state.orders)}")
                        
                        # Show all current order IDs
                        all_order_ids = [o.get('order_id', 'NO_ID') for o in st.session_state.orders]
                        st.code(f"All Order IDs in session:\n{all_order_ids}")
                        
                        # Prepare deletion list for confirmation
                        names_to_delete = []
                        orders_to_keep = []
                        
                        # CRITICAL FIX: Delete by order_id, not by index
                        for i, order in enumerate(st.session_state.orders):
                            order_id = order.get('order_id')
                            customer_name = order.get('customer_name', 'Unknown')
                            
                            if order_id in st.session_state.pending_delete_order_ids:
                                # This order should be deleted
                                names_to_delete.append(customer_name)
                                st.warning(f"❌ DELETING: {customer_name} (ID: {order_id})")
                            else:
                                # This order should be kept
                                orders_to_keep.append(order)
                                st.success(f"✅ KEEPING: {customer_name} (ID: {order_id})")
                        
                        st.warning(f"⚠️ Will delete {len(names_to_delete)} orders:")
                        st.info(", ".join(names_to_delete))
                        
                        st.success(f"✅ Will keep {len(orders_to_keep)} orders")
                        
                        # Update session state with remaining orders
                        st.session_state.orders = orders_to_keep
                        
                        # Sync to Google Sheets after deletion
                        try:
                            # DEBUG: Verify what we are saving
                            st.info(f"💾 Saving {len(st.session_state.orders)} orders to database...")
                            kept_ids = [o.get('order_id') for o in st.session_state.orders]
                            st.code(f"IDs being saved: {kept_ids}")
                            
                            from components.database import Database
                            db = Database()
                            date_str = today.strftime('%Y-%m-%d')
                            
                            db.save_orders(st.session_state.orders, date_str)
                            
                            # Delete session cache to prevent auto-restore
                            current_user = UserSession.get_current_user()
                            if current_user:
                                cache_file = f".session_cache_{current_user}.json"
                                if os.path.exists(cache_file):
                                    os.remove(cache_file)
                            
                            # Force reload from ORDERS sheet
                            fresh_orders = db.get_orders(date=date_str, status=None)  # Get all statuses
                            st.session_state.orders = fresh_orders if fresh_orders else []
                            
                            st.toast("✅ Orders deleted and synced to database!", icon="☁️")
                            
                        except Exception as e:
                            st.error(f"❌ Operation failed: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())
                            # Restore session state if possible
                            # st.session_state.orders = orders_to_keep
                        
                        st.session_state.confirming_delete = False  # Reset
                        st.session_state.pending_delete_order_ids = []  # Clear
                        
                        # CRITICAL: Rerun to refresh table indices and avoid IndexError
                        st.rerun()
                with col_conf2:
                    if st.button("❌ Cancel", key="btn_cancel_del"):
                        st.session_state.confirming_delete = False
                        st.rerun()
                        
        else:
            if 'confirming_clear' not in st.session_state:
                st.session_state.confirming_clear = False
                
            if st.button("🗑️ Clear All Orders", use_container_width=True):
                st.session_state.confirming_clear = True
                st.rerun()  # Rerun to show confirmation
                
            if st.session_state.confirming_clear:
                st.error("⚠️ WARNING: This will delete ALL orders!")
                col_clr1, col_clr2 = st.columns(2)
                with col_clr1:
                    if st.button("✅ Confirm Clear All", type="primary", key="btn_confirm_clr"):
                        st.session_state.orders = []
                        
                        # Sync to Google Sheets (clear all)
                        try:
                            from components.database import Database
                            db = Database()
                            date_str = today.strftime('%Y-%m-%d')
                            db.save_orders(st.session_state.orders, date_str)
                            
                            # Delete session cache to prevent auto-restore
                            current_user = UserSession.get_current_user()
                            if current_user:
                                cache_file = f".session_cache_{current_user}.json"
                                if os.path.exists(cache_file):
                                    os.remove(cache_file)
                            
                            # Force reload from ORDERS sheet (should be empty now)
                            fresh_orders = db.get_orders(date=date_str, status=None)
                            st.session_state.orders = fresh_orders if fresh_orders else []
                            
                            st.toast("✅ All orders cleared and synced!", icon="☁️")
                        except Exception as e:
                            st.error(f"Clear failed: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())
                        
                        st.session_state.confirming_clear = False
                        st.success("🆑 All orders cleared!")
                        st.rerun()
                with col_clr2:
                    if st.button("❌ Cancel", key="btn_cancel_clr"):
                        st.session_state.confirming_clear = False
                        st.rerun()


    with col2:
        # Send selected orders to routes
        if count > 0:
            # Check if any selected orders already have drivers assigned
            assigned_orders = []
            unassigned_orders = []
            
            for i in selected_indices:
                order = st.session_state.orders[i]
                driver = order.get('assigned_driver', '')
                if driver and driver not in ['Unassigned', 'None', '', None]:
                    assigned_orders.append(order)
                else:
                    unassigned_orders.append(order)
            
            # Show warning if trying to re-route assigned orders
            if assigned_orders:
                st.warning(
                    f"⚠️ **{len(assigned_orders)} of the selected orders are already assigned to drivers!**\n\n"
                    f"Re-routing these orders will change their driver assignments."
                )
                
                # Show which drivers will be affected
                affected_drivers = set([o.get('assigned_driver', '') for o in assigned_orders])
                affected_drivers = [d for d in affected_drivers if d and d not in ['Unassigned', 'None', '']]
                if affected_drivers:
                    st.info(f"📋 Currently assigned to: {', '.join(affected_drivers)}")
                
                col_override1, col_override2 = st.columns(2)
                
                with col_override1:
                    if st.button(f"🔄 Override & Re-Route All ({count})", type="secondary", use_container_width=True):
                        st.session_state.orders_for_routing = [st.session_state.orders[i] for i in selected_indices]
                        st.warning(f"⚠️ Re-routing {count} orders (including {len(assigned_orders)} already assigned)")
                        st.switch_page("pages/2_👥_Select_Drivers.py")
                
                with col_override2:
                    if len(unassigned_orders) > 0:
                        if st.button(f"✈️ Route Unassigned Only ({len(unassigned_orders)})", type="primary", use_container_width=True):
                            st.session_state.orders_for_routing = unassigned_orders
                            st.success(f"✅ {len(unassigned_orders)} unassigned orders ready for routing!")
                            st.switch_page("pages/2_👥_Select_Drivers.py")
            else:
                # All selected are unassigned - safe to route
                if st.button(f"✈️ Send Selected ({count}) to Routes", type="primary", use_container_width=True):
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
    # Better Empty State
    st.info("📦 No orders for today yet!")
    
    st.markdown("### 🚀 Quick Start:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📸 Upload Image")
        st.caption("Got a screenshot or fax? Upload it!")
        if st.button("Upload Image", use_container_width=True, key="empty_img"):
            st.info("👆 Use the '📸 Upload Image' tab above")
    
    with col2:
        st.markdown("#### 📝 Paste Text")
        st.caption("Copy-paste order details")
        if st.button("Paste Text", use_container_width=True, key="empty_text"):
            st.info("👆 Use the '📝 Paste Text' tab above")
    
    with col3:
        st.markdown("#### 📄 Upload File")  
        st.caption("CSV or Excel file")
        if st.button("Upload File", use_container_width=True, key="empty_file"):
            st.info("👆 Use the '📄 Upload File' tab above")

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

# Workflow Progress Indicator (at very top)
st.sidebar.markdown("---")
st.sidebar.subheader("📍 Workflow Progress")
workflow_steps = [
    ("1️⃣ Input Orders", True),  # Current page
    ("2️⃣ Select Drivers", 'selected_drivers' in st.session_state and st.session_state.selected_drivers),
    ("3️⃣ Optimize Routes", 'optimized_routes' in st.session_state and st.session_state.optimized_routes),
    ("4️⃣ Send to Drivers", False)
]

for step_name, is_complete in workflow_steps:
    if is_complete:
        st.sidebar.success(f"✅ {step_name}")
    else:
        st.sidebar.info(f"⏳ {step_name}")

