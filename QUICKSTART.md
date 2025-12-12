# 🚀 Quick Start Guide

## Prerequisites Checklist

Before running the app, make sure you have:

- [ ] Python 3.8+ installed
- [ ] Git configured with your GitHub credentials
- [ ] Google Cloud project created
- [ ] Google Sheets API enabled
- [ ] `credentials.json` downloaded
- [ ] Google Gemini API key obtained
- [ ] Google Sheet created with proper tabs

---

## 5-Minute Setup

### 1. Install Dependencies (1 min)

```bash
pip install -r requirements.txt
```

### 2. Configure Environment (2 min)

**Create `.env` file:**
```bash
cp .env.example .env
```

**Edit `.env` and add your keys:**
```env
GEMINI_API_KEY=your_actual_gemini_key_here
GOOGLE_SHEET_ID=1mwSH2hFmggSjxBnkqbIZARylMd_3fXtrF2M0pTgrJe0
```

**Add `credentials.json`:**
- Place your OAuth credentials file in project root
- File name must be exactly `credentials.json`

### 3. Run the App (1 min)

```bash
streamlit run app.py
```

**First run will:**
- Open browser for Google OAuth
- Ask you to grant Sheets access
- Create `token.pickle` file
- Launch the app

### 4. Add Sample Driver (1 min)

1. Go to "Select Drivers" page
2. Click "Add New Driver"
3. Enter:
   - Name: Test Driver
   - Primary Areas: Orange County
   - Cities: Irvine
   - Zip Prefixes: 92
4. Submit

### 5. Test Workflow (30 sec)

1. **Input Orders** - Add a test order manually
2. **Select Drivers** - Check your test driver
3. **Optimize Routes** - Click "Run AI Optimization"
4. **Send Routes** - View the generated route

✅ **Done! Your system is working!**

---

## GitHub Push (Fix Authentication)

The local commit is ready. To push to GitHub:

### Option 1: Using Personal Access Token (Recommended)

```bash
# Generate token at: https://github.com/settings/tokens
# Select scopes: repo, workflow

# Set up credentials
git remote set-url origin https://YOUR_TOKEN@github.com/dmeprousa/DME-Route-Planner.git

# Push
git push -u origin main
```

### Option 2: Using SSH

```bash
# Set up SSH key first, then:
git remote set-url origin git@github.com:dmeprousa/DME-Route-Planner.git
git push -u origin main
```

### Option 3: Using GitHub CLI

```bash
gh auth login
git push -u origin main
```

---

## Common Issues & Quick Fixes

### ❌ "credentials.json not found"
**Fix:** Download from Google Cloud Console and place in project root

### ❌ "GEMINI_API_KEY not found"
**Fix:** Create `.env` file and add your API key

### ❌ "Worksheet 'DRIVERS' not found"
**Fix:** Create tabs in Google Sheet: ORDERS, ROUTES, DRIVERS (exact names)

### ❌ "Permission denied" on Google Sheets
**Fix:** Make sure you're signed in with the correct Google account

### ❌ Git push fails with authentication error
**Fix:** Use Personal Access Token (see GitHub Push section above)

---

## Files You Need to Provide

**You must add these files (they are gitignored for security):**

1. `credentials.json` - From Google Cloud Console
2. `.env` - Copy from `.env.example` and fill in your keys

**These files will be auto-generated:**

- `token.pickle` - Created on first OAuth login
- `__pycache__/` - Python cache files

---

## Deployment Checklist

### Local Testing
- [ ] App runs without errors
- [ ] Can add orders
- [ ] Can select drivers
- [ ] AI optimization works
- [ ] Routes display correctly
- [ ] WhatsApp links work
- [ ] PDF downloads work

### GitHub
- [ ] Code pushed to main branch
- [ ] Repository is public (or private with proper access)
- [ ] No sensitive files committed (.env, credentials.json)

### Streamlit Cloud
- [ ] Connected to GitHub
- [ ] Secrets configured
- [ ] App deployed successfully
- [ ] Can access the live app

---

## Important Links

- **Google Cloud Console:** https://console.cloud.google.com/
- **Google AI Studio (Gemini):** https://ai.google.dev/
- **Streamlit Cloud:** https://share.streamlit.io
- **GitHub Tokens:** https://github.com/settings/tokens
- **Google Sheet:** https://docs.google.com/spreadsheets/d/1mwSH2hFmggSjxBnkqbIZARylMd_3fXtrF2M0pTgrJe0/edit

---

## Test Data

### Sample Order (for testing)

```
Order Type: Delivery
Customer: John Doe
Phone: 760-555-1234
Address: 123 Main St
City: Irvine
Zip: 92618
Items: Hospital Bed, Oxygen Concentrator
Time Window: 10:00 AM - 2:00 PM
Notes: Call before arrival
```

### Sample Driver (for testing)

```
Name: Test Driver
Phone: 760-555-9999
Email: driver@test.com
Primary Areas: Orange County
Cities: Irvine, Anaheim
Zip Prefixes: 92
Vehicle: Van
Start Location: Irvine Office
```

---

## Support

📞 **Phone:** 760-879-1071  
📧 **Email:** support@hospiceprodme.com

---

## What's Next?

After successful setup:

1. ✅ Add your real drivers to the database
2. ✅ Import historical data if needed
3. ✅ Customize start locations
4. ✅ Test with real orders
5. ✅ Deploy to Streamlit Cloud
6. ✅ Share with team

---

**Last Updated:** December 12, 2024  
**Version:** 1.0.0
