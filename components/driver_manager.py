"""
Driver Manager Component - Manage driver selection and configuration
"""

from typing import List, Dict

class DriverManager:
    
    @staticmethod
    def filter_available(drivers: List[Dict], selected_ids: List[str]) -> List[Dict]:
        """Filter drivers by selection"""
        return [d for d in drivers if d.get('driver_id') in selected_ids]
    
    @staticmethod
    def prepare_for_optimization(drivers: List[Dict], config: Dict) -> List[Dict]:
        """
        Prepare drivers for route optimization
        
        Args:
            drivers: List of driver dicts
            config: Dict with per-driver configuration (start_time, start_location)
        
        Returns:
            List of drivers with config applied
        """
        prepared = []
        
        for driver in drivers:
            driver_id = driver.get('driver_id')
            driver_config = config.get(driver_id, {})
            
            prepared_driver = driver.copy()
            
            # Apply overrides from config
            if 'start_time' in driver_config:
                prepared_driver['start_time'] = driver_config['start_time']
            elif 'start_time' not in prepared_driver:
                prepared_driver['start_time'] = '09:00 AM'
            
            if 'start_location' in driver_config:
                prepared_driver['start_location'] = driver_config['start_location']
            elif not prepared_driver.get('start_location'):
                prepared_driver['start_location'] = 'Office'
            
            prepared.append(prepared_driver)
        
        return prepared
    
    @staticmethod
    def format_driver_summary(driver: Dict) -> str:
        """Format driver info for display"""
        name = driver.get('driver_name', 'Unknown')
        areas = driver.get('primary_areas', 'N/A')
        cities = driver.get('cities_covered', 'N/A')
        
        return f"**{name}**\nAreas: {areas}\nCities: {cities}"
