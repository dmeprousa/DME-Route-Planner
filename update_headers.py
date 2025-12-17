import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from components.database import Database
import streamlit as st

def update_headers():
    print("Connecting to database...")
    try:
        db = Database()
        ws = db.spreadsheet.worksheet('ORDERS')
        
        # Get current headers (row 1)
        headers = ws.row_values(1)
        print(f"Current headers: {headers}")
        
        new_headers = []
        if 'lat' not in headers:
            new_headers.append('lat')
        if 'lng' not in headers:
            new_headers.append('lng')
            
        if new_headers:
            print(f"Adding new headers: {new_headers}")
            # Calculate column to start adding at
            start_col = len(headers) + 1
            
            # Update cells
            # We can use update_cell for each, or update a range
            # For robustness, let's update one by one
            for i, h in enumerate(new_headers):
                ws.update_cell(1, start_col + i, h)
                print(f"Added '{h}' to column {start_col + i}")
                
            print("✅ Headers updated successfully!")
        else:
            print("ℹ️ Headers 'lat' and 'lng' already exist.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Mock streamlit secrets for Database class if running standalone
    # The Database class checks st.secrets, so we might need to rely on the environment 
    # or existing credentials file if not running via streamlit.
    # But since we are in the user's environment where they ostensibly used 'streamlit run',
    # we might not have 'st.secrets' populated if we run this as a script directly unless we mock it or use 'streamlit run'.
    
    # Actually, Database class logic for local auth:
    # 3. Try Local OAuth (Best for Local Development) -> checks token.pickle/credentials.json
    # It attempts st.secrets first, but catches errors if keys missing.
    # BUT accessing st.secrets outside of streamlit app raises error? No, it just returns empty or fails.
    
    # To be safe, let's try. If it fails, we advise user to add them manually from the doc.
    update_headers()
