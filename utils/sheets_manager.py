"""
Google Sheets Manager for Data Persistence
Handles sync between app and Google Sheets
"""

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import streamlit as st
import json
import os


class SheetsManager:
    def __init__(self):
        """Initialize connection to Google Sheets"""
        from google.oauth2 import service_account
        from google.oauth2.credentials import Credentials
        
        creds = None
        
        try:
            # Priority 1: Try Service Account from Streamlit Secrets
            if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
                try:
                    # Check if it's a dict or a string
                    if isinstance(st.secrets["gcp_service_account"], str):
                        service_account_info = json.loads(st.secrets["gcp_service_account"])
                    else:
                        service_account_info = st.secrets["gcp_service_account"]
                    
                    SCOPES = [
                        'https://spreadsheets.google.com/feeds',
                        'https://www.googleapis.com/auth/drive'
                    ]
                    
                    creds = service_account.Credentials.from_service_account_info(
                        service_account_info, scopes=SCOPES
                    )
                except Exception as e:
                    st.warning(f"Could not load service account: {str(e)}")
            
            # Priority 2: Try OAuth from Streamlit Secrets (gcp_oauth)
            if not creds and hasattr(st, 'secrets') and 'gcp_oauth' in st.secrets:
                try:
                    oauth_info = st.secrets["gcp_oauth"]
                    
                    # Use scopes from secrets if available, otherwise default
                    if "scopes" in oauth_info:
                        SCOPES = oauth_info["scopes"]
                    else:
                        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
                    
                    creds = Credentials(
                        token=oauth_info.get("token"),
                        refresh_token=oauth_info.get("refresh_token"),
                        token_uri=oauth_info.get("token_uri"),
                        client_id=oauth_info.get("client_id"),
                        client_secret=oauth_info.get("client_secret"),
                        scopes=SCOPES
                    )
                except Exception as e:
                    st.warning(f"Could not load OAuth credentials: {str(e)}")
            
            # Priority 3: Try local credentials.json (for local development)
            if not creds:
                creds_path = 'credentials.json'
                if os.path.exists(creds_path):
                    try:
                        SCOPES = [
                            'https://spreadsheets.google.com/feeds',
                            'https://www.googleapis.com/auth/drive'
                        ]
                        
                        with open(creds_path, 'r') as f:
                            creds_dict = json.load(f)
                        creds = service_account.Credentials.from_service_account_info(
                            creds_dict, scopes=SCOPES
                        )
                    except Exception as e:
                        st.warning(f"Could not read credentials.json: {str(e)}")
            
            # If no credentials found anywhere
            if not creds:
                st.warning("⚠️ Google Sheets credentials not configured. Add 'gcp_oauth' or 'gcp_service_account' to Streamlit Secrets.")
                self.client = None
                self.spreadsheet = None
                return
            
            # Authorize with gspread (NEW method - fixes deprecation warning)
            from gspread.http_client import HTTPClient
            http_client = HTTPClient(creds)
            self.client = gspread.Client(auth=creds, http_client=http_client)
            
            # Get the sheet ID
            if hasattr(st, 'secrets') and 'GOOGLE_SHEET_ID' in st.secrets:
                sheet_id = st.secrets['GOOGLE_SHEET_ID']
            else:
                sheet_id = '1mwSH2hFmggSjxBnkqbIZARylMd_3fXtrF2M0pTgrJe0'
            
            self.spreadsheet = self.client.open_by_key(sheet_id)
            
        except Exception as e:
            st.error(f"❌ Failed to connect to Google Sheets: {str(e)}")
            self.client = None
            self.spreadsheet = None
    
    def get_worksheet(self, name):
        """Get or create a worksheet by name"""
        if not self.spreadsheet:
            return None
        
        try:
            return self.spreadsheet.worksheet(name)
        except gspread.WorksheetNotFound:
            # Create the worksheet if it doesn't exist
            return self.spreadsheet.add_worksheet(title=name, rows=1000, cols=20)
    
    def save_pending_orders(self, orders, username):
        """Save pending orders to PENDING_ORDERS sheet"""
        if not self.spreadsheet:
            return False
        
        try:
            worksheet = self.get_worksheet('PENDING_ORDERS')
            
            # Clear existing data for this user
            all_values = worksheet.get_all_records()
            
            # Filter out orders from this user
            filtered = [row for row in all_values if row.get('username') != username]
            
            # Add new orders
            for order in orders:
                order_row = {
                    'username': username,
                    'added_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'selected': 'FALSE',  # Default to not selected
                    'order_type': order.get('order_type', 'Delivery'),
                    'customer_name': order.get('customer_name', ''),
                    'customer_phone': order.get('customer_phone', ''),
                    'address': order.get('address', ''),
                    'city': order.get('city', ''),
                    'zip_code': order.get('zip_code', ''),
                    'items': order.get('items', ''),
                    'time_window_start': order.get('time_window_start', ''),
                    'time_window_end': order.get('time_window_end', ''),
                    'special_notes': order.get('special_notes', '')
                }
                filtered.append(order_row)
            
            # Clear sheet and write headers + data
            if filtered:
                df = pd.DataFrame(filtered)
                worksheet.clear()
                worksheet.update([df.columns.values.tolist()] + df.values.tolist())
            
            return True
        except Exception as e:
            st.error(f"Failed to save orders: {str(e)}")
            return False
    
    def load_pending_orders(self, username):
        """Load pending orders for a specific user"""
        if not self.spreadsheet:
            return []
        
        try:
            worksheet = self.get_worksheet('PENDING_ORDERS')
            all_records = worksheet.get_all_records()
            
            # Filter by username
            user_orders = [row for row in all_records if row.get('username') == username]
            return user_orders
        except Exception as e:
            st.warning(f"Could not load pending orders: {str(e)}")
            return []
    
    def update_selection_status(self, username, order_index, selected):
        """Update the selection status of an order"""
        if not self.spreadsheet:
            return False
        
        try:
            worksheet = self.get_worksheet('PENDING_ORDERS')
            all_records = worksheet.get_all_records()
            
            # Find the order for this user
            user_count = 0
            for i, row in enumerate(all_records):
                if row.get('username') == username:
                    if user_count == order_index:
                        # Update the selection status
                        worksheet.update_cell(i + 2, 3, 'TRUE' if selected else 'FALSE')  # +2 for header and 0-index
                        return True
                    user_count += 1
            
            return False
        except Exception as e:
            st.error(f"Failed to update selection: {str(e)}")
            return False
    
    def get_selected_orders(self, username):
        """Get only the selected orders for a user"""
        orders = self.load_pending_orders(username)
        return [order for order in orders if order.get('selected') == 'TRUE']
    
    def clear_selected_orders(self, username):
        """Remove selected orders from pending (move them to ORDERS tab)"""
        if not self.spreadsheet:
            return False
        
        try:
            worksheet = self.get_worksheet('PENDING_ORDERS')
            all_records = worksheet.get_all_records()
            
            # Keep only unselected orders
            filtered = [row for row in all_records if not (row.get('username') == username and row.get('selected') == 'TRUE')]
            
            # Rewrite sheet
            if filtered:
                df = pd.DataFrame(filtered)
                worksheet.clear()
                worksheet.update([df.columns.values.tolist()] + df.values.tolist())
            else:
                worksheet.clear()
            
            return True
        except Exception as e:
            st.error(f"Failed to clear selected orders: {str(e)}")
            return False
    
    def save_route_history(self, routes, date):
        """Save completed routes to history"""
        if not self.spreadsheet:
            return False
        
        try:
            # Use the existing ROUTES tab
            worksheet = self.get_worksheet('ROUTES')
            
            for route_id, route_data in routes.items():
                row = [
                    route_id,
                    date,
                    route_data.get('driver_name', ''),
                    route_data.get('start_location', ''),
                    route_data.get('total_stops', 0),
                    route_data.get('total_distance', ''),
                    route_data.get('total_time', ''),
                    route_data.get('estimated_finish', ''),
                    'completed',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
                worksheet.append_row(row)
            
            return True
        except Exception as e:
            st.error(f"Failed to save route history: {str(e)}")
            return False
