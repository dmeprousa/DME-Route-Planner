# User Management System

## Overview
The DME Route Planner now supports **multiple users** working simultaneously without conflicts.

## Features

### ✅ User Sessions
- **Sofia**, **Cyrus**, and **Admin** can work at the same time
- Each user has their own separate data
- No conflicts between users

### ✅ State Persistence
- Each user's work is saved in a separate file:
  - `app_state_sofia.json`
  - `app_state_cyrus.json`
  - `app_state_admin.json`
- Refresh the page? No problem - your data is restored automatically

### ✅ Session Logging
- All login/logout events are tracked in `user_sessions.log`
- Helps monitor who's using the system and when

## How It Works

### 1. Login Screen
When you open the app, you'll see a user selection screen:
- Select your name from the dropdown
- Click "Continue"
- You're in!

### 2. Personal Workspace
Everything you do is saved to your personal session:
- ✅ Orders you add
- ✅ Drivers you select
- ✅ Routes you optimize
- ✅ All your configurations

### 3. Logout
- Click the "Logout" button in the sidebar
- Your data is saved automatically
- Next time you login, everything is still there

## Multi-User Scenarios

### Scenario 1: Sofia and Cyrus Working Together
```
9:00 AM - Sofia logs in
- Adds 10 orders for Long Beach
- Selects 3 drivers
- Optimizes routes

9:30 AM - Cyrus logs in (while Sofia is still working)
- Adds 5 orders for Irvine
- Selects 2 different drivers
- Optimizes routes

Result: ✅ No conflicts! Each sees only their own data.
```

### Scenario 2: Refresh Recovery
```
Sofia is working:
- 10 orders entered
- Routes optimized
- Accidentally closes browser tab

Sofia reopens:
- Selects "Sofia" from login
- ALL her work is restored!
- Can continue where she left off
```

## Current Users

| Username | Name  | Role          |
|----------|-------|---------------|
| sofia    | Sofia | Dispatcher    |
| cyrus    | Cyrus | Manager       |
| admin    | Admin | Administrator |

## Adding New Users

To add a new user, edit `components/user_session.py`:

```python
USERS = {
    'sofia': {'name': 'Sofia', 'role': 'Dispatcher'},
    'cyrus': {'name': 'Cyrus', 'role': 'Manager'},
    'admin': {'name': 'Admin', 'role': 'Administrator'},
    'john': {'name': 'John', 'role': 'Dispatcher'},  # New user
}
```

## Technical Details

### File Structure
```
app_state_sofia.json     # Sofia's session data
app_state_cyrus.json     # Cyrus's session data
app_state_admin.json     # Admin's session data
user_sessions.log        # All login/logout events
```

### Session Data
Each user's state file contains:
```json
{
  "selected_drivers": [...],
  "driver_config": {...},
  "orders": [...],
  "routes": {...},
  "optimized_routes": {...}
}
```

## Benefits for MVP

### ✅ Immediate Benefits
1. **No Conflicts** - Multiple dispatchers can work simultaneously
2. **Data Safety** - Refresh doesn't lose work
3. **Accountability** - Know who created which routes
4. **Simple** - No complex authentication needed for MVP

### 🚀 Future Enhancements
1. Add password authentication
2. Role-based permissions
3. Database instead of JSON files
4. Real-time collaboration
5. Activity tracking per user

## FAQ

**Q: What happens if two users select the same drivers?**
A: Currently, both can select the same drivers. This is fine for MVP. In future versions, we can add driver availability tracking.

**Q: Can I see another user's routes?**
A: No. Each user only sees their own data. However, all routes are saved to the Google Sheet, where an admin can see everything.

**Q: What if I forget to logout?**
A: Your work is auto-saved. Next time you login, you'll see your previous work. Just clear it if you want to start fresh.

**Q: Can I work on two devices at once?**
A: No, the state is saved locally on each server instance. For multi-device support, we'd need database-backed authentication (future enhancement).

## Migration from Old System

If you have an existing `app_state.json` file:
1. It will be used as `app_state_default.json`
2. Or you can rename it to `app_state_sofia.json` to give it to Sofia
3. Or just start fresh - the old file won't interfere

## Summary

✅ **Problem Solved**: Sofia and Cyrus can now work at the same time!
✅ **Refresh Safe**: Your work is auto-saved and restored
✅ **Simple**: Just select your name and go
✅ **Ready for MVP**: No complex setup needed
