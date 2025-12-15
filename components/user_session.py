"""
Simple User Management for DME Route Planner
Allows multiple users to work with separate sessions
"""

import streamlit as st
import json
import os
from datetime import datetime

# Available users
USERS = {
    'sofia': {'name': 'Sofia', 'role': 'Dispatcher'},
    'cyrus': {'name': 'Cyrus', 'role': 'Manager'},
    'admin': {'name': 'Admin', 'role': 'Administrator'}
}

class UserSession:
    
    @staticmethod
    def get_state_file(username):
        """Get user-specific state file"""
        return f"app_state_{username}.json"
    
    @staticmethod
    def init_user():
        """Initialize user selection"""
        
        # Check if user is already selected in this session
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
            st.session_state.user_name = None
            st.session_state.user_role = None
    
    @staticmethod
    def select_user():
        """Show user selection page"""
        
        st.title("🔐 DME Route Planner - Login")
        st.write("Select your user to continue")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.write("")
            st.write("")
            
            # User selection dropdown
            user_options = {v['name']: k for k, v in USERS.items()}
            selected_name = st.selectbox(
                "Who are you?",
                options=[''] + list(user_options.keys()),
                format_func=lambda x: "Select user..." if x == '' else x
            )
            
            if selected_name and selected_name != '':
                username = user_options[selected_name]
                user_info = USERS[username]
                
                st.info(f"**Role:** {user_info['role']}")
                
                if st.button("Continue →", type="primary", use_container_width=True):
                    # Set user in session
                    st.session_state.current_user = username
                    st.session_state.user_name = user_info['name']
                    st.session_state.user_role = user_info['role']
                    
                    # Log session start
                    UserSession.log_session_start(username)
                    
                    st.rerun()
        
        return False
    
    @staticmethod
    def log_session_start(username):
        """Log when user starts a session"""
        log_file = "user_sessions.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, 'a') as f:
            f.write(f"{timestamp} - {username} - SESSION_START\n")
    
    @staticmethod
    def is_logged_in():
        """Check if user is logged in"""
        return st.session_state.get('current_user') is not None
    
    @staticmethod
    def get_current_user():
        """Get current logged in user"""
        return st.session_state.get('current_user')
    
    @staticmethod
    def logout():
        """Logout current user"""
        if 'current_user' in st.session_state:
            username = st.session_state.current_user
            UserSession.log_session_end(username)
            
            # Clear user session
            st.session_state.current_user = None
            st.session_state.user_name = None
            st.session_state.user_role = None
            
            # Clear app data
            st.session_state.orders = []
            st.session_state.selected_drivers = []
            st.session_state.optimized_routes = {}
    
    @staticmethod
    def log_session_end(username):
        """Log when user ends a session"""
        log_file = "user_sessions.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, 'a') as f:
            f.write(f"{timestamp} - {username} - SESSION_END\n")
    
    @staticmethod
    def show_user_info_sidebar():
        """Show current user info in sidebar"""
        if UserSession.is_logged_in():
            with st.sidebar:
                st.divider()
                st.write("**👤 Current User**")
                st.write(f"**Name:** {st.session_state.user_name}")
                st.write(f"**Role:** {st.session_state.user_role}")
                
                if st.button("🚪 Logout", use_container_width=True):
                    UserSession.logout()
                    st.rerun()
