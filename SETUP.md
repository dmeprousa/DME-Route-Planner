# 🔧 DME Route Planner - Setup Guide

## Prerequisites

- Python 3.8 or higher
- Google Cloud Project with Sheets API enabled
- Google Gemini API key
- Git

## Step-by-Step Setup

### 1. Clone Repository

```bash
git clone https://github.com/dmeprousa/DME-Route-Planner.git
cd DME-Route-Planner
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Google Sheets Setup

#### Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable **Google Sheets API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"

#### Create OAuth Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop app"
4. Download the JSON file
5. **Rename it to `credentials.json`**
6. **Place it in the project root directory**

#### Create Google Sheet

1. Create a new Google Sheet
2. Name it "DME Routes Database"
3. Create 3 tabs with exact names:
   - **ORDERS**
   - **ROUTES**
   - **DRIVERS**

4. Add headers to each tab:

**ORDERS tab:**
```
order_id | date | created_at | status | order_type | customer_name | customer_phone | address | city | zip_code | items | time_window_start | time_window_end | special_notes | assigned_driver | route_id | stop_number | eta | updated_at
```

**ROUTES tab:**
```
route_id | date | driver_name | start_location | total_stops | total_distance_miles | total_drive_time_min | estimated_finish | route_status | sent_at | created_at
```

**DRIVERS tab:**
```
driver_id | driver_name | phone | email | status | primary_areas | cities_covered | zip_prefixes | vehicle_type | start_location | notes | created_at | updated_at
```

5. Copy the Sheet ID from the URL:
   - URL format: `https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit`
   - Copy the `SHEET_ID` part

### 4. Get Gemini API Key

1. Go to [Google AI Studio](https://ai.google.dev/)
2. Click "Get API Key"
3. Create a new key or use existing
4. Copy the API key

### 5. Configure Environment

1. Copy the example env file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   GOOGLE_SHEET_ID=your_sheet_id_here
   ```

### 6. First Run

```bash
streamlit run app.py
```

**On first run:**
- Browser will open for Google OAuth
- Sign in with your Google account
- Grant access to Google Sheets
- A `token.pickle` file will be created (this caches your auth)

### 7. Add Sample Drivers

1. Go to "Select Drivers" page
2. Click "Add New Driver"
3. Fill in driver details
4. Submit

**Sample Driver Data:**
```
Name: John Smith
Phone: 760-555-1234
Primary Areas: Orange County
Cities Covered: Irvine, Anaheim, Santa Ana
Zip Prefixes: 92
Vehicle: Van
Start Location: Irvine Office
```

## Deployment to Streamlit Cloud

### 1. Prepare for Deployment

Add to `.streamlit/secrets.toml` (create if doesn't exist):

```toml
GEMINI_API_KEY = "your_api_key"
GOOGLE_SHEET_ID = "your_sheet_id"

[gcp_service_account]
# Paste your credentials.json content here
```

Note: For Streamlit Cloud, you'll need to use a Service Account instead of OAuth. See [Streamlit Secrets](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management).

### 2. Push to GitHub

```bash
git add .
git commit -m "Initial setup for deployment"
git push origin main
```

### 3. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select repository: `dmeprousa/DME-Route-Planner`
4. Main file: `app.py`
5. Add secrets from `.streamlit/secrets.toml`
6. Click "Deploy"

## Troubleshooting

### OAuth Error

**Problem:** "credentials.json not found"

**Solution:** Make sure `credentials.json` is in the project root directory

---

**Problem:** Token expired

**Solution:** Delete `token.pickle` and restart the app to re-authenticate

---

### Gemini API Error

**Problem:** "GEMINI_API_KEY not found"

**Solution:** Check your `.env` file and make sure the key is set

---

**Problem:** API quota exceeded

**Solution:** Check your [Google AI Studio](https://ai.google.dev/) quota

---

### Google Sheets Error

**Problem:** "Worksheet not found"

**Solution:** Make sure your Google Sheet has tabs named exactly: `ORDERS`, `ROUTES`, `DRIVERS`

---

**Problem:** Permission denied

**Solution:** Make sure the Google account you authenticated with has access to the Sheet

---

## Support

For issues or questions:
- 📞 Call: 760-879-1071
- 📧 Email: support@hospiceprodme.com

## Next Steps

1. ✅ Add your drivers to the database
2. ✅ Test the workflow with sample orders
3. ✅ Verify WhatsApp integration works
4. ✅ Test PDF generation
5. ✅ Deploy to Streamlit Cloud
