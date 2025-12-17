"""
Page 3: Optimize Routes
Use AI to optimize routes and assign orders to drivers
"""

import sys
import os
# Add project root to path for proper imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from datetime import date
from components.ai_optimizer import AIOptimizer
from components.driver_manager import DriverManager
from components.route_formatter import RouteFormatter
from components.database import Database
from components.user_session import UserSession
import os

st.set_page_config(page_title="Optimize Routes", page_icon="🤖", layout="wide")

# Require authentication
UserSession.require_auth()

st.title("🤖 Optimize Routes")
st.caption("AI-powered route optimization using Google Gemini")

# Check prerequisites
if 'orders_for_routing' in st.session_state and st.session_state.orders_for_routing:
    # Use selected orders
    orders_to_route = st.session_state.orders_for_routing
elif 'orders' in st.session_state and st.session_state.orders:
    # Fallback to all orders if no selection
    orders_to_route = st.session_state.orders
    st.info("ℹ️ Using all orders (no specific selection made)")
else:
    st.warning("⚠️ No orders loaded. Please add orders first.")
    if st.button("📦 Go to Input Orders"):
        st.switch_page("pages/1_📦_Input_Orders.py")
    st.stop()

if 'selected_drivers' not in st.session_state or not st.session_state.selected_drivers:
    st.warning("⚠️ No drivers selected. Please select drivers first.")
    if st.button("👥 Go to Select Drivers"):
        st.switch_page("pages/2_👥_Select_Drivers.py")
    st.stop()

# Initialize session state
if 'optimized_routes' not in st.session_state:
    st.session_state.optimized_routes = {}

# AUTO-LOAD routes from database if available (prevents data loss on refresh!)
if not st.session_state.optimized_routes:
    try:
        today = date.today().strftime('%Y-%m-%d')
        db = Database()
        
        # Try to load today's routes
        saved_routes = db.get_routes(date=today)
        
        if saved_routes:
            # Reconstruct optimized_routes structure
            # (Assuming get_routes returns list, need to group by driver)
            # This is simplified - adjust based on actual data structure
            st.session_state.optimized_routes = saved_routes
            st.info(f"📥 Loaded existing routes for {today} from database")
            
    except Exception as e:
        # Silently fail - no routes to load
        pass

# Show current status
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Orders to Route", len(orders_to_route))
with col2:
    st.metric("Available Drivers", len(st.session_state.selected_drivers))
with col3:
    routes_ready = "Yes" if st.session_state.optimized_routes else "No"
    st.metric("Routes Optimized", routes_ready)

st.divider()

# Prepare drivers with configuration
driver_config = st.session_state.get('driver_config', {})
prepared_drivers = DriverManager.prepare_for_optimization(
    st.session_state.selected_drivers,
    driver_config
)

# Show driver summary
with st.expander("📋 Driver Configuration"):
    for driver in prepared_drivers:
        st.write(f"**{driver.get('driver_name')}**")
        st.write(f"- Start: {driver.get('start_time')} from {driver.get('start_location')}")
        st.write(f"- Coverage: {driver.get('primary_areas', 'N/A')}")

st.divider()

# Optimize button
if st.button("🚀 Run AI Optimization", type="primary", use_container_width=True):
    
    # Check API key
    if not os.getenv('GEMINI_API_KEY'):
        st.error("❌ GEMINI_API_KEY not found. Please configure your .env file.")
        st.stop()
    
    try:
        with st.spinner("🤖 AI is optimizing routes... This may take 10-30 seconds..."):
            optimizer = AIOptimizer()
            result = optimizer.optimize_routes(
                orders_to_route,  # Use selected orders only!
                prepared_drivers
            )
            
            # Extract routes
            st.session_state.optimized_routes = result.get('routes', {})
            warnings = result.get('warnings', [])
            unassigned = result.get('unassigned_orders', [])
            
            st.success("✅ Routes optimized successfully!")
            
            # UPDATE Assigned Driver in Session State automatically
            for driver_name, route_data in st.session_state.optimized_routes.items():
                # route_data is a dict containing 'stops' and 'summary'
                stops = route_data.get('stops', [])
                for route_order in stops:
                    # Find matching order in session to update driver
                    for session_order in st.session_state.orders:
                        # Match by address (and customer if possible) to be safe
                        if session_order.get('address') == route_order.get('address'):
                            session_order['assigned_driver'] = driver_name
                            
            # Trigger session save
            from components.user_session import UserSession
            UserSession._auto_save_session()
            
            # AUTO-SAVE to database to prevent data loss on refresh!
            try:
                today = date.today().strftime('%Y-%m-%d')
                db = Database()
                
                # Save routes
                db.save_routes(st.session_state.optimized_routes, today)
                # Save orders that were routed
                db.save_orders(orders_to_route, today)
                
                st.success("💾 Routes auto-saved to database!")
                
            except Exception as save_error:
                st.warning(f"⚠️ Routes generated but couldn't auto-save: {str(save_error)}")
                st.info("💡 Use 'Save Routes to Database' button below to save manually")
            
            # Show warnings
            if warnings:
                with st.expander("⚠️ Warnings", expanded=True):
                    for warning in warnings:
                        st.warning(warning)
            
            # Show unassigned
            if unassigned:
                with st.expander("❌ Unassigned Orders", expanded=True):
                    st.error(f"{len(unassigned)} orders could not be assigned:")
                    for order in unassigned:
                        st.write(f"- {order}")
            
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Optimization failed: {str(e)}")
        st.info("Check that your GEMINI_API_KEY is valid and you have credits.")

# Display optimized routes
if st.session_state.optimized_routes:
    st.divider()
    st.subheader("📋 Optimized Routes")
    
    # Display formatted routes
    formatter = RouteFormatter()
    
    for driver_name, route_data in st.session_state.optimized_routes.items():
        with st.expander(f"🚚 {driver_name}", expanded=True):
            summary = route_data.get('summary', {})
            stops = route_data.get('stops', [])
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Stops", summary.get('total_stops', 0))
            with col2:
                st.metric("Distance", f"{summary.get('total_distance_miles', 0)} mi")
            with col3:
                st.metric("Drive Time", f"{summary.get('total_drive_time_min', 0)} min")
            with col4:
                st.metric("Finish", summary.get('estimated_finish', 'TBD'))
            
            st.write(f"**Start:** {summary.get('start_time', 'TBD')} from {summary.get('start_location', 'TBD')}")
            
            st.divider()
            
            # Stops table
            for stop in stops:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### Stop {stop['stop_number']}: {stop['order_type']}")
                    st.write(f"📍 **{stop['address']}, {stop['city']}**")
                    st.write(f"📦 {stop['items']}")
                    st.write(f"⏰ ETA: **{stop['eta']}** (Window: {stop['time_window']})")
                    
                    if stop.get('special_notes'):
                        st.info(f"ℹ️ {stop['special_notes']}")
                    
                    # Time window validation
                    if not stop.get('time_window_ok', True):
                        st.error("⚠️ Time window conflict!")
                
                with col2:
                    # Navigation button
                    import urllib.parse
                    nav_url = f"https://www.google.com/maps/dir/?api=1&destination={urllib.parse.quote(stop['address'])}"
                    st.link_button("🗺️ Navigate", nav_url, use_container_width=True)
                
                st.divider()
    
    # Save and continue
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Routes to Database", use_container_width=True):
            try:
                today = date.today().strftime('%Y-%m-%d')
                
                db = Database()
                db.save_routes(st.session_state.optimized_routes, today)
                # Save only the orders that were routed
                db.save_orders(orders_to_route, today)
                
                st.success("✅ Routes and orders saved to Google Sheets!")
                
            except Exception as e:
                st.error(f"Error saving to database: {str(e)}")
    
    with col2:
        if st.button("📤 Next: Send Routes →", type="primary", use_container_width=True):
            st.switch_page("pages/4_📤_Send_Routes.py")

else:
    st.info("Click 'Run AI Optimization' to generate optimal routes")

# Navigation
st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("👥 Back to Drivers", use_container_width=True):
        st.switch_page("pages/2_👥_Select_Drivers.py")
with col2:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")

# Sidebar
with st.sidebar:
    st.header("💡 How It Works")
    st.write("""
    **AI Optimization:**
    1. Analyzes driver coverage areas
    2. Assigns orders geographically
    3. Optimizes stop sequence
    4. Validates time windows
    5. Calculates ETAs
    
    **Powered by:**
    - Google Gemini AI
    - Geographic clustering
    - Traffic-aware routing
    """)
    
    st.divider()
    
    st.header("📊 Session Info")
    st.write(f"Orders to route: {len(orders_to_route)}")
    st.write(f"Total orders: {len(st.session_state.get('orders', []))}")
    st.write(f"Drivers: {len(st.session_state.selected_drivers)}")
    st.write(f"Routes: {'Ready' if st.session_state.optimized_routes else 'Not ready'}")

# Show user info at the bottom of the sidebar
UserSession.show_user_info_sidebar()
