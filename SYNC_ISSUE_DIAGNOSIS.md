# DATA SYNCHRONIZATION ISSUE - DIAGNOSIS

## Current Problem:
The pages are NOT synchronized because:

1. **Dashboard** reads from `st.session_state.orders`
2. **Optimize Routes** creates `st.session_state.optimized_routes` 
3. **Route Map** reads from `st.session_state.optimized_routes` OR `st.session_state.orders`

## Issues Found:

### Issue 1: Orders not updated when routes are optimized
- **Location**: `pages/3_🤖_Optimize_Routes.py` lines 123-134
- **Problem**: The code tries to update `st.session_state.orders` with `assigned_driver`, but:
  - Matching is by address only (not reliable if address formatting differs)
  - The matched order doesn't get `status` updated to `'sent_to_driver'`
  
### Issue 2: Route Map showing wrong Pending count
- **Location**: `pages/7_🗺️_Route_Map.py` line 301
- **Problem**: `pending = total_stops - delivered` is correct, but the orders from `optimized_routes` don't have `status` field set properly
- **Result**: Shows "Pending: 0" even when there should be 2 pending

### Issue 3: Dashboard not reflecting optimized routes
- **Location**: `app.py` lines 54-58  
- **Problem**: Dashboard calculates stats from `st.session_state.orders`, but these orders are not updated when optimization happens
- **Result**: Shows all 8 orders as "Pending" even after assigning 2 to David

## Root Cause:
**Two separate data structures** that don't sync:
- `st.session_state.orders` = original input orders
- `st.session_state.optimized_routes` = optimized route data

When routes are optimized:
✅ Creates `optimized_routes`  
❌ Doesn't properly update `orders` with `assigned_driver` and `status`

## Solution Required:

### Fix 1: Update orders when optimization completes
In `pages/3_🤖_Optimize_Routes.py`, after line 134, add:
```python
# Also update status to sent_to_driver
session_order['status'] = 'sent_to_driver'
```

### Fix 2: Use customer_name + address for matching
Change line 131 to:
```python
if (session_order.get('address') == route_order.get('address') and 
    session_order.get('customer_name') == route_order.get('customer_name')):
```

### Fix 3: Ensure optimized routes have status field
In `components/ai_optimizer.py`, ensure each stop has:
```python
stop['status'] = stop.get('status', 'pending')
```

### Fix 4: Dashboard should check both sources
In `app.py`, dashboard should show orders from optimized_routes if they exist, otherwise from orders.

##Tests Needed:
1. Add 8 orders → Check Dashboard shows 8 Pending
2. Opt imize routes → Check Dashboard updates to show Sent
3. View Route Map → Check table shows correct Pending count
4. All pages should show consistent data
