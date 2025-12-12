"""
Validators for orders, addresses, and time windows
"""

import re
from typing import Dict, Tuple

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone:
        return True  # Optional field
    
    # Remove common formatting
    clean = re.sub(r'[^\d]', '', phone)
    
    # Must be 10 digits (US)
    return len(clean) == 10

def validate_zip_code(zip_code: str) -> bool:
    """Validate zip code"""
    if not zip_code:
        return False
    
    # Remove spaces/dashes
    clean = zip_code.replace(' ', '').replace('-', '')
    
    # Must be 5 digits
    return len(clean) == 5 and clean.isdigit()

def validate_address(address: str) -> bool:
    """Basic address validation"""
    if not address or len(address) < 5:
        return False
    
    # Should contain at least a number
    return bool(re.search(r'\d', address))

def validate_time_format(time_str: str) -> bool:
    """Validate time format (HH:MM AM/PM)"""
    if not time_str:
        return True  # Optional
    
    pattern = r'^\d{1,2}:\d{2}\s?(AM|PM|am|pm)$'
    return bool(re.match(pattern, time_str.strip()))

def validate_order(order: Dict) -> Tuple[bool, str]:
    """
    Validate complete order
    
    Returns:
        (is_valid, error_message)
    """
    # Required fields
    if not order.get('address'):
        return False, "Address is required"
    
    if not validate_address(order['address']):
        return False, "Invalid address format"
    
    if not order.get('city'):
        return False, "City is required"
    
    # Optional but validated if present
    if order.get('zip_code') and not validate_zip_code(order['zip_code']):
        return False, "Invalid zip code"
    
    if order.get('customer_phone') and not validate_phone(order['customer_phone']):
        return False, "Invalid phone number"
    
    if order.get('time_window_start') and not validate_time_format(order['time_window_start']):
        return False, "Invalid start time format (use HH:MM AM/PM)"
    
    if order.get('time_window_end') and not validate_time_format(order['time_window_end']):
        return False, "Invalid end time format (use HH:MM AM/PM)"
    
    return True, "Valid"
