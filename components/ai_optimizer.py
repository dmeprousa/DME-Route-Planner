"""
AI Route Optimizer using Google Gemini
"""

import google.generativeai as genai
import json
import os
from typing import List, Dict

class AIOptimizer:
    
    def __init__(self):
        """Initialize Gemini API"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def optimize_routes(self, orders: List[Dict], drivers: List[Dict]) -> Dict:
        """
        Optimize routes using AI
        
        Args:
            orders: List of order dicts
            drivers: List of available driver dicts
        
        Returns:
            Dict with optimized routes per driver
        """
        
        prompt = self._build_prompt(orders, drivers)
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text
            
            # Clean JSON markers
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            
            result = json.loads(result_text.strip())
            return result
            
        except Exception as e:
            raise Exception(f"AI optimization failed: {str(e)}")
    
    def _build_prompt(self, orders: List[Dict], drivers: List[Dict]) -> str:
        """Build optimization prompt"""
        
        return f"""
You are a logistics expert optimizing DME delivery routes in Southern California.

AVAILABLE DRIVERS TODAY:
{json.dumps(drivers, indent=2)}

ORDERS TO ASSIGN AND ROUTE:
{json.dumps(orders, indent=2)}

TASKS:
1. Assign each order to the BEST driver based on:
   - Geographic proximity (driver's coverage areas, cities, zip codes)
   - Balanced workload across drivers
   - Driver availability and start location

2. For each driver's orders, optimize stop sequence to:
   - MINIMIZE total drive time and distance
   - Respect ALL time windows (CRITICAL - cannot be violated)
   - Consider Southern California traffic patterns
   - Provide realistic ETAs

3. Calculate for each stop:
   - Drive time from previous stop (minutes)
   - ETA (estimated time of arrival)
   - Validate time window feasibility
   - Estimate stop duration (30-60 min for delivery/setup)

4. Provide route summary:
   - Total stops
   - Total distance (miles)
   - Total drive time (minutes)
   - Estimated finish time

CONSTRAINTS:
- MUST respect time windows
- Assume 30-60 min per stop (delivery/pickup/setup)
- Use realistic Southern California drive times
- Start times and locations per driver are specified

RETURN THIS EXACT JSON FORMAT:
{{
  "routes": {{
    "Driver Name": {{
      "stops": [
        {{
          "stop_number": 1,
          "order_id": "index or ID",
          "address": "full address",
          "city": "city",
          "order_type": "Delivery/Pickup",
          "items": "items list",
          "time_window": "HH:MM AM/PM - HH:MM AM/PM",
          "eta": "HH:MM AM/PM",
          "drive_time_from_previous_min": 0,
          "stop_duration_min": 45,
          "time_window_ok": true,
          "special_notes": "notes if any"
        }}
      ],
      "summary": {{
        "total_stops": 3,
        "total_distance_miles": 45,
        "total_drive_time_min": 120,
        "total_stop_time_min": 135,
        "start_time": "10:00 AM",
        "start_location": "Long Beach",
        "estimated_finish": "2:15 PM"
      }}
    }}
  }},
  "unassigned_orders": [],
  "warnings": []
}}

IMPORTANT:
- Use 12-hour format with AM/PM
- Flag time window conflicts in warnings
- Put unassignable orders in unassigned_orders array
- Provide clear reasoning for any issues

Begin optimization now.
"""
