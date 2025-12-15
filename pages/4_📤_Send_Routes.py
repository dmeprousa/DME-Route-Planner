"""
Page 4: Send Routes
Send routes via WhatsApp and generate PDFs
"""

import sys
import os
# Add project root to path for proper imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from datetime import date
from utils.whatsapp import create_whatsapp_url, format_route_message
from utils.pdf_generator import generate_route_pdf
from components.route_formatter import RouteFormatter
from components.user_session import UserSession

st.set_page_config(page_title="Send Routes", page_icon="📤", layout="wide")

# Require authentication
UserSession.require_auth()

st.title("📤 Send Routes")
st.caption("Send routes to drivers via WhatsApp or download as PDF")

# Check if routes exist
if 'optimized_routes' not in st.session_state or not st.session_state.optimized_routes:
    st.warning("⚠️ No optimized routes found. Please optimize routes first.")
    if st.button("🤖 Go to Optimize Routes"):
        st.switch_page("pages/3_🤖_Optimize_Routes.py")
    st.stop()

today = date.today().strftime('%Y-%m-%d')
today_formatted = date.today().strftime('%B %d, %Y')

st.subheader(f"📅 Routes for {today_formatted}")

st.divider()

# For each driver's route
for driver_name, route_data in st.session_state.optimized_routes.items():
    
    with st.expander(f"🚚 {driver_name}", expanded=True):
        summary = route_data.get('summary', {})
        
        # Quick summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Stops", summary.get('total_stops', 0))
        with col2:
            st.metric("Distance", f"{summary.get('total_distance_miles', 0)} mi")
        with col3:
            st.metric("Est. Finish", summary.get('estimated_finish', 'TBD'))
        
        st.divider()
        
        # WhatsApp section
        st.subheader("📱 WhatsApp")
        
        # Find driver phone
        driver_phone = ""
        if 'selected_drivers' in st.session_state:
            for driver in st.session_state.selected_drivers:
                if driver.get('driver_name') == driver_name:
                    driver_phone = driver.get('phone', '')
                    break
        
        # Phone input
        phone_input = st.text_input(
            "Driver Phone Number",
            value=driver_phone,
            key=f"phone_{driver_name}",
            placeholder="760-123-4567"
        )
        
        # Preview message
        whatsapp_message = format_route_message(driver_name, route_data, today_formatted)
        
        with st.expander("📝 Preview WhatsApp Message"):
            st.text(whatsapp_message)
        
        # Send button
        if phone_input:
            whatsapp_url = create_whatsapp_url(phone_input, whatsapp_message)
            col1, col2 = st.columns(2)
            
            with col1:
                st.link_button(
                    "📲 Send via WhatsApp",
                    whatsapp_url,
                    use_container_width=True,
                    type="primary"
                )
            
            with col2:
                # Copy to clipboard button (using st.code)
                if st.button("📋 Copy Message", key=f"copy_{driver_name}", use_container_width=True):
                    st.code(whatsapp_message, language=None)
                    st.success("Message displayed above - copy manually")
        else:
            st.warning("Enter phone number to send via WhatsApp")
        
        st.divider()
        
        # PDF section
        st.subheader("📄 PDF Download")
        
        try:
            pdf_bytes = generate_route_pdf(driver_name, route_data, today_formatted)
            
            st.download_button(
                label="⬇️ Download PDF Route Sheet",
                data=pdf_bytes,
                file_name=f"route_{driver_name.replace(' ', '_')}_{today}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")

st.divider()

# Bulk actions
st.subheader("🚀 Bulk Actions")

col1, col2 = st.columns(2)

with col1:
    if st.button("📱 Open All WhatsApp Links", use_container_width=True):
        # Generate all links
        links_html = "<h3>WhatsApp Links</h3>"
        
        for driver_name, route_data in st.session_state.optimized_routes.items():
            # Find phone
            driver_phone = ""
            if 'selected_drivers' in st.session_state:
                for driver in st.session_state.selected_drivers:
                    if driver.get('driver_name') == driver_name:
                        driver_phone = driver.get('phone', '')
                        break
            
            if driver_phone:
                message = format_route_message(driver_name, route_data, today_formatted)
                url = create_whatsapp_url(driver_phone, message)
                links_html += f'<p><a href="{url}" target="_blank">📲 Send to {driver_name}</a></p>'
        
        st.markdown(links_html, unsafe_allow_html=True)

with col2:
    if st.button("📄 Download All PDFs", use_container_width=True):
        st.info("Individual downloads available above (browser limitation prevents bulk download)")

st.divider()

# Display all routes summary
st.subheader("📊 Routes Summary")

formatter = RouteFormatter()
summary_df = formatter.format_stops_as_dataframe(st.session_state.optimized_routes)

st.dataframe(summary_df, use_container_width=True)

# Download summary as CSV
csv = summary_df.to_csv(index=False)
st.download_button(
    "⬇️ Download Summary CSV",
    csv,
    f"routes_summary_{today}.csv",
    "text/csv",
    use_container_width=True
)

st.divider()

# Navigation
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🤖 Back to Optimization", use_container_width=True):
        st.switch_page("pages/3_🤖_Optimize_Routes.py")

with col2:
    if st.button("📊 View History", use_container_width=True):
        st.switch_page("pages/5_📊_History.py")

with col3:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")

# Sidebar
with st.sidebar:
    st.header("💡 Tips")
    st.write("""
    **WhatsApp:**
    - Click "Send via WhatsApp" to open chat
    - Message is pre-filled and ready to send
    - Works on mobile and desktop
    
    **PDF:**
    - Professional route sheet
    - Printable format
    - Contains all stop details
    
    **Best Practice:**
    - Send WhatsApp for immediate access
    - Provide PDF as backup
    """)
    
    st.divider()
    
    st.header("📞 Support")
    st.info("Questions?\nCall: 760-879-1071")
