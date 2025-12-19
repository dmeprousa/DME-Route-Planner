"""
WhatsApp Integration - Generate click-to-send URLs
"""

import urllib.parse
from typing import Dict

def format_route_message(driver_name: str, route_data: Dict, date: str) -> str:
    """Format route as a clean, simple WhatsApp message with basic emojis only"""
    
    summary = route_data.get('summary', {})
    stops = route_data.get('stops', [])
    
    # Header - Simple with basic emojis
    message = [
        f"*ROUTE: {date}*",
        f"*Driver:* {driver_name}",
        f"*Stops:* {len(stops)} | *Distance:* {summary.get('total_distance_miles', 0)} mi",
        "",
        "-------------------",
        ""
    ]
    
    for i, stop in enumerate(stops, 1):
        # Clean up items
        items_raw = stop.get('items', '')
        if isinstance(items_raw, str):
            items_list = [item.strip() for item in items_raw.replace('\n', ',').replace(';', ',').split(',') if item.strip()]
        else:
            items_list = items_raw if isinstance(items_raw, list) else []

        # Format items as simple comma-separated list
        items_text = ", ".join(items_list) if items_list else "N/A"
        
        # Stop type
        order_type = stop.get('order_type', 'DELIVERY').upper()
        
        # Build compact stop info
        stop_lines = [
            f"*{i}. {order_type}* ({stop.get('eta', 'TBD')})"
        ]
        
        # Address
        address = stop.get('address', '')
        city = stop.get('city', '')
        full_address = f"{address}, {city}" if city else address
        stop_lines.append(f"Location: {full_address}")
        
        # Customer info - Name and Phone
        customer_name = stop.get('customer_name', '')
        customer_phone = stop.get('customer_phone', '')
        
        if customer_name or customer_phone:
            customer_info = []
            if customer_name:
                customer_info.append(customer_name)
            if customer_phone:
                customer_info.append(f"📱 {customer_phone}")
            stop_lines.append(f"Customer: {' - '.join(customer_info)}")
        
        # Items - single line
        stop_lines.append(f"Items: {items_text}")
        
        # Time window if important
        time_window = stop.get('time_window', '')
        if time_window and time_window not in ['Anytime', 'N/A', '']:
            stop_lines.append(f"Window: {time_window}")
        
        # Notes if any
        notes = stop.get('special_notes', '')
        if notes and str(notes).lower() not in ['nan', '', 'n/a']:
            stop_lines.append(f"NOTE: {notes}")
        
        # Clean navigation link
        encoded_addr = urllib.parse.quote(full_address)
        stop_lines.append(f"Map: https://maps.google.com/?q={encoded_addr}")
        
        message.extend(stop_lines)
        message.append("")
    
    # Footer - Compact summary
    message.append("-------------------")
    message.append(f"*Finish Time:* {summary.get('estimated_finish', 'N/A')}")
    message.append("")
    message.append("Route optimized by DME AI")
    
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
