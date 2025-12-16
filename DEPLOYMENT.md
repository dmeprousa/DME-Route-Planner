# 🚀 Streamlit Cloud Deployment Guide

## Prerequisites
- GitHub repository connected
- Streamlit Cloud account (streamlit.io/cloud)
- Google Gemini API key
- Google Sheets service account credentials

## Step 1: Configure Secrets in Streamlit Cloud

After deploying your app to Streamlit Cloud, you need to add the following secrets:

1. Go to your app's dashboard on Streamlit Cloud
2. Click on "Settings" → "Secrets"  
3. Add the following secrets (in TOML format):

```toml
# Google Gemini API Key
GOOGLE_API_KEY = "your-actual-google-gemini-api-key"

# Password Hashes (SHA-256)
# Current passwords:
# sofia: 123456Ss
# cyrus: 123456Cc  
# admin: 1234567Hh
PASSWORD_SOFIA = "b231efc738cff097ab77e2a5d475dda69ac9e3ee0d97bebcf4b500406d8d8fa9"
PASSWORD_CYRUS = "a41f28e1b8acc52ae6147822a59381ee6159cc0dc1884f4050f59bb7ba80c74a"
PASSWORD_ADMIN = "384d3a536fe70fdfaa5793e6b98a23ad4baaf83e11ee8f3ee18af5088eaebe87"

# Google Sheets Credentials
# Replace with your actual service account JSON
[GOOGLE_SHEETS_CREDENTIALS]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_ACTUAL_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-client-cert-url"
```

## Step 2: Deploy to Streamlit Cloud

1. **Go to** [share.streamlit.io](https://share.streamlit.io)
2. **Click** "New app"
3. **Select** your GitHub repository: `dmeprousa/DME-Route-Planner`
4. **Set** the main file path: `app.py`
5. **Click** "Deploy"

## Step 3: Verify Environment

After deployment, your app should:
- ✅ Load without errors
- ✅ Show the login page
- ✅ Accept user credentials
- ✅ Connect to Google Sheets (if configured)

## Important Notes

### Read-Only Filesystem
Streamlit Cloud uses a **read-only filesystem**, which means:
- ❌ Cannot write log files to disk
- ❌ Cannot save session state files locally
- ✅ State persists only in `st.session_state` during active sessions
- ✅ Need to use Streamlit's native `st.secrets` for configuration

### Session State
Due to the read-only filesystem:
- User sessions will persist during active browser sessions
- Data will be lost when the app restarts or user refreshes
- Consider using Google Sheets for persistent storage

### Passwords
The app uses **hardcoded passwords** with multiple fallback mechanisms:
1. **Direct plaintext check** (primary - works without secrets)
2. **Hardcoded hash check** (secondary fallback)
3. **Secrets/environment check** (legacy support)

Current credentials:
- **Sofia**: `123456Ss`
- **Cyrus**: `123456Cc`
- **Admin**: `1234567Hh`
- **Emergency master key**: `admin123` (works for any user)

To change passwords:
1. Update the `DIRECT_PASSWORDS` dict in `components/user_session.py`
2. Generate new SHA-256 hashes
3. Update `CORRECT_HASHES` dict
4. Push changes to GitHub

### Environment Variables

For Google Gemini API:
```python
import streamlit as st
api_key = st.secrets.get("GOOGLE_API_KEY")
```

For Google Sheets credentials:
```python
import streamlit as st
credentials_dict = dict(st.secrets["GOOGLE_SHEETS_CREDENTIALS"])
```

## Troubleshooting

### Error: "No module named X"
- Check `requirements.txt` has all dependencies
- Redeploy the app

### Error: "Permission denied"
- This is expected for file write operations
- Already handled with try-except blocks in:
  - `components/user_session.py`
  - `components/session_manager.py`

### Error: "API key not found"
- Add `GOOGLE_API_KEY` to Streamlit Cloud secrets
- Make sure code uses `st.secrets.get("GOOGLE_API_KEY")`

### Login not working
- The app has multiple fallback authentication methods
- Hardcoded passwords will work even without secrets configured
- Try the emergency master key: `admin123`

## Security Considerations

⚠️ **Important**: The current implementation has hardcoded passwords in the source code for reliability. For production use, you should:

1. Remove hardcoded passwords from `components/user_session.py`
2. Use only secrets-based authentication
3. Implement proper password hashing storage
4. Add rate limiting for login attempts
5. Enable HTTPS (Streamlit Cloud does this by default)

## Monitoring

Check your app's health:
1. Go to your app dashboard on Streamlit Cloud  
2. View logs in real-time
3. Monitor app status and performance

## Updates

To update your deployed app:
1. Push changes to GitHub main branch
2. Streamlit Cloud auto-deploys changes
3. App will restart automatically

---

**Last Updated**: December 2025
**Version**: 2.0
