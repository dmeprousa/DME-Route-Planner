"""
Page 5: History
View historical routes and orders
"""

import streamlit as st
from components.database import Database
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="History", page_icon="📊", layout="wide")

st.title("📊 Route History")
st.caption("View past routes and orders from Google Sheets")

st.divider()

# Date filter
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    # Date range selector
    default_start = datetime.now() - timedelta(days=7)
    start_date = st.date_input("From Date", value=default_start)

with col2:
    end_date = st.date_input("To Date", value=datetime.now())

with col3:
    st.write("")  # Spacer
    st.write("")  # Spacer
    search_btn = st.button("🔍 Search", type="primary", use_container_width=True)

st.divider()

# Tab view
tab1, tab2, tab3 = st.tabs(["🚚 Routes", "📦 Orders", "👥 Drivers"])

with tab1:
    st.subheader("Route History")
    
    if search_btn or st.session_state.get('auto_load_history', False):
        try:
            with st.spinner("Loading routes from database..."):
                db = Database()
                
                # Get routes worksheet
                ws = db.spreadsheet.worksheet('ROUTES')
                records = ws.get_all_records()
                
                if records:
                    df = pd.DataFrame(records)
                    
                    # Filter by date if date column exists
                    if 'date' in df.columns:
                        df['date'] = pd.to_datetime(df['date'])
                        mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
                        df = df[mask]
                    
                    st.success(f"✅ Found {len(df)} routes")
                    
                    # Display metrics
                    if len(df) > 0:
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Routes", len(df))
                        with col2:
                            total_stops = df['total_stops'].sum() if 'total_stops' in df.columns else 0
                            st.metric("Total Stops", int(total_stops))
                        with col3:
                            total_miles = df['total_distance_miles'].sum() if 'total_distance_miles' in df.columns else 0
                            st.metric("Total Miles", f"{total_miles:.1f}")
                        with col4:
                            unique_drivers = df['driver_name'].nunique() if 'driver_name' in df.columns else 0
                            st.metric("Drivers Used", unique_drivers)
                        
                        st.divider()
                        
                        # Display table
                        st.dataframe(df, use_container_width=True, height=400)
                        
                        # Download CSV
                        csv = df.to_csv(index=False)
                        st.download_button(
                            "⬇️ Download Routes CSV",
                            csv,
                            f"routes_history_{start_date}_to_{end_date}.csv",
                            "text/csv"
                        )
                    else:
                        st.info("No routes found in selected date range")
                else:
                    st.info("No routes in database yet")
                    
        except Exception as e:
            st.error(f"Error loading routes: {str(e)}")
            st.info("Make sure ROUTES worksheet exists in your Google Sheet")
    else:
        st.info("Click 'Search' to load route history")

with tab2:
    st.subheader("Order History")
    
    if search_btn or st.session_state.get('auto_load_history', False):
        try:
            with st.spinner("Loading orders from database..."):
                db = Database()
                
                # Get orders worksheet
                ws = db.spreadsheet.worksheet('ORDERS')
                records = ws.get_all_records()
                
                if records:
                    df = pd.DataFrame(records)
                    
                    # Filter by date if date column exists
                    if 'date' in df.columns:
                        df['date'] = pd.to_datetime(df['date'])
                        mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
                        df = df[mask]
                    
                    st.success(f"✅ Found {len(df)} orders")
                    
                    # Display metrics
                    if len(df) > 0:
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Orders", len(df))
                        with col2:
                            deliveries = len(df[df['order_type'] == 'Delivery']) if 'order_type' in df.columns else 0
                            st.metric("Deliveries", deliveries)
                        with col3:
                            pickups = len(df[df['order_type'] == 'Pickup']) if 'order_type' in df.columns else 0
                            st.metric("Pickups", pickups)
                        with col4:
                            unique_cities = df['city'].nunique() if 'city' in df.columns else 0
                            st.metric("Cities", unique_cities)
                        
                        st.divider()
                        
                        # Filters
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if 'city' in df.columns:
                                cities = ['All'] + sorted(df['city'].unique().tolist())
                                selected_city = st.selectbox("Filter by City", cities)
                                if selected_city != 'All':
                                    df = df[df['city'] == selected_city]
                        
                        with col2:
                            if 'order_type' in df.columns:
                                types = ['All'] + sorted(df['order_type'].unique().tolist())
                                selected_type = st.selectbox("Filter by Type", types)
                                if selected_type != 'All':
                                    df = df[df['order_type'] == selected_type]
                        
                        # --- NEW: Actionable Status Update ---
                        st.write("### 📝 Manage Status")
                        st.info("Check orders below to mark them as **Delivered** and click 'Save Changes'.")
                        
                        # Prepare data for editor
                        editable_df = df.copy()
                        # Add a boolean column for the checkbox based on status text
                        editable_df['is_delivered'] = editable_df['status'].str.lower() == 'delivered'
                        
                        # Use Data Editor
                        edited_data = st.data_editor(
                            editable_df,
                            column_config={
                                "is_delivered": st.column_config.CheckboxColumn(
                                    "Mark Delivered?",
                                    help="Check to mark as delivered",
                                    default=False
                                ),
                                "status": st.column_config.TextColumn("Current Status", disabled=True),
                                "order_id": st.column_config.TextColumn("ID", disabled=True),
                                "customer_name": st.column_config.TextColumn("Customer", disabled=True),
                                "address": st.column_config.TextColumn("Address", disabled=True),
                            },
                            disabled=["order_id", "status", "customer_name", "address", "city", "items"],
                            hide_index=True,
                            use_container_width=True,
                            key="orders_editor"
                        )
                        
                        # Save Button
                        if st.button("💾 Save Status Changes", type="primary"):
                            updated_count = 0
                            progress_text = "Updating orders..."
                            my_bar = st.progress(0, text=progress_text)
                            
                            try:
                                db = Database()
                                total_rows = len(edited_data)
                                
                                for index, row in edited_data.iterrows():
                                    order_id = row['order_id']
                                    new_checked = row['is_delivered']
                                    original_status = row['status'].lower()
                                    
                                    # Logic: If checked and wasn't delivered -> Mark Delivered
                                    if new_checked and original_status != 'delivered':
                                        db.update_order_status(order_id, 'delivered')
                                        updated_count += 1
                                    
                                    # Optional: If unchecked and was delivered -> Revert to pending?
                                    elif not new_checked and original_status == 'delivered':
                                        db.update_order_status(order_id, 'pending')
                                        updated_count += 1
                                        
                                    my_bar.progress((index + 1) / total_rows)
                                
                                my_bar.empty()
                                
                                if updated_count > 0:
                                    st.success(f"✅ Successfully updated {updated_count} orders!")
                                    st.rerun()
                                else:
                                    st.info("No changes detected.")
                                    
                            except Exception as e:
                                st.error(f"Error saving changes: {str(e)}")
                        # -------------------------------------
                        
                        # Download CSV
                        csv = df.to_csv(index=False)
                        st.download_button(
                            "⬇️ Download Orders CSV",
                            csv,
                            f"orders_history_{start_date}_to_{end_date}.csv",
                            "text/csv"
                        )
                    else:
                        st.info("No orders found in selected date range")
                else:
                    st.info("No orders in database yet")
                    
        except Exception as e:
            st.error(f"Error loading orders: {str(e)}")
            st.info("Make sure ORDERS worksheet exists in your Google Sheet")
    else:
        st.info("Click 'Search' to load order history")

with tab3:
    st.subheader("Driver List")
    
    try:
        with st.spinner("Loading drivers..."):
            db = Database()
            drivers = db.get_drivers(status='')  # Get all drivers
            
            if drivers:
                df = pd.DataFrame(drivers)
                
                st.success(f"✅ Found {len(df)} drivers")
                
                # Metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    active = len(df[df['status'] == 'active']) if 'status' in df.columns else 0
                    st.metric("Active Drivers", active)
                
                with col2:
                    inactive = len(df[df['status'] != 'active']) if 'status' in df.columns else 0
                    st.metric("Inactive Drivers", inactive)
                
                st.divider()
                
                # Display table
                st.dataframe(df, use_container_width=True, height=400)
                
                # Download CSV
                csv = df.to_csv(index=False)
                st.download_button(
                    "⬇️ Download Drivers CSV",
                    csv,
                    "drivers_list.csv",
                    "text/csv"
                )
            else:
                st.info("No drivers in database")
                
    except Exception as e:
        st.error(f"Error loading drivers: {str(e)}")

st.divider()

# Navigation
col1, col2 = st.columns(2)

with col1:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("app.py")

with col2:
    if st.button("📦 New Routes", type="primary", use_container_width=True):
        st.switch_page("pages/1_📦_Input_Orders.py")

# Sidebar
with st.sidebar:
    st.header("💡 Tips")
    st.write("""
    **History View:**
    - Select date range to filter
    - Export data as CSV
    - Track performance metrics
    
    **Analytics:**
    - Monitor delivery volume
    - Track driver utilization
    - Identify service areas
    """)
    
    st.divider()
    
    st.header("🔄 Quick Links")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.session_state.auto_load_history = True
        st.rerun()
