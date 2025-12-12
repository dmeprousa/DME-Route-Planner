"""
Maps utilities for generating navigation links
"""

import urllib.parse

def create_google_maps_url(address: str) -> str:
    """Create Google Maps navigation URL"""
    encoded = urllib.parse.quote(address)
    return f"https://www.google.com/maps/dir/?api=1&destination={encoded}"

def create_multi_stop_url(stops: list) -> str:
    """Create Google Maps URL with multiple waypoints"""
    if not stops:
        return ""
    
    # First stop is destination
    destination = urllib.parse.quote(stops[-1])
    
    # Middle stops are waypoints
    if len(stops) > 1:
        waypoints = '|'.join([urllib.parse.quote(stop) for stop in stops[:-1]])
        return f"https://www.google.com/maps/dir/?api=1&destination={destination}&waypoints={waypoints}"
    else:
        return f"https://www.google.com/maps/dir/?api=1&destination={destination}"

def create_search_url(query: str) -> str:
    """Create Google Maps search URL"""
    encoded = urllib.parse.quote(query)
    return f"https://www.google.com/maps/search/?api=1&query={encoded}"
