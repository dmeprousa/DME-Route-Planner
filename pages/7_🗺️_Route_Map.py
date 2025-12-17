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
def load_data(date_obj):
    try:
        db = Database()
        date_str = date_obj.strftime('%Y-%m-%d')
        orders = db.get_orders(date=date_str)
        return orders
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return []

orders = load_data(selected_date)

if not orders:
    st.info("No orders found for this date.")
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
col_map, col_details = st.columns([3, 1])

with col_map:
    st_folium(m, width="100%", height=600)

with col_details:
    st.subheader("Stats")
    st.metric("📍 Mapped Stops", len(valid_orders))
    st.metric("⚠️ Unmapped", len(unmapped_orders))
    
    st.divider()
    if unmapped_orders:
        with st.expander("Unmapped Orders (Missing Coords)"):
            status_df = pd.DataFrame(unmapped_orders)
            if 'address' in status_df.columns:
                st.dataframe(status_df[['customer_name', 'address']], hide_index=True)
            else:
                 st.dataframe(status_df, hide_index=True)

