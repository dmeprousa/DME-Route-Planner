"""
Order Input Component - Parse and validate orders from multiple sources
"""

import google.generativeai as genai
import pandas as pd
import os
from typing import List, Dict

class OrderInput:
    
    def __init__(self):
        """Initialize with Gemini API for text parsing"""
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    def parse_text(self, text: str) -> List[Dict]:
        """Parse order text using AI"""
        if not self.model:
            raise ValueError("GEMINI_API_KEY not configured")
        
        prompt = f"""
Extract DME delivery/pickup orders from this text.

TEXT:
{text}

Return a JSON array of orders with this structure:
[
  {{
    "order_type": "Delivery" or "Pickup",
    "customer_name": "name",
    "customer_phone": "phone or empty",
    "address": "street address",
    "city": "city",
    "zip_code": "zip",
    "items": "equipment items",
    "time_window_start": "HH:MM AM/PM or empty",
    "time_window_end": "HH:MM AM/PM or empty",
    "special_notes": "any special instructions or empty"
  }}
]

Return ONLY the JSON array, no other text.
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Clean JSON markers
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            
            import json
            orders = json.loads(result_text.strip())
            return orders
            
        except Exception as e:
            raise Exception(f"Failed to parse text: {str(e)}")
    
    def parse_file(self, uploaded_file) -> List[Dict]:
        """Parse CSV or Excel file"""
        try:
            # Determine file type
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            else:
                raise ValueError("Unsupported file type. Use CSV or Excel.")
            
            # Convert to list of dicts
            orders = df.to_dict('records')
            
            # Normalize column names
            normalized = []
            for order in orders:
                normalized.append({
                    'order_type': order.get('order_type', order.get('type', 'Delivery')),
                    'customer_name': order.get('customer_name', order.get('name', '')),
                    'customer_phone': order.get('customer_phone', order.get('phone', '')),
                    'address': order.get('address', ''),
                    'city': order.get('city', ''),
                    'zip_code': str(order.get('zip_code', order.get('zip', ''))),
                    'items': order.get('items', order.get('equipment', '')),
                    'time_window_start': order.get('time_window_start', order.get('start_time', '')),
                    'time_window_end': order.get('time_window_end', order.get('end_time', '')),
                    'special_notes': order.get('special_notes', order.get('notes', ''))
                })
            
            return normalized
            
        except Exception as e:
            raise Exception(f"Failed to parse file: {str(e)}")
    
    def validate_order(self, order: Dict) -> tuple[bool, str]:
        """Validate a single order"""
        required_fields = ['address', 'city']
        
        for field in required_fields:
            if not order.get(field):
                return False, f"Missing required field: {field}"
        
        return True, "Valid"
