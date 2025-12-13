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
        if "gcp_service_account" in st.secrets:
            try:
                service_account_info = st.secrets["gcp_service_account"]
                creds = service_account.Credentials.from_service_account_info(
                    service_account_info, scopes=SCOPES
                )
            except Exception as e:
                print(f"Error loading secrets: {e}")
        
        # 2. Try Local OAuth (Best for Local Development)
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
        if "GOOGLE_SHEET_ID" in st.secrets:
            sheet_id = st.secrets["GOOGLE_SHEET_ID"]
        else:
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
        """Save orders to ORDERS sheet"""
        try:
            ws = self.spreadsheet.worksheet('ORDERS')
            
            for i, order in enumerate(orders):
                order_id = f"ORD-{date.replace('-', '')}-{i+1:03d}"
                
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
                    order.get('items', ''),
                    order.get('time_window_start', ''),
                    order.get('time_window_end', ''),
                    order.get('special_notes', ''),
                    order.get('assigned_driver', ''),
                    order.get('route_id', ''),
                    order.get('stop_number', ''),
                    order.get('eta', ''),
                    datetime.now().isoformat()
                ]
                
                ws.append_row(row)
                
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
    
    def get_orders(self, date: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
        """Query orders"""
        try:
            ws = self.spreadsheet.worksheet('ORDERS')
            records = ws.get_all_records()
            
            if date:
                records = [r for r in records if r.get('date') == date]
            if status:
                records = [r for r in records if r.get('status', '').lower() == status.lower()]
            
            return records
            
        except Exception as e:
            raise Exception(f"Error reading orders: {str(e)}")
