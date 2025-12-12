"""
Route Formatter - Format optimized routes for display and export
"""

from typing import Dict
import urllib.parse

class RouteFormatter:
    
    @staticmethod
    def format_for_display(routes: Dict) -> str:
        """Format routes for Streamlit display"""
        output = []
        
        for driver_name, route_data in routes.items():
            summary = route_data.get('summary', {})
            stops = route_data.get('stops', [])
            
            output.append(f"\n## 🚚 {driver_name}\n")
            output.append(f"**{summary.get('total_stops', 0)} stops** | ")
            output.append(f"**{summary.get('total_distance_miles', 0)} miles** | ")
            output.append(f"**{summary.get('total_drive_time_min', 0)} min drive time**\n")
            output.append(f"Start: {summary.get('start_time', 'TBD')} from {summary.get('start_location', 'TBD')}\n")
            output.append(f"Finish: {summary.get('estimated_finish', 'TBD')}\n\n")
            
            for stop in stops:
                output.append(f"### Stop {stop['stop_number']}: {stop['order_type']}\n")
                output.append(f"📍 {stop['address']}, {stop['city']}\n")
                output.append(f"📦 {stop['items']}\n")
                output.append(f"⏰ ETA: {stop['eta']} (Window: {stop['time_window']})\n")
                if stop.get('special_notes'):
                    output.append(f"⚠️ {stop['special_notes']}\n")
                output.append("\n")
        
        return "".join(output)
    
    @staticmethod
    def format_for_whatsapp(driver_name: str, route_data: Dict, date: str) -> str:
        """Format route as WhatsApp message"""
        summary = route_data.get('summary', {})
        stops = route_data.get('stops', [])
        
        message = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚚 YOUR ROUTE - {date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 SUMMARY
Total Stops: {summary.get('total_stops', 0)}
Distance: {summary.get('total_distance_miles', 0)} miles
Drive Time: {summary.get('total_drive_time_min', 0)} min
Stop Time: {summary.get('total_stop_time_min', 0)} min
Start: {summary.get('start_time', 'TBD')} from {summary.get('start_location', 'TBD')}
Finish: {summary.get('estimated_finish', 'TBD')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        for stop in stops:
            nav_url = f"https://www.google.com/maps/dir/?api=1&destination={urllib.parse.quote(stop['address'])}"
            
            message += f"""
{stop['stop_number']}. 📦 {stop['order_type'].upper()}
   📍 {stop['address']}
   ⏰ ETA: {stop['eta']}
   📦 Items: {stop['items']}
   🕐 Window: {stop['time_window']}
   {f"⚠️ {stop['special_notes']}" if stop.get('special_notes') else ''}
   
   Navigate: {nav_url}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        message += "\n✅ Route optimized by DME AI\n📱 Questions? Call Cyrus: 760-879-1071"
        
        return message
    
    @staticmethod
    def format_stops_as_dataframe(routes: Dict):
        """Format all stops as pandas DataFrame"""
        import pandas as pd
        
        rows = []
        for driver_name, route_data in routes.items():
            for stop in route_data.get('stops', []):
                rows.append({
                    'Driver': driver_name,
                    'Stop': stop['stop_number'],
                    'Type': stop['order_type'],
                    'Address': stop['address'],
                    'City': stop['city'],
                    'Items': stop['items'],
                    'ETA': stop['eta'],
                    'Window': stop['time_window'],
                    'Notes': stop.get('special_notes', '')
                })
        
        return pd.DataFrame(rows)
