"""
Page 7: Route Map
Visual dashboard for tracking drivers and routes on a map.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from datetime import date
from components.database import Database
from components.user_session import UserSession
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster, Fullscreen

st.set_page_config(page_title="Route Map", page_icon="🗺️", layout="wide")

# Require authentication
UserSession.require_auth()

st.title("🗺️ Route Visualization")
st.caption("Visual tracking of drivers and delivery routes")

# --- Filters ---
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    selected_date = st.date_input("Select Date", value=date.today())
with col2:
    view_mode = st.radio("View Mode", ["All Drivers", "Single Driver"], horizontal=True)
with col3:
    if st.button("🔄 Refresh"):
        st.rerun()

# --- Load Data ---
@st.cache_data(ttl=60)
def load_data_from_db(date_obj):
    try:
        db = Database()
        date_str = date_obj.strftime('%Y-%m-%d')
        orders = db.get_orders(date=date_str)
        return orders
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return []

# Smart data loading: Always respect the selected date
def load_orders_for_map(date_obj):
    """
    Load orders for map visualization.
    Priority:
    1. If date is today and session state has data, use it
    2. Otherwise load from database
    """
    from datetime import date as date_class
    
    date_str = date_obj.strftime('%Y-%m-%d')
    today_str = date_class.today().strftime('%Y-%m-%d')
    
    # Check if we're looking at today's date
    is_today = (date_str == today_str)
    
    # Option 1: For today's date, prefer session state (contains latest unsaved changes)
    if is_today:
        # Try optimized routes first
        if 'optimized_routes' in st.session_state and st.session_state.optimized_routes:
            st.info("📍 Showing routes from current optimization session")
            orders = []
            for driver_name, route_data in st.session_state.optimized_routes.items():
                stops = route_data.get('stops', [])
                for stop in stops:
                    # Try to find the actual order in session_state.orders to get real status
                    actual_status = 'pending'  # default
                    for session_order in st.session_state.get('orders', []):
                        address_match = session_order.get('address', '').strip().lower() == stop.get('address', '').strip().lower()
                        customer_match = session_order.get('customer_name', '').strip().lower() == stop.get('customer_name', '').strip().lower()
                        if address_match and customer_match:
                            actual_status = session_order.get('status', 'pending')
                            break
                    
                    order = {
                        'customer_name': stop.get('customer_name', 'Unknown'),
                        'address': stop.get('address', ''),
                        'city': stop.get('city', ''),
                        'assigned_driver': driver_name,
                        'stop_number': stop.get('stop_number', ''),
                        'status': actual_status,  # Use actual status from session
                        'order_type': stop.get('order_type', ''),
                        'items': stop.get('items', ''),
                        'time_window': stop.get('time_window', ''),
                    }
                    
                    coords = stop.get('coordinates', {})
                    if coords and coords.get('lat') and coords.get('lng'):
                        order['lat'] = coords.get('lat')
                        order['lng'] = coords.get('lng')
                    
                    orders.append(order)
            
            if orders:
                return orders
        
        # Try session state orders
        if 'orders' in st.session_state and st.session_state.orders:
            st.info("📍 Showing orders from current session")
            return st.session_state.orders
    
    # Option 2: Load from database for historical dates or if no session data
    st.info(f"📍 Loading orders from database for {date_str}")
    return load_data_from_db(date_obj)

orders = load_orders_for_map(selected_date)

if not orders:
    st.warning("⚠️ No orders found for this date")
    st.info("Go to 'Optimize Routes' to create routes, or 'Input Orders' to add new orders")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🤖 Optimize Routes"):
            st.switch_page("pages/3_🤖_Optimize_Routes.py")
    with col2:
        if st.button("📦 Input Orders"):
            st.switch_page("pages/1_📦_Input_Orders.py")
    st.stop()

df = pd.DataFrame(orders)

# Helper: Extract Lat/Lng
# Database saves them as extra columns but get_orders might not label them if header is missing
# We rely on convention: last 2 columns might be lat/lng if we appended them
# Or if we have them in the dict if get_all_records picked them up (if user added headers 'lat', 'lng')

# Let's check what columns we have
cols = df.columns.tolist()
# If 'lat' and 'lng' are not in columns, we might need to look at indices or assume raw data?
# gspread get_all_records uses first row as keys.
# If I just started appending columns, the header might not exist.
# For now, let's assume 'lat' and 'lng' might NOT work for old data.
# WE WILL USE 'coordinates' keys if they exist (from session state logic before save?)
# No, we loaded from DB.

# Try to find lat/lng columns
lat_col = next((c for c in cols if str(c).lower() in ['lat', 'latitude']), None)
lng_col = next((c for c in cols if str(c).lower() in ['lng', 'lon', 'longitude']), None)

# If not found, maybe they are empty keys? (gspread behavior with no header)
# This is tricky. 
# Plan B: Fallback to simple visualization if no coords.

valid_orders = []
unmapped_orders = []

for idx, row in df.iterrows():
    lat = None
    lng = None
    
    # Try generic columns
    if lat_col and lng_col:
        try:
            lat = float(row[lat_col])
            lng = float(row[lng_col])
        except:
            pass
            
    # Try dictionary access if nested (unlikely from flat sheet)
    
    if lat and lng:
        # Valid coordinate
        order_data = row.to_dict()
        order_data['lat'] = lat
        order_data['lng'] = lng
        valid_orders.append(order_data)
    else:
        unmapped_orders.append(row)

# Start Map
# Default location: Southern California (approximate center)
m = folium.Map(location=[34.0522, -118.2437], zoom_start=10)
Fullscreen().add_to(m)

# Group by Driver
if 'assigned_driver' in df.columns:
    drivers = [d for d in df['assigned_driver'].unique() if d]
else:
    drivers = []

selected_driver_filter = None

if view_mode == "Single Driver":
    if drivers:
        selected_driver_filter = st.selectbox("Select Driver", drivers)
    else:
        st.info("No drivers found for this date.")

# Define colors for drivers
colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']

for i, driver in enumerate(drivers):
    if not driver:
        continue
        
    # Apply Filter
    if selected_driver_filter and driver != selected_driver_filter:
        continue
            
    driver_color = colors[i % len(colors)]
    
    # Get driver orders
    driver_orders = [o for o in valid_orders if o.get('assigned_driver') == driver]
    
    if not driver_orders:
        continue

    # Sort by stop number
    try:
        driver_orders.sort(key=lambda x: int(x.get('stop_number', 0)) if x.get('stop_number') else 999)
    except:
        pass # Sort failed, keep order
        
    # Create FeatureGroup
    fg = folium.FeatureGroup(name=f"🚚 {driver}")
    
    route_points = []
    
    for order in driver_orders:
        lat = order['lat']
        lng = order['lng']
        route_points.append([lat, lng])
        
        status = order.get('status', 'pending')
        # Icon based on status
        icon_color = driver_color
        if status == 'delivered':
            icon_color = 'green'
        
        popup_html = f"""
        <b>{driver}</b><br>
        Stop: {order.get('stop_number')}<br>
        Customer: {order.get('customer_name')}<br>
        Status: {status}
        """
        
        folium.Marker(
            [lat, lng],
            popup=popup_html,
            tooltip=f"{driver} - Stop {order.get('stop_number')}",
            icon=folium.Icon(color=icon_color, icon='info-sign')
        ).add_to(fg)
        
    # Draw Line
    if len(route_points) > 1:
        folium.PolyLine(
            route_points,
            color=driver_color,
            weight=3,
            opacity=0.8
        ).add_to(fg)
        
    fg.add_to(m)

# Add Unassigned/No Driver orders
unassigned_mapped = [o for o in valid_orders if not o.get('assigned_driver')]
if unassigned_mapped:
    fg_un = folium.FeatureGroup(name="❓ Unassigned")
    for order in unassigned_mapped:
        folium.Marker(
            [order['lat'], order['lng']],
            popup=f"Unassigned<br>{order.get('address')}",
            icon=folium.Icon(color='gray', icon='question-sign')
        ).add_to(fg_un)
    fg_un.add_to(m)

folium.LayerControl().add_to(m)

# Layout
st_folium(m, width="100%", height=600)

# --- Stats Section ---
st.divider()

col_stats1, col_stats2, col_stats3 = st.columns(3)
with col_stats1:
    st.metric("📍 Total Stops", len(valid_orders))
with col_stats2:
    st.metric("🚚 Active Drivers", len(drivers))
with col_stats3:
    st.metric("⚠️ Unmapped", len(unmapped_orders))

# --- Driver Details Table ---
if drivers:
    st.subheader("📊 Driver Route Details")
    
    # Calculate stats for each driver
    driver_stats = []
    for driver in drivers:
        if not driver:
            continue
            
        driver_orders = [o for o in valid_orders if o.get('assigned_driver') == driver]
        
        if not driver_orders:
            continue
        
        # Count statuses
        total_stops = len(driver_orders)
        delivered = len([o for o in driver_orders if o.get('status', '').lower() == 'delivered'])
        pending = total_stops - delivered
        
        # Calculate completion percentage
        completion = (delivered / total_stops * 100) if total_stops > 0 else 0
        
        # Estimate route distance (simplified - sum of distances between consecutive stops)
        distance_km = 0
        sorted_orders = sorted(driver_orders, key=lambda x: int(x.get('stop_number', 0)) if x.get('stop_number') else 999)
        
        for i in range(len(sorted_orders) - 1):
            try:
                lat1, lng1 = sorted_orders[i]['lat'], sorted_orders[i]['lng']
                lat2, lng2 = sorted_orders[i + 1]['lat'], sorted_orders[i + 1]['lng']
                
                # Haversine formula for distance
                from math import radians, cos, sin, asin, sqrt
                
                lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
                dlng = lng2 - lng1
                dlat = lat2 - lat1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
                c = 2 * asin(sqrt(a))
                km = 6371 * c  # Radius of earth in kilometers
                distance_km += km
            except:
                pass
        
        # Estimate time (assume 30 min per stop + travel time)
        # Average speed: 40 km/h in city
        travel_time_hours = distance_km / 40 if distance_km > 0 else 0
        stop_time_hours = (total_stops * 30) / 60  # 30 min per stop
        total_time_hours = travel_time_hours + stop_time_hours
        
        # Get first and last stops
        first_stop = sorted_orders[0].get('customer_name', 'N/A') if sorted_orders else 'N/A'
        last_stop = sorted_orders[-1].get('customer_name', 'N/A') if sorted_orders else 'N/A'
        
        driver_stats.append({
            'Driver': driver,
            'Total Stops': total_stops,
            'Delivered': delivered,
            'Pending': pending,
            'Completion': f"{completion:.0f}%",
            'Distance (km)': f"{distance_km:.1f}",
            'Est. Time (hrs)': f"{total_time_hours:.1f}",
            'First Stop': first_stop,
            'Last Stop': last_stop
        })
    
    if driver_stats:
        # Create DataFrame
        stats_df = pd.DataFrame(driver_stats)
        
        # Display as styled table
        st.dataframe(
            stats_df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Driver": st.column_config.TextColumn("🚚 Driver", width="medium"),
                "Total Stops": st.column_config.NumberColumn("📍 Stops", width="small"),
                "Delivered": st.column_config.NumberColumn("✅ Done", width="small"),
                "Pending": st.column_config.NumberColumn("⏳ Pending", width="small"),
                "Completion": st.column_config.ProgressColumn("📊 Progress", width="medium", format="%s", min_value=0, max_value=100),
                "Distance (km)": st.column_config.TextColumn("📏 Distance", width="small"),
                "Est. Time (hrs)": st.column_config.TextColumn("⏱️ Time", width="small"),
                "First Stop": st.column_config.TextColumn("🏁 First", width="medium"),
                "Last Stop": st.column_config.TextColumn("🏁 Last", width="medium"),
            }
        )
        
        # Add download button
        csv = stats_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Route Stats",
            data=csv,
            file_name=f"driver_stats_{selected_date.strftime('%Y-%m-%d')}.csv",
            mime="text/csv",
        )

# --- Unmapped Orders ---
if unmapped_orders:
    st.divider()
    with st.expander(f"⚠️ Unmapped Orders ({len(unmapped_orders)})"):
        st.caption("These orders are missing GPS coordinates and cannot be displayed on the map.")
        status_df = pd.DataFrame(unmapped_orders)
        
        # Check which columns are available and display accordingly
        available_cols = []
        if 'customer_name' in status_df.columns:
            available_cols.append('customer_name')
        if 'address' in status_df.columns:
            available_cols.append('address')
        if 'city' in status_df.columns:
            available_cols.append('city')
        
        if available_cols:
            st.dataframe(status_df[available_cols], hide_index=True, use_container_width=True)
        else:
            st.dataframe(status_df, hide_index=True, use_container_width=True)

