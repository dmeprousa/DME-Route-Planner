"""
Page 6: Track Orders
Real-time order tracking and status updates
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from datetime import date, datetime
from components.database import Database
from components.user_session import UserSession
import pandas as pd

st.set_page_config(page_title="Track Orders", page_icon="📍", layout="wide")

# Require authentication
UserSession.require_auth()

st.title("📍 Track Orders")
st.caption("Monitor order status and driver progress in real-time")

# Date filter
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    selected_date = st.date_input("Select Date", value=date.today())
with col2:
    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "Pending", "Sent to Driver", "Delivered", "Failed"]
    )
with col3:
    st.write("")
    st.write("")
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.divider()

# Load orders from database
try:
    db = Database()
    date_str = selected_date.strftime('%Y-%m-%d')
    
    # Get all orders for this date
    all_orders = db.get_orders(date=date_str)
    
    if all_orders:
        df = pd.DataFrame(all_orders)
        
        # Apply status filter
        if status_filter != "All":
            df = df[df['status'] == status_filter.lower().replace(' ', '_')]
        
        # Group by status
        st.subheader("📊 Status Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            pending = len(df[df['status'] == 'pending'])
            st.metric("🟡 Pending", pending)
        
        with col2:
            sent = len(df[df['status'] == 'sent_to_driver'])
            st.metric("🔵 Sent to Driver", sent)
        
        with col3:
            delivered = len(df[df['status'] == 'delivered'])
            st.metric("🟢 Delivered", delivered)
        
        with col4:
            failed = len(df[df['status'] == 'failed'])
            st.metric("🔴 Failed", failed)
        
        st.divider()
        
        # Display orders by driver
        if 'assigned_driver' in df.columns:
            drivers = df['assigned_driver'].unique()
            
            for driver in drivers:
                if not driver or driver == '':
                    continue
                
                driver_orders = df[df['assigned_driver'] == driver]
                
                with st.expander(f"🚚 {driver} ({len(driver_orders)} orders)", expanded=True):
                    
                    # Summary
                    driver_pending = len(driver_orders[driver_orders['status'] == 'pending'])
                    driver_sent = len(driver_orders[driver_orders['status'] == 'sent_to_driver'])
                    driver_delivered = len(driver_orders[driver_orders['status'] == 'delivered'])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.info(f"🟡 Pending: {driver_pending}")
                    with col2:
                        st.info(f"🔵 Sent: {driver_sent}")
                    with col3:
                        st.success(f"🟢 Delivered: {driver_delivered}")
                    
                    st.divider()
                    
                    # Each order
                    for idx, order in driver_orders.iterrows():
                        col1, col2, col3 = st.columns([4, 2, 1])
                        
                        with col1:
                            # Order info
                            st.markdown(f"**Order #{order.get('stop_number', 'N/A')}**: {order.get('customer_name', 'Unknown')}")
                            st.caption(f"📍 {order.get('address', 'No address')}, {order.get('city', '')}")
                            st.caption(f"📦 {order.get('items', 'No items')}")
                        
                        with col2:
                            # Status selector
                            current_status = order.get('status', 'pending')
                            
                            status_options = {
                                'pending': '🟡 Pending',
                                'sent_to_driver': '🔵 Sent to Driver',
                                'delivered': '🟢 Delivered',
                                'failed': '🔴 Failed'
                            }
                            
                            # Map current status to display
                            current_display = status_options.get(current_status, '🟡 Pending')
                            current_index = list(status_options.values()).index(current_display)
                            
                            new_status_display = st.selectbox(
                                "Status",
                                options=list(status_options.values()),
                                index=current_index,
                                key=f"status_{order.get('order_id')}"
                            )
                            
                            # Map back to internal status
                            new_status = [k for k, v in status_options.items() if v == new_status_display][0]
                            
                            # Update if changed
                            if new_status != current_status:
                                try:
                                    db.update_order_status(order.get('order_id'), new_status)
                                    st.success("✅ Updated!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                        
                        with col3:
                            # Quick delivered checkbox
                            is_delivered = current_status == 'delivered'
                            
                            if st.checkbox(
                                "✅ Delivered",
                                value=is_delivered,
                                key=f"delivered_{order.get('order_id')}"
                            ):
                                if not is_delivered:
                                    try:
                                        db.update_order_status(order.get('order_id'), 'delivered')
                                        st.success("✅ Marked as delivered!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                        
                        st.divider()
            
            # Unassigned orders
            unassigned = df[(df['assigned_driver'].isna()) | (df['assigned_driver'] == '')]
            
            if len(unassigned) > 0:
                with st.expander(f"❓ Unassigned Orders ({len(unassigned)})", expanded=True):
                    for idx, order in unassigned.iterrows():
                        st.markdown(f"**{order.get('customer_name', 'Unknown')}** - {order.get('address', 'No address')}")
                        st.caption(f"📦 {order.get('items', 'No items')}")
                    
                    st.warning("⚠️ These orders haven't been assigned to any driver yet.")
        
        else:
            # No driver assignments yet
            st.info("ℹ️ Orders haven't been assigned to drivers yet.")
            
            # Show all orders
            st.dataframe(df, use_container_width=True)
    
    else:
        # No orders for this date
        st.info(f"📦 No orders found for {selected_date.strftime('%B %d, %Y')}")
        
        if st.button("➕ Add Orders for Today"):
            st.switch_page("pages/1_📦_Input_Orders.py")

except Exception as e:
    st.error(f"❌ Error loading orders: {str(e)}")
    st.info("Make sure Google Sheets is connected and ORDERS worksheet exists.")

st.divider()

# Navigation
col1, col2 = st.columns(2)
with col1:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("app.py")
with col2:
    if st.button("📊 View History", use_container_width=True):
        st.switch_page("pages/5_📊_History.py")

# Sidebar
with st.sidebar:
    st.header("💡 Tips")
    st.write("""
    **Order Tracking:**
    - View all orders by driver
    - Update status in real-time
    - Quick "Delivered" checkbox
    - Filter by status or date
    
    **Status Options:**
    - 🟡 Pending: Not sent yet
    - 🔵 Sent to Driver: On the way
    - 🟢 Delivered: Completed ✅
    - 🔴 Failed: Problem occurred
    """)
    
    st.divider()
    
    st.header("🔄 Quick Actions")
    if st.button("Mark All Sent as Delivered", use_container_width=True):
        try:
            db = Database()
            date_str = selected_date.strftime('%Y-%m-%d')
            orders = db.get_orders(date=date_str, status='sent_to_driver')
            
            count = 0
            for order in orders:
                db.update_order_status(order['order_id'], 'delivered')
                count += 1
            
            if count > 0:
                st.success(f"✅ Marked {count} orders as delivered!")
                st.rerun()
            else:
                st.info("No orders to mark")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Show user info
UserSession.show_user_info_sidebar()
