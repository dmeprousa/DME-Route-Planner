import streamlit as st
import json
import os

def get_state_file():
    """Get the state file for current user"""
    username = st.session_state.get('current_user', 'default')
    return f"app_state_{username}.json"

class SessionManager:
    @staticmethod
    def save_state():
        """Save relevant session state to disk (user-specific)"""
        state_file = get_state_file()
        
        state_to_save = {
            'selected_drivers': st.session_state.get('selected_drivers', []),
            'driver_config': st.session_state.get('driver_config', {}),
            'orders': st.session_state.get('orders', []),
            'routes': st.session_state.get('routes', {}),
            'optimized_routes': st.session_state.get('optimized_routes', {})
        }
        try:
            with open(state_file, 'w') as f:
                json.dump(state_to_save, f, indent=2)
        except Exception as e:
            print(f"Error saving state: {e}")

    @staticmethod
    def load_state():
        """Load session state from disk if exists (user-specific)"""
        state_file = get_state_file()
        
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
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
                
                if 'optimized_routes' not in st.session_state:
                    st.session_state.optimized_routes = saved_state.get('optimized_routes', {})
                    
            except Exception as e:
                print(f"Error loading state: {e}")
    
    @staticmethod
    def clear_state():
        """Clear user's saved state file"""
        state_file = get_state_file()
        if os.path.exists(state_file):
            try:
                os.remove(state_file)
            except Exception as e:
                print(f"Error clearing state: {e}")

