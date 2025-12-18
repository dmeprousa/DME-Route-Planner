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
                            session_order['stop_number'] = route_order.get('stop_number', '')
                            session_order['eta'] = route_order.get('eta', '')
                            
            # Trigger session save
            from components.user_session import UserSession
            UserSession._auto_save_session()
            
            # AUTO-SAVE to database to prevent data loss on refresh!
            try:
                today = date.today().strftime('%Y-%m-%d')
                db = Database()
                
                # Save routes
                db.save_routes(st.session_state.optimized_routes, today)
                
                # UPDATE existing orders instead of creating duplicates
                update_count = 0
                for driver_name, route_data in st.session_state.optimized_routes.items():
                    route_id = f"ROUTE-{today.replace('-', '')}-{driver_name.split()[0].upper()}"
                    stops = route_data.get('stops', [])
                    
                    for stop in stops:
                        # Try to find order_id
                        order_id = stop.get('order_id')
                        
                        # If order_id is not available, try to find it from orders_to_route
                        if not order_id or order_id == 'MANUAL':
                            # Match by address
                            for order in orders_to_route:
                                if order.get('address') == stop.get('address'):
                                    order_id = order.get('order_id')
                                    break
                        
                        # Update the order in Google Sheets
                        if order_id:
                            try:
                                success = db.update_order_driver_and_route(
                                    order_id=order_id,
                                    driver_name=driver_name,
                                    route_id=route_id,
                                    stop_number=str(stop.get('stop_number', '')),
                                    eta=stop.get('eta', '')
                                )
                                if success:
                                    update_count += 1
                            except Exception as update_err:
                                st.warning(f"⚠️ Could not update order {order_id}: {str(update_err)}")
                
                st.success(f"💾 Routes saved! Updated {update_count} orders in Google Sheets")
                
            except Exception as save_error:
                st.warning(f"⚠️ Routes generated but couldn't auto-save: {str(save_error)}")
                st.info("💡 Use 'Save Routes to Database' button below to save manually")
            
            # Save unassigned to session for persistence
            st.session_state.unassigned_orders = unassigned
            
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
    
    # Show unassigned with FORCE ADD option (MOVED HERE to persist)
    if 'unassigned_orders' in st.session_state and st.session_state.unassigned_orders:
        st.divider()
        st.subheader("⚠️ Unassigned Orders")
        
        # Better explanation
        st.warning(
            f"**{len(st.session_state.unassigned_orders)} order(s) could not be automatically assigned**\n\n"
            f"The AI was unable to assign these orders based on driver availability, coverage areas, "
            f"time windows, or capacity constraints."
        )
        
        # Helpful info box
        st.info(
            "💡 **Why some orders remain unassigned:**\n\n"
            "• **Outside Coverage Area**: Order location is outside all selected drivers' coverage zones\n"
            "• **Time Conflicts**: Delivery time window conflicts with driver's schedule\n"
            "• **Capacity Exceeded**: Driver already has maximum number of stops\n"
            f"• **Multiple Drivers Selected**: Orders are distributed across {len(st.session_state.selected_drivers)} drivers to balance workload\n\n"
            "You can manually assign these orders below using the Force Add option."
        )
        
        # Create a copy to iterate safely while modifying
        unassigned_copy = list(st.session_state.unassigned_orders)
        
        for i, order in enumerate(unassigned_copy):
            # Unique key based on index or content
            key_suffix = f"{i}_{len(unassigned_copy)}" 
            
            with st.expander(f"📦 Unassigned Order #{i+1}", expanded=True):
                # Handle if order is string or dict
                if isinstance(order, str):
                    st.warning(f"⚠️ **Reason:** {order}")
                    order_details = order
                else:
                    # Show order details in a nice format
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"**Customer:** {order.get('customer_name', 'N/A')}")
                        st.markdown(f"**Address:** {order.get('address', 'N/A')}")
                        st.markdown(f"**City:** {order.get('city', 'N/A')}")
                    with col_b:
                        st.markdown(f"**Order Type:** {order.get('order_type', 'N/A')}")
                        st.markdown(f"**Time Window:** {order.get('time_window', 'N/A')}")
                        st.markdown(f"**Items:** {order.get('items', 'N/A')}")
                    
                    # Show possible reason
                    if order.get('unassigned_reason'):
                        st.error(f"❌ **Reason:** {order.get('unassigned_reason')}")
                    else:
                        st.error("❌ **Reason:** Could not match with any driver's coverage area or schedule")
                    
                    order_details = str(order)
                
                st.divider()
                    
                col1, col2 = st.columns([2, 1])
                with col1:
                    target_driver = st.selectbox(
                        "🚚 Manually Assign to Driver",
                        options=[d['driver_name'] for d in st.session_state.selected_drivers],
                        key=f"force_driver_{key_suffix}",
                        help="Select a driver to manually add this order to their route"
                    )
                
                with col2:
                    if st.button("➕ Force Add to Route", key=f"force_btn_{key_suffix}", type="primary"):
                        # Logic to add to optimized_routes
                        if target_driver in st.session_state.optimized_routes:
                            # Create a new stop object
                            new_stop = {
                                "stop_number": 999,
                                "order_id": "MANUAL",
                                "order_type": "Manual Add",
                                "address": order_details,
                                "city": "Unknown",
                                "items": "Manually Added",
                                "time_window": "Manual",
                                "eta": "Manual",
                                "special_notes": "⚠️ Manually added by dispatcher"
                            }
                            
                            # If order was a dict, try to get better data
                            if isinstance(order, dict):
                                new_stop.update({
                                    "order_id": order.get('order_id', 'MANUAL'),
                                    "address": order.get('address', 'Unknown Address'),
                                    "city": order.get('city', ''),
                                    "items": order.get('items', ''),
                                    "time_window": order.get('time_window', ''),
                                })
                            
                            # Append to stops
                            driver_route = st.session_state.optimized_routes[target_driver]
                            if 'stops' not in driver_route:
                                driver_route['stops'] = []
                            
                            # Fix stop number
                            new_stop['stop_number'] = len(driver_route['stops']) + 1
                            driver_route['stops'].append(new_stop)
                            
                            # Update summary
                            if 'summary' not in driver_route:
                                driver_route['summary'] = {}
                            driver_route['summary']['total_stops'] = len(driver_route['stops'])
                            
                            # Remove from session unassigned list
                            st.session_state.unassigned_orders.pop(i)
                            
                            # Trigger session save logic
                            from components.user_session import UserSession
                            UserSession._auto_save_session()
                            
                            st.success(f"Added to {target_driver}'s route!")
                            st.rerun()
                        else:
                            st.error("Driver route not found.")
    
    # Save and continue
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Routes to Database", use_container_width=True):
            try:
                today = date.today().strftime('%Y-%m-%d')
                
                db = Database()
                db.save_routes(st.session_state.optimized_routes, today)
                
                # UPDATE existing orders instead of creating duplicates
                update_count = 0
                for driver_name, route_data in st.session_state.optimized_routes.items():
                    route_id = f"ROUTE-{today.replace('-', '')}-{driver_name.split()[0].upper()}"
                    stops = route_data.get('stops', [])
                    
                    for stop in stops:
                        order_id = stop.get('order_id')
                        
                        # Try to find order_id from orders_to_route if not in stop
                        if not order_id or order_id == 'MANUAL':
                            for order in orders_to_route:
                                if order.get('address') == stop.get('address'):
                                    order_id = order.get('order_id')
                                    break
                        
                        if order_id:
                            try:
                                success = db.update_order_driver_and_route(
                                    order_id=order_id,
                                    driver_name=driver_name,
                                    route_id=route_id,
                                    stop_number=str(stop.get('stop_number', '')),
                                    eta=stop.get('eta', '')
                                )
                                if success:
                                    update_count += 1
                            except Exception as update_err:
                                st.warning(f"⚠️ Could not update order {order_id}: {str(update_err)}")
                
                st.success(f"✅ Routes saved! Updated {update_count} orders in Google Sheets")
                
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
