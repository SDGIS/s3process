"""
Nautical Twilight Calculator

Calculates nautical dusk and dawn times for a given location and date range.
Nautical twilight is defined as when the sun is between 6° and 12° below the horizon.
- Nautical dawn: when the sun reaches 12° below the horizon in the morning
- Nautical dusk: when the sun reaches 12° below the horizon in the evening
"""

import math
from datetime import datetime, timedelta

def calculate_nautical_twilight(latitude, longitude, elevation=0, days=5):
    """
    Main function to calculate nautical twilight times for the next specified number of days.
    
    Args:
        latitude (float): Latitude in degrees
        longitude (float): Longitude in degrees
        elevation (float, optional): Elevation in meters. Defaults to 0.
        days (int, optional): Number of days to calculate. Defaults to 5.
        
    Returns:
        list: List of dictionaries containing date, nautical dawn, and nautical dusk times
    """
    results = []
    today = datetime.now()
    
    for i in range(days):
        date = today + timedelta(days=i)
        
        nautical_dawn = calculate_nautical_dawn(date, latitude, longitude, elevation)
        nautical_dusk = calculate_nautical_dusk(date, latitude, longitude, elevation)
        
        results.append({
            "date": format_date(date),
            "nautical_dawn": format_time(nautical_dawn),
            "nautical_dusk": format_time(nautical_dusk)
        })
    
    return results

def calculate_nautical_dawn(date, latitude, longitude, elevation):
    """Calculate nautical dawn (sun reaches 12° below horizon in morning)"""
    return calculate_sun_time(date, latitude, longitude, elevation, -12, True)

def calculate_nautical_dusk(date, latitude, longitude, elevation):
    """Calculate nautical dusk (sun reaches 12° below horizon in evening)"""
    return calculate_sun_time(date, latitude, longitude, elevation, -12, False)

def calculate_sun_time(date, latitude, longitude, elevation, angle, is_rising):
    """
    Calculate time when sun reaches specified angle
    
    Args:
        date (datetime): Date to calculate for
        latitude (float): Latitude in degrees
        longitude (float): Longitude in degrees
        elevation (float): Elevation in meters
        angle (float): Sun angle in degrees (negative for below horizon)
        is_rising (bool): True for rising (dawn), False for setting (dusk)
        
    Returns:
        datetime: Time when sun reaches the specified angle, or None if it never happens
    """
    # Convert latitude and longitude from degrees to radians
    lat = math.radians(latitude)
    lng = math.radians(longitude)
    
    # Date calculations
    year = date.year
    month = date.month
    day = date.day
    
    # Get day of year
    N1 = math.floor(275 * month / 9)
    N2 = math.floor((month + 9) / 12)
    N3 = (1 + math.floor((year - 4 * math.floor(year / 4) + 2) / 3))
    N = N1 - (N2 * N3) + day - 30
    
    # Approximate time
    lng_hour = longitude / 15
    
    # Calculate initial time based on whether we want sunrise or sunset
    if is_rising:
        # For nautical dawn
        t = N + ((6 - lng_hour) / 24)
    else:
        # For nautical dusk
        t = N + ((18 - lng_hour) / 24)
    
    # Calculate Sun's mean anomaly
    M = (0.9856 * t) - 3.289
    
    # Calculate Sun's true longitude
    L = M + (1.916 * math.sin(math.radians(M))) + (0.020 * math.sin(math.radians(2 * M))) + 282.634
    # Adjust into 0-360 range
    L = (L + 360) % 360
    
    # Calculate Sun's right ascension
    RA = math.degrees(math.atan(0.91764 * math.tan(math.radians(L))))
    # Adjust into 0-360 range
    RA = (RA + 360) % 360
    
    # Adjust RA to be in same quadrant as L
    Lquadrant = math.floor(L / 90) * 90
    RAquadrant = math.floor(RA / 90) * 90
    RA = RA + (Lquadrant - RAquadrant)
    
    # Convert RA to hours
    RA = RA / 15
    
    # Calculate Sun's declination
    sin_dec = 0.39782 * math.sin(math.radians(L))
    cos_dec = math.cos(math.asin(sin_dec))
    
    # Calculate Sun's local hour angle
    cos_H = (math.sin(math.radians(angle)) - (sin_dec * math.sin(lat))) / (cos_dec * math.cos(lat))
    
    # Check if sun never reaches the specified angle
    if cos_H > 1:
        return None  # Sun never reaches the angle below horizon at this location (e.g., polar day)
    if cos_H < -1:
        return None  # Sun never reaches the angle above horizon at this location (e.g., polar night)
    
    # Calculate H and convert to hours
    if is_rising:
        H = 360 - math.degrees(math.acos(cos_H))
    else:
        H = math.degrees(math.acos(cos_H))
    H = H / 15
    
    # Calculate local mean time of rising/setting
    T = H + RA - (0.06571 * t) - 6.622
    
    # Adjust for UTC
    UT = T - lng_hour
    # Adjust into 0-24 range
    UT = (UT + 24) % 24
    
    # Convert UT to local date and time
    hours = math.floor(UT)
    minutes = math.floor((UT - hours) * 60)
    seconds = math.floor(((UT - hours) * 60 - minutes) * 60)
    
    # Create datetime object with calculated time
    result_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    result_date = result_date.replace(hour=hours, minute=minutes, second=seconds)
    
    # Apply elevation adjustment if provided
    if elevation > 0:
        # Approximate adjustment: for every 1000m elevation, sun rises about 1 minute earlier and sets 1 minute later
        elevation_adjustment = (elevation / 1000) * 60  # in seconds
        if is_rising:
            result_date = result_date - timedelta(seconds=elevation_adjustment)
        else:
            result_date = result_date + timedelta(seconds=elevation_adjustment)
    
    return result_date

def format_date(date):
    """Format date as YYYY-MM-DD"""
    return date.strftime("%Y-%m-%d")

def format_time(date):
    """Format time as HH:MM:SS"""
    if date is None:
        return "Not occurring"
    return date.strftime("%H:%M:%S")

# Example usage:
# results = calculate_nautical_twilight(40.7128, -74.0060, 10)
# print(results)