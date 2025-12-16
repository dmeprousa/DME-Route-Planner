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

st.title("🚚 DME Route Planner")
st.caption("AI-Powered Route Optimization for Hospice Pro DME")

today = date.today().strftime("%B %d, %Y")
st.subheader(f"📅 {today}")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Active Drivers", len(st.session_state.selected_drivers), help="Selected for today")
with col2:
    st.metric("Orders Today", len(st.session_state.orders), help="Total orders loaded")
with col3:
    st.metric("Routes Ready", "Yes" if st.session_state.optimized_routes else "No", help="Optimized and ready to send")

st.divider()

st.subheader("🚀 Quick Start Workflow")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 1️⃣ Input Orders")
    st.write("Add today's deliveries")
    if st.button("📦 Add Orders →", use_container_width=True, type="primary"):
        st.switch_page("pages/1_📦_Input_Orders.py")

with col2:
    st.markdown("### 2️⃣ Select Drivers")
    st.write("Choose who's working")
    if st.button("👥 Select Drivers →", use_container_width=True):
        st.switch_page("pages/2_👥_Select_Drivers.py")

with col3:
    st.markdown("### 3️⃣ Optimize & Send")
    st.write("AI plans routes")
    if st.button("🤖 Optimize Routes →", use_container_width=True):
        st.switch_page("pages/3_🤖_Optimize_Routes.py")

st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📍 Track Orders", use_container_width=True, type="primary"):
        st.switch_page("pages/6_📍_Track_Orders.py")
with col2:
    if st.button("📊 View History", use_container_width=True):
        st.switch_page("pages/5_📊_History.py")
with col3:
    if st.button("📱 Contact Info", use_container_width=True):
        st.info("**Hospice Pro DME**\n📞 760-879-1071")

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

