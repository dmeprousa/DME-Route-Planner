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
        """Verify password against stored hash - works with both secrets and env"""
        stored_hash = None
        source = "NOT FOUND"
        
        # Hash the entered password
        password_hash = UserSession.hash_password(password)
        
        # Try multiple methods to get the password hash
        # Method 1: Try Streamlit secrets
        try:
            import streamlit as st
            # Direct access without checking
            password_key = f'PASSWORD_{username.upper()}'
            stored_hash = st.secrets.get(password_key, None)
            if stored_hash:
                source = "Streamlit Secrets"
        except Exception as e:
            pass
        
        # Method 2: Try environment variables
        if not stored_hash:
            try:
                load_dotenv(override=True)
                stored_hash = os.getenv(f'PASSWORD_{username.upper()}')
                if stored_hash:
                    source = ".env file"
            except:
                pass
        
        # If still not found, return False
        if not stored_hash:
            # Only show debug in development
            if os.getenv('DEBUG_MODE') == 'true':
                st.error(f"Password hash not found for {username}")
            return False
        
        # Compare hashes
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
        """Show professional login page with modern DME branding"""
        
        # Inject modern CSS
        st.markdown("""
        <style>
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Modern gradient background */
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Login container */
        .login-card {
            background: white;
            border-radius: 24px;
            padding: 3rem 2.5rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 450px;
            margin: 2rem auto;
        }
        
        /* Headings */
        h1 {
            color: #1a202c !important;
            font-size: 2rem !important;
            font-weight: 800 !important;
            text-align: center;
            margin-bottom: 0.5rem !important;
        }
        
        h2, h3 {
            color: #4a5568 !important;
            font-weight: 600 !important;
            text-align: center;
        }
        
        /* Input fields */
        .stSelectbox, .stTextInput {
            margin-bottom: 1.5rem;
        }
        
        .stSelectbox label, .stTextInput label {
            font-weight: 600 !important;
            color: #2d3748 !important;
            font-size: 0.95rem !important;
        }
        
        input, select {
            border-radius: 12px !important;
            border: 2px solid #e2e8f0 !important;
            padding: 0.875rem !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
        }
        
        input:focus, select:focus {
            border-color: #E63946 !important;
            box-shadow: 0 0 0 3px rgba(230,57,70,0.1) !important;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #E63946 0%, #C5303E 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.875rem 2rem !important;
            font-weight: 700 !important;
            font-size: 1.05rem !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 14px rgba(230,57,70,0.4) !important;
            margin-top: 1rem !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(230,57,70,0.5) !important;
        }
        
        /* Role badge */
        .role-badge {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 12px;
            text-align: center;
            font-weight: 600;
            margin: 1rem 0 1.5rem 0;
            font-size: 0.95rem;
        }
        
        /* Footer */
        .login-footer {
            text-align: center;
            color: #718096;
            font-size: 0.875rem;
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid #e2e8f0;
        }
        
        /* Logo area */
        .logo-area {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        /* Error/Success messages */
        .stAlert {
            border-radius: 12px !important;
            margin-top: 1rem !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Main container
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col2:
            # Logo and header
            st.markdown("""
            <div class='logo-area'>
                <h1>🏥 DME PRO</h1>
                <p style='color: #718096; font-size: 0.95rem; margin-top: 0.5rem;'>
                    The Authority in Durable Medical Solutions
                </p>
                <h3 style='margin-top: 2rem; color: #2d3748;'>Route Planner Login</h3>
                <p style='color: #a0aec0; font-size: 0.9rem;'>
                    Access your route management dashboard
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # User selection
            user_options = {v['name']: k for k, v in USERS.items()}
            selected_name = st.selectbox(
                "Select Your Account",
                options=[''] + list(user_options.keys()),
                format_func=lambda x: "Choose your name..." if x == '' else x,
                key="user_select_main"
            )
            
            if selected_name and selected_name != '':
                username = user_options[selected_name]
                user_info = USERS[username]
                
                # Role badge
                st.markdown(f"""
                <div class='role-badge'>
                    👤 {user_info['role']}
                </div>
                """, unsafe_allow_html=True)
                
                # Password input
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your secure password",
                    key="password_main"
                )
                
                # Login button
                if st.button("🔓 Sign In", key="login_main"):
                    if not password:
                        st.error("⚠️ Please enter your password")
                    elif UserSession.verify_password(username, password):
                        # Successful login
                        st.session_state.current_user = username
                        st.session_state.user_name = user_info['name']
                        st.session_state.user_role = user_info['role']
                        st.session_state.login_attempts = 0
                        
                        UserSession.log_session_start(username)
                        
                        st.success(f"✅ Welcome, {user_info['name']}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.session_state.login_attempts = st.session_state.get('login_attempts', 0) + 1
                        st.error(f"❌ Incorrect password (Attempt {st.session_state.login_attempts})")
                        UserSession.log_failed_login(username)
                
                # Warning for multiple attempts
                if st.session_state.get('login_attempts', 0) >= 3:
                    st.warning("⚠️ Multiple failed attempts. Contact administrator if you forgot your password.")
            
            # Footer
            st.markdown("""
            <div class='login-footer'>
                🔒 Secure Authentication • AI-Powered Optimization<br>
                <span style='color: #cbd5e0; font-size: 0.8rem;'>© 2025 DME Pro. All Rights Reserved.</span>
            </div>
            """, unsafe_allow_html=True)
        
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

