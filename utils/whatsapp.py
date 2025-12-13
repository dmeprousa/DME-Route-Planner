"""
WhatsApp Integration - Generate click-to-send URLs
"""

import urllib.parse
from typing import Dict

def format_route_message(driver_name: str, route_data: Dict, date: str) -> str:
    """Format route as a clean, vertical WhatsApp message with bullet points"""
    
    summary = route_data.get('summary', {})
    stops = route_data.get('stops', [])
    
    # Header
    message = [
        f"📅 *ROUTE: {date}*",
        f"👤 *Driver:* {driver_name}",
        f"🛑 *Stops:* {len(stops)}",
        "__________________________",
        ""
    ]
    
    for stop in stops:
        # Clean up items list
        items_raw = stop.get('items', '')
        if isinstance(items_raw, str):
            # Split items intelligently (handle comma or newlines)
            # Remove empty strings and spaces
            items_list = [i.strip() for i in items_raw.replace('\n', ',').replace(';', ',').split(',') if i.strip()]
        else:
            items_list = items_raw if isinstance(items_raw, list) else []

        # Bullet points for items
        items_formatted = "\n".join([f"   • {item}" for item in items_list])
        
        # Stop Header
        order_type = stop.get('order_type', 'STOP').upper()
        
        # Navigation Link
        # Using /search/ is sometimes safer for mobile linking than /dir/ if starting point is ambiguous
        encoded_addr = urllib.parse.quote(stop['address'])
        nav_url = f"https://www.google.com/maps/search/?api=1&query={encoded_addr}"
        
        # Build Stop Block
        stop_block = [
            f"*{stop['stop_number']}. {order_type}* ({stop.get('eta', '')})",
            f"📍 {stop['address']}",
        ]
        
        # Items Section
        if items_formatted:
            stop_block.append(f"📦 *Items:*")
            stop_block.append(items_formatted)
        
        # Notes Section
        notes = stop.get('special_notes')
        if notes and str(notes).lower() != 'nan' and str(notes).strip():
            stop_block.append(f"📝 *Note:* {notes}")
            
        stop_block.append(f"🔗 Map: {nav_url}")
        
        message.extend(stop_block)
        message.append("")
        message.append("__________________________")
        message.append("")
        
    # Footer
    message.append(f"⛽ Miles: {summary.get('total_distance_miles', 0)}")
    message.append(f"🏁 Finish: {summary.get('estimated_finish', 'N/A')}")
    message.append("")
    message.append("✅ Route optimized by DME AI")
    
    return "\n".join(message)


def create_whatsapp_url(phone: str, message: str) -> str:
    """Create WhatsApp click-to-send URL"""
    
    # Clean phone number
    if not phone:
        return ""
        
    clean_phone = str(phone).replace('+1', '').replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # URL encode
    encoded_message = urllib.parse.quote(message)
    
    # Create URL
    return f"https://wa.me/1{clean_phone}?text={encoded_message}"
