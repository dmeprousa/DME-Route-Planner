"""
Google Sheets Database with OAuth Authentication
"""

import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
from datetime import datetime
from typing import List, Dict, Optional

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class Database:
    
    def __init__(self):
        """Initialize Google Sheets with OAuth or Service Account"""
        import streamlit as st
        from google.oauth2 import service_account
        
        creds = None
        
        # 1. Try Service Account from Streamlit Secrets (Best for Cloud)
        try:
            if "gcp_service_account" in st.secrets:
                try:
                    # Check if it's a dict or a string (sometimes people paste JSON as string)
                    if isinstance(st.secrets["gcp_service_account"], str):
                        import json
                        service_account_info = json.loads(st.secrets["gcp_service_account"])
                    else:
                        service_account_info = st.secrets["gcp_service_account"]
                    
                    creds = service_account.Credentials.from_service_account_info(
                        service_account_info, scopes=SCOPES
                    )
                except Exception as e:
                    st.error(f"⚠️ Error reading 'gcp_service_account' from secrets: {str(e)}")
        except:
            # Secrets file doesn't exist, will try local auth
            pass

        # 2. Try OAuth Refresh Token from Streamlit Secrets (Alternative for Personal Accounts)
        try:
            if not creds and "gcp_oauth" in st.secrets:
                try:
                    oauth_info = st.secrets["gcp_oauth"]
                    creds = Credentials(
                        token=oauth_info.get("token"),
                        refresh_token=oauth_info.get("refresh_token"),
                        token_uri=oauth_info.get("token_uri"),
                        client_id=oauth_info.get("client_id"),
                        client_secret=oauth_info.get("client_secret"),
                        scopes=SCOPES
                    )
                except Exception as e:
                     st.error(f"⚠️ Error reading 'gcp_oauth' from secrets: {str(e)}")
        except:
            # Secrets file doesn't exist, will try local auth
            pass
        
        # 3. Try Local OAuth (Best for Local Development)
        if not creds:
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                elif os.path.exists('credentials.json'):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                    with open('token.pickle', 'wb') as token:
                        pickle.dump(creds, token)
        
        
        if not creds:
            raise Exception("Could not authenticate. Check secrets or credentials.json")
            
        # Authorize and open sheet
        self.client = gspread.authorize(creds)
        
        # Get Sheet ID from Secrets or Env
        sheet_id = None
        try:
            if "GOOGLE_SHEET_ID" in st.secrets:
                sheet_id = st.secrets["GOOGLE_SHEET_ID"]
        except:
            pass
        
        if not sheet_id:
            sheet_id = os.getenv('GOOGLE_SHEET_ID', '1mwSH2hFmggSjxBnkqbIZARylMd_3fXtrF2M0pTgrJe0')
            
        self.spreadsheet = self.client.open_by_key(sheet_id)
    
    def get_drivers(self, status: str = 'active') -> List[Dict]:
        """Get all drivers from DRIVERS sheet"""
        try:
            ws = self.spreadsheet.worksheet('DRIVERS')
            records = ws.get_all_records()
            
            if status:
                records = [r for r in records if r.get('status', '').lower() == status.lower()]
            
            return records
        except Exception as e:
            raise Exception(f"Error reading drivers: {str(e)}")
    
    def add_driver(self, driver_data: Dict) -> str:
        """Add new driver to DRIVERS sheet"""
        try:
            ws = self.spreadsheet.worksheet('DRIVERS')
            
            # Generate ID
            existing = ws.get_all_records()
            num = len(existing) + 1
            driver_id = f"DRV-{num:03d}"
            
            # Prepare row
            row = [
                driver_id,
                driver_data.get('driver_name', ''),
                driver_data.get('phone', ''),
                driver_data.get('email', ''),
                driver_data.get('status', 'active'),
                driver_data.get('primary_areas', ''),
                driver_data.get('cities_covered', ''),
                driver_data.get('zip_prefixes', ''),
                driver_data.get('vehicle_type', 'Van'),
                driver_data.get('start_location', ''),
                driver_data.get('notes', ''),
                datetime.now().strftime('%Y-%m-%d'),
                datetime.now().strftime('%Y-%m-%d')
            ]
            
            ws.append_row(row)
            return driver_id
            
        except Exception as e:
            raise Exception(f"Error adding driver: {str(e)}")
    
    def save_orders(self, orders: List[Dict], date: str) -> None:
        """Save orders to ORDERS sheet - replaces existing orders for this date"""
        try:
            ws = self.spreadsheet.worksheet('ORDERS')
            
            # Find rows with matching date (Column B, index 1)
            all_values = ws.get_all_values()
            if len(all_values) > 1:
                rows_to_delete = []
                for idx, row in enumerate(all_values[1:], start=2):
                    if len(row) > 1 and row[1] == date:
                        rows_to_delete.append(idx)
                
                # Delete in reverse order
                for row_idx in reversed(rows_to_delete):
                    ws.delete_rows(row_idx)
            
            # Prepare rows for bulk append
            rows_to_append = []
            for i, order in enumerate(orders):
                order_id = order.get('order_id') or order.get('order_id_1')
                if not order_id:
                    order_id = f"ORD-{date.replace('-', '')}-{i+1:03d}"
                
                # CRITICAL FIX: Save the generated order_id back to the order dictionary
                # This ensures orders in session state have valid IDs for deletion
                order['order_id'] = order_id
                
                # Map fields robustly
                raw_items = order.get('items', '')
                clean_items = " | ".join(raw_items) if isinstance(raw_items, list) else str(raw_items).replace(',', ' | ')
                
                row = [
                    order_id,
                    date,
                    datetime.now().isoformat(),
                    order.get('status', 'pending'),
                    order.get('order_type', ''),
                    order.get('customer_name', ''),
                    order.get('customer_phone', ''),
                    order.get('address', ''),
                    order.get('city', ''),
                    order.get('zip_code', ''),
                    clean_items,
                    order.get('time_window_start', '') or order.get('time_start', ''),
                    order.get('time_window_end', '') or order.get('time_end', ''),
                    order.get('special_notes', ''),
                    order.get('assigned_driver', ''),
                    order.get('route_id', ''),
                    order.get('stop_number', ''),
                    order.get('eta', ''),
                    order.get('eta', ''),
                    datetime.now().isoformat(),
                    order.get('coordinates', {}).get('lat', '') if isinstance(order.get('coordinates'), dict) else '',
                    order.get('coordinates', {}).get('lng', '') if isinstance(order.get('coordinates'), dict) else '',
                    order.get('parsed_at', '')
                ]
                rows_to_append.append(row)
            
            if rows_to_append:
                ws.append_rows(rows_to_append)
                
        except Exception as e:
            raise Exception(f"Error saving orders: {str(e)}")
    
    def save_routes(self, routes: Dict, date: str) -> None:
        """Save routes to ROUTES sheet"""
        try:
            ws = self.spreadsheet.worksheet('ROUTES')
            
            for driver_name, route_data in routes.items():
                route_id = f"ROUTE-{date.replace('-', '')}-{driver_name.split()[0].upper()}"
                summary = route_data.get('summary', {})
                
                row = [
                    route_id,
                    date,
                    driver_name,
                    summary.get('start_location', ''),
                    summary.get('total_stops', 0),
                    summary.get('total_distance_miles', 0),
                    summary.get('total_drive_time_min', 0),
                    summary.get('estimated_finish', ''),
                    'planned',
                    '',
                    datetime.now().isoformat()
                ]
                
                ws.append_row(row)
                
        except Exception as e:
            raise Exception(f"Error saving routes: {str(e)}")
    
    def get_routes(self, date: Optional[str] = None) -> List[Dict]:
        """Query routes from ROUTES sheet"""
        try:
            ws = self.spreadsheet.worksheet('ROUTES')
            records = ws.get_all_records()
            
            if date:
                records = [r for r in records if r.get('date') == date]
            
            return records
            
        except Exception as e:
            raise Exception(f"Error reading routes: {str(e)}")
    
    def get_orders(self, date: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
        """Query orders"""
        try:
            ws = self.spreadsheet.worksheet('ORDERS')
            
            # Use get_all_values to handle duplicate/empty headers manually
            all_values = ws.get_all_values()
            
            if not all_values:
                return []
                
            raw_headers = all_values[0]
            rows = all_values[1:]
            
            # Create normalized headers for mapping (snake_case)
            # This handles 'Date' -> 'date', 'Order Type' -> 'order_type'
            headers = []
            seen_count = {}
            for h in raw_headers:
                # Normalize: lowercase, strip, replace spaces with underscores
                key = str(h).strip().lower().replace(' ', '_')
                if not key:
                    key = "unknown"
                
                if key in seen_count:
                    seen_count[key] += 1
                    key = f"{key}_{seen_count[key]}"
                else:
                    seen_count[key] = 0
                headers.append(key)
            
            records = []
            for row in rows:
                # Ensure row is same length as headers
                if len(row) < len(headers):
                    row = row + [''] * (len(headers) - len(row))
                elif len(row) > len(headers):
                    row = row[:len(headers)]
                    
                records.append(dict(zip(headers, row)))
            
            # Filter results - Using normalized keys
            if date:
                records = [r for r in records if r.get('date') == date]
            if status:
                records = [r for r in records if str(r.get('status', '')).lower() == status.lower()]
            
            return records
            
        except Exception as e:
            raise Exception(f"Error reading orders: {str(e)}")

    def update_order_status(self, order_id: str, new_status: str) -> bool:
        """Update the status of a specific order"""
        try:
            ws = self.spreadsheet.worksheet('ORDERS')
            cell = ws.find(order_id)
            if cell:
                # Status is in column 4 (D) based on save_orders structure
                # row, col. Update col 4
                ws.update_cell(cell.row, 4, new_status)
                return True
            return False
        except Exception as e:
            raise Exception(f"Error updating status: {str(e)}")
    
    def update_order_driver_and_route(self, order_id: str, driver_name: str, route_id: str = '', stop_number: str = '', eta: str = '', status: str = '') -> bool:
        """Update order's assigned driver and route information"""
        try:
            ws = self.spreadsheet.worksheet('ORDERS')
            cell = ws.find(order_id)
            
            if cell:
                row_num = cell.row
                # Based on save_orders structure:
                # Column 4 = status
                # Column 15 = assigned_driver
                # Column 16 = route_id
                # Column 17 = stop_number
                # Column 18 = eta
                
                # Update status if provided (column 4)
                if status:
                    ws.update_cell(row_num, 4, status)
                
                # Update assigned_driver (column 15)
                ws.update_cell(row_num, 15, driver_name)
                
                # Update route_id if provided (column 16)
                if route_id:
                    ws.update_cell(row_num, 16, route_id)
                
                # Update stop_number if provided (column 17)
                if stop_number:
                    ws.update_cell(row_num, 17, str(stop_number))
                
                # Update eta if provided (column 18)
                if eta:
                    ws.update_cell(row_num, 18, eta)
                
                return True
            else:
                return False
                
        except Exception as e:
            raise Exception(f"Error updating order driver/route: {str(e)}")

