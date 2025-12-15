import streamlit as st
import json
import os

STATE_FILE = "app_state.json"

class SessionManager:
    @staticmethod
    def save_state():
        """Save relevant session state to disk"""
        state_to_save = {
            'selected_drivers': st.session_state.get('selected_drivers', []),
            'driver_config': st.session_state.get('driver_config', {}),
            'orders': st.session_state.get('orders', []),
            'routes': st.session_state.get('routes', {})
        }
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump(state_to_save, f)
        except Exception as e:
            print(f"Error saving state: {e}")

    @staticmethod
    def load_state():
        """Load session state from disk if exists"""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    saved_state = json.load(f)
                
                # Restore to session state if not already set
                if 'selected_drivers' not in st.session_state:
                    st.session_state.selected_drivers = saved_state.get('selected_drivers', [])
                
                if 'driver_config' not in st.session_state:
                    st.session_state.driver_config = saved_state.get('driver_config', {})
                
                if 'orders' not in st.session_state:
                    st.session_state.orders = saved_state.get('orders', [])
                    
                if 'routes' not in st.session_state:
                    st.session_state.routes = saved_state.get('routes', {})
                    
            except Exception as e:
                print(f"Error loading state: {e}")
