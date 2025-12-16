"""
DME Route Planner - Main Application
"""

import streamlit as st
from datetime import date
from components.session_manager import SessionManager
from components.user_session import UserSession
import os

st.set_page_config(
    page_title="DME Route Planner",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
def load_css():
    css_file = "assets/style.css"
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# Initialize user session
UserSession.init_user()

# Check if user is logged in
if not UserSession.is_logged_in():
    UserSession.select_user()
    st.stop()

# Load saved state for this user (Auto-Recovery)
SessionManager.load_state()

# Initialize session state
if 'orders' not in st.session_state:
    st.session_state.orders = []
if 'selected_drivers' not in st.session_state:
    st.session_state.selected_drivers = []
if 'optimized_routes' not in st.session_state:
    st.session_state.optimized_routes = {}

st.title("🚚 Dashboard")
st.caption("Daily Operations Overview")

today = date.today().strftime("%A, %B %d, %Y")
st.subheader(f"📅 {today}")

# --- METRICS SECTION ---
# Calculate stats from session state orders
total_orders = len(st.session_state.orders)
pending = sum(1 for o in st.session_state.orders if o.get('status', 'pending') == 'pending')
sent = sum(1 for o in st.session_state.orders if o.get('status') == 'sent_to_driver')
delivered = sum(1 for o in st.session_state.orders if o.get('status') == 'delivered')
failed = sum(1 for o in st.session_state.orders if o.get('status') == 'failed')

# Progress Calculation
progress = 0
if total_orders > 0:
    progress = (delivered + sent) / total_orders

# Display Metrics
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("📦 Total Orders", total_orders, delta=f"{total_orders} Today")
col2.metric("⏳ Pending", pending, delta_color="off")
col3.metric("📤 Sent", sent)
col4.metric("✅ Delivered", delivered)
col5.metric("❌ Failed", failed)

# Progress Bar
st.write(f"**Daily Progress: {int(progress*100)}%**")
st.progress(progress)

st.divider()

# --- QUICK ACTIONS ---
st.subheader("🚀 Quick Actions")

c1, c2, c3 = st.columns(3)

with c1:
    st.info("**1️⃣ Input Orders**")
    if st.button("📦 Add New Orders", use_container_width=True, type="primary"):
        st.switch_page("pages/1_📦_Input_Orders.py")

with c2:
    st.info("**2️⃣ Route Planning**")
    if st.button("🤖 Optimize Routes", use_container_width=True):
        st.switch_page("pages/3_🤖_Optimize_Routes.py")

with c3:
    st.info("**3️⃣ Tracking**")
    if st.button("📍 Track Status", use_container_width=True):
        st.switch_page("pages/6_📍_Track_Orders.py")

st.divider()

# --- RECENT ORDERS PREVIEW ---
if total_orders > 0:
    st.subheader("📝 Recent Orders")
    # Show simplified view of last 5 orders
    import pandas as pd
    if st.session_state.orders:
        display_df = pd.DataFrame(st.session_state.orders)[['customer', 'address', 'status', 'time_window']].tail(5)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.info("👋 No orders yet today! Click 'Add New Orders' to get started.")

with st.sidebar:
    st.header("ℹ️ About")
    st.write("""
    AI-powered route planning system for DME delivery.
    
    **Features:**
    - Smart driver assignment
    - Route optimization
    - WhatsApp integration
    - Historical tracking
    """)
    
    with st.expander("🔍 Session Info"):
        st.write(f"Orders: {len(st.session_state.orders)}")
        st.write(f"Drivers: {len(st.session_state.selected_drivers)}")
        st.write(f"Routes: {'Ready' if st.session_state.optimized_routes else 'Not ready'}")
    
    # Show user info and logout button
    UserSession.show_user_info_sidebar()

