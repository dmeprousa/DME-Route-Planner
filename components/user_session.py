"""
Simple User Management for DME Route Planner
Allows multiple users to work with separate sessions
Now includes password authentication for security
"""

import streamlit as st
import json
import os
import hashlib
from datetime import datetime
from dotenv import load_dotenv

# Force reload of environment variables (important for password updates)
load_dotenv(override=True)

# Available users (passwords are stored hashed in .env)
USERS = {
    'sofia': {'name': 'Sofia', 'role': 'Dispatcher'},
    'cyrus': {'name': 'Cyrus', 'role': 'Manager'},
    'admin': {'name': 'Admin', 'role': 'Administrator'}
}

class UserSession:
    
    @staticmethod
    def hash_password(password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(username, password):
        """Verify password against stored hash"""
        # Try to get password from Streamlit secrets first (for cloud deployment)
        # Then fallback to .env file (for local development)
        stored_hash = None
        source = "NOT FOUND"
        
        # Debug info about secrets
        import streamlit as st
        available_secrets = []
        
        try:
            # Try Streamlit secrets first (cloud deployment)
            password_key = f'PASSWORD_{username.upper()}'
            
            # Check what secrets are available (for debugging)
            if hasattr(st, 'secrets'):
                try:
                    available_secrets = list(st.secrets.keys())
                except:
                    available_secrets = ["Unable to list secrets"]
                
                # Check if our password key exists
                if password_key in st.secrets:
                    stored_hash = st.secrets[password_key]
                    source = "Streamlit Secrets"
        except Exception as e:
            # If secrets don't exist or error, continue to .env fallback
            available_secrets.append(f"Error: {str(e)}")
        
        # If not found in secrets, try .env file (local development)
        if not stored_hash:
            try:
                load_dotenv(override=True)
                stored_hash = os.getenv(f'PASSWORD_{username.upper()}')
                if stored_hash:
                    source = ".env file"
            except:
                pass
        
        # Debug: Print what we're comparing (only first/last 8 chars for security)
        password_hash = UserSession.hash_password(password)
        
        # Temporary debug output
        if 'debug_mode' not in st.session_state:
            st.session_state.debug_mode = True
            
        if st.session_state.debug_mode:
            st.write("🔍 **Debug Info:**")
            st.write(f"- Username: `{username}`")
            st.write(f"- Looking for key: `PASSWORD_{username.upper()}`")
            st.write(f"- Password entered: `{'*' * len(password)}`")
            st.write(f"- Generated hash: `{password_hash[:8]}...{password_hash[-8:]}`")
            st.write(f"- Stored hash: `{stored_hash[:8] if stored_hash else 'None'}...{stored_hash[-8:] if stored_hash else ''}`")
            st.write(f"- Hash length: {len(stored_hash) if stored_hash else 0} chars")
            st.write(f"- Source: {source}")
            
            # Show available secrets (sensitive info hidden)
            if available_secrets:
                st.write(f"- **Available secret keys**: {', '.join([f'`{k}`' for k in available_secrets if not k.startswith('gcp_')])}")
            
            st.write(f"- Match: {password_hash == stored_hash if stored_hash else 'NO HASH FOUND'}")
        
        if not stored_hash:
            return False
        
        # Hash the provided password and compare
        return password_hash == stored_hash
    
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
            st.session_state.login_attempts = 0
    
    @staticmethod
    def select_user():
        """Show user selection and password page"""
        
        st.title("🔐 DME Route Planner - Login")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.write("")
            st.write("")
            
            # User selection dropdown
            user_options = {v['name']: k for k, v in USERS.items()}
            selected_name = st.selectbox(
                "Select User",
                options=[''] + list(user_options.keys()),
                format_func=lambda x: "Choose your name..." if x == '' else x
            )
            
            if selected_name and selected_name != '':
                username = user_options[selected_name]
                user_info = USERS[username]
                
                st.info(f"**Role:** {user_info['role']}")
                
                # Password input
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password"
                )
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("🔓 Login", type="primary", use_container_width=True):
                        if not password:
                            st.error("Please enter your password")
                        elif UserSession.verify_password(username, password):
                            # Set user in session
                            st.session_state.current_user = username
                            st.session_state.user_name = user_info['name']
                            st.session_state.user_role = user_info['role']
                            st.session_state.login_attempts = 0
                            
                            # Log session start
                            UserSession.log_session_start(username)
                            
                            st.success(f"Welcome back, {user_info['name']}! 👋")
                            st.rerun()
                        else:
                            st.session_state.login_attempts += 1
                            st.error(f"❌ Incorrect password! Attempt {st.session_state.login_attempts}")
                            
                            # Log failed attempt
                            UserSession.log_failed_login(username)
                
                # Show login attempts warning
                if st.session_state.get('login_attempts', 0) >= 3:
                    st.warning("⚠️ Multiple failed attempts detected. Please contact admin if you forgot your password.")
        
        return False
    
    @staticmethod
    def log_session_start(username):
        """Log when user starts a session"""
        log_file = "user_sessions.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, 'a') as f:
            f.write(f"{timestamp} - {username} - LOGIN_SUCCESS\n")
    
    @staticmethod
    def log_failed_login(username):
        """Log failed login attempt"""
        log_file = "user_sessions.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, 'a') as f:
            f.write(f"{timestamp} - {username} - LOGIN_FAILED\n")
    
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
            st.session_state.login_attempts = 0
            
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
            f.write(f"{timestamp} - {username} - LOGOUT\n")
    
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
    
    @staticmethod
    def require_auth():
        """Require authentication for a page - call this at the top of each page"""
        UserSession.init_user()
        
        if not UserSession.is_logged_in():
            st.error("🔒 This page requires authentication")
            st.info("Please login from the home page to continue")
            
            if st.button("Go to Login Page"):
                st.switch_page("app.py")
            
            st.stop()

