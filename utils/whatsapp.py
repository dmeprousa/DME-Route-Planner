"""
WhatsApp Integration - Generate click-to-send URLs
"""

import urllib.parse
from typing import Dict

def format_route_message(driver_name: str, route_data: Dict, date: str) -> str:
    """Format route as WhatsApp message"""
    
    summary = route_data.get('summary', {})
    stops = route_data.get('stops', [])
    
    message = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚚 YOUR ROUTE - {date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 SUMMARY
Total Stops: {summary.get('total_stops', 0)}
Distance: {summary.get('total_distance_miles', 0)} miles
Drive Time: {summary.get('total_drive_time_min', 0)} min
Stop Time: {summary.get('total_stop_time_min', 0)} min
Start: {summary.get('start_time', 'TBD')} from {summary.get('start_location', 'TBD')}
Finish: {summary.get('estimated_finish', 'TBD')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    for stop in stops:
        nav_url = f"https://www.google.com/maps/dir/?api=1&destination={urllib.parse.quote(stop['address'])}"
        
        message += f"""
{stop['stop_number']}. 📦 {stop['order_type'].upper()}
   📍 {stop['address']}
   ⏰ ETA: {stop['eta']}
   📦 Items: {stop['items']}
   🕐 Window: {stop['time_window']}
   {f"⚠️ {stop['special_notes']}" if stop.get('special_notes') else ''}
   
   Navigate: {nav_url}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    message += "\n✅ Route optimized by DME AI\n📱 Questions? Call Cyrus: 760-879-1071"
    
    return message


def create_whatsapp_url(phone: str, message: str) -> str:
    """Create WhatsApp click-to-send URL"""
    
    # Clean phone number
    clean_phone = phone.replace('+1', '').replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # URL encode
    encoded_message = urllib.parse.quote(message)
    
    # Create URL
    return f"https://wa.me/1{clean_phone}?text={encoded_message}"
