"""
Order Input Component - Parse and validate orders from multiple sources
"""

import google.generativeai as genai
import pandas as pd
from PIL import Image
import io
import os
from typing import List, Dict

class OrderInput:
    
    def __init__(self):
        """Initialize with Gemini API for text parsing"""
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
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

Return a JSON array of orders with this EXACT structure (use these specific keys):
[
  {{
    "order_type": "Delivery" or "Pickup",
    "customer": "Full Name (look for capitalized names)",
    "phone": "Phone Number (extract any 10-digit number format)",
    "address": "Street Address",
    "city": "City Name",
    "zip_code": "Zip Code",
    "items": "Comma separated equipment list",
    "time_window": "Single string e.g. '10am-2pm' (combine start/end)",
    "notes": "Any special instructions or gate codes"
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
            # Fallback for Model Name Errors (like 404 for gemini-2.5)
            if "404" in str(e) or "not found" in str(e).lower():
                try:
                    import streamlit as st
                    st.warning("⚠️ Model 'gemini-2.5-flash' not found. Falling back to 'gemini-1.5-flash'...")
                    fallback_model = genai.GenerativeModel('gemini-1.5-flash')
                    response = fallback_model.generate_content(prompt)
                    # Process fallback response
                    result_text = response.text.strip()
                    if '```json' in result_text:
                         result_text = result_text.split('```json')[1].split('```')[0]
                    elif '```' in result_text:
                        result_text = result_text.split('```')[1].split('```')[0]
                    import json
                    return json.loads(result_text.strip())
                except Exception as fallback_error:
                    raise Exception(f"Fallback failed too: {str(fallback_error)}")
            
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
                    'customer': order.get('customer', order.get('customer_name', order.get('name', ''))),
                    'phone': order.get('phone', order.get('customer_phone', '')),
                    'address': order.get('address', ''),
                    'city': order.get('city', ''),
                    'zip_code': str(order.get('zip_code', order.get('zip', ''))),
                    'items': order.get('items', order.get('equipment', '')),
                    'time_window': order.get('time_window', f"{order.get('time_window_start', '')} - {order.get('time_window_end', '')}".strip(' - ')),
                    'notes': order.get('notes', order.get('special_notes', ''))
                })
            
            return normalized
            
        except Exception as e:
            raise Exception(f"Failed to parse file: {str(e)}")

    def parse_image(self, uploaded_file) -> List[Dict]:
        """Parse order data from an image using Gemini Vision"""
        if not self.model:
            raise ValueError("GEMINI_API_KEY not configured")
            
        try:
            # Open the image using Pillow
            image = Image.open(uploaded_file)
            
            prompt = """
            Look at this image containing delivery or pickup orders.
            Extract all order details into a structured JSON format.
            
            Return a JSON array of orders with this logic:
            - If multiple orders are visible, extract all of them.
            - If a field is missing, use an empty string "".
            - infer 'order_type' as 'Delivery' unless 'Pickup' or 'Exchange' is mentioned.
            
            JSON Structure (Use these EXACT keys):
            [
              {
                "order_type": "Delivery" or "Pickup",
                "customer": "Full Name",
                "phone": "Phone Number",
                "address": "street address",
                "city": "city",
                "zip_code": "zip code",
                "items": "items list comma separated",
                "time_window": "Single string e.g. '10am-2pm'",
                "notes": "special instructions"
              }
            ]
            
            Return ONLY the valid JSON array. No markdown code blocks, no extra text.
            """
            
            # Send both prompt and image to the model
            response = self.model.generate_content([prompt, image])
            result_text = response.text.strip()
            
            # Clean JSON markers (Gemini loves markdown)
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            
            import json
            orders = json.loads(result_text.strip())
            return orders
            
        except Exception as e:
            # Fallback logic could be added here similar to parse_text if needed
            raise Exception(f"Failed to parse image: {str(e)}")
    
    def validate_order(self, order: Dict) -> tuple[bool, str]:
        """Validate a single order"""
        required_fields = ['address', 'city']
        
        for field in required_fields:
            if not order.get(field):
                return False, f"Missing required field: {field}"
        
        return True, "Valid"
