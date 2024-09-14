import pytz
from timezonefinder import TimezoneFinder
from datetime import datetime, timedelta
from pysolar.solar import get_altitude
import math
import time
import warnings

# TODO import GDAL and make sure elevation calculation works.

# Suppress specific warning about leap seconds
warnings.filterwarnings("ignore", message="I don't know about leap seconds after 2023")

# Function to extract elevation from a DEM using lat/lon
def get_elevation_from_dem(dem_path, lat, lon):
    dem = gdal.Open(dem_path)
    transform = dem.GetGeoTransform()
    x = int((lon - transform[0]) / transform[1])
    y = int((lat - transform[3]) / transform[5])
    band = dem.GetRasterBand(1)
    elevation_array = band.ReadAsArray()
    elevation = elevation_array[y, x]
    return elevation

# Function to apply altitude correction for ground elevation
def altitude_correction(altitude, elevation):
    R = 6371000  # Radius of the Earth in meters
    correction = math.degrees(-math.sqrt(2 * elevation / R))
    return altitude + correction

# Function to calculate altitude at a given time
def calculate_altitude(lat, lon, time):
    utc_time = time.astimezone(pytz.utc)
    return get_altitude(lat, lon, utc_time)

# Function to find sunrise or sunset with 1-hour approximation
def find_boundary_time(lat, lon, initial_time, direction, step_minutes=60):
    current_time = initial_time
    while True:
        altitude = calculate_altitude(lat, lon, current_time)
        if (direction == 'sunrise' and altitude >= 0) or (direction == 'sunset' and altitude < 0):
            return current_time
        current_time += timedelta(minutes=step_minutes)

# Function to refine the civil twilight times within a 2-hour window
def refine_twilight(lat, lon, time, direction, twilight_altitude, dem_path, radius_minutes=120):
    twilight_time = None
    if direction == 'dawn':
        # Search backward from the given time for the first occurrence of twilight_altitude
        for minute in range(0, radius_minutes):
            current_time = time - timedelta(minutes=minute)
            utc_time = current_time.astimezone(pytz.utc)
            altitude = calculate_altitude(lat, lon, current_time)
            elevation = get_elevation_from_dem(dem_path, lat, lon) if dem_path else 0
            corrected_altitude = altitude_correction(altitude, elevation) if dem_path else altitude

            if corrected_altitude <= twilight_altitude:
                twilight_time = current_time
                break
    else:  # direction == 'dusk'
        # Search within a 2-hour window for the first occurrence of twilight_altitude
        for minute in range(-radius_minutes, radius_minutes + 1):
            current_time = time + timedelta(minutes=minute)
            utc_time = current_time.astimezone(pytz.utc)
            altitude = calculate_altitude(lat, lon, current_time)
            elevation = get_elevation_from_dem(dem_path, lat, lon) if dem_path else 0
            corrected_altitude = altitude_correction(altitude, elevation) if dem_path else altitude

            if corrected_altitude <= twilight_altitude:
                twilight_time = current_time
                break
    return twilight_time

# Optimized function to find sunrise, sunset, and civil twilight
def find_civil_twilight(lat, lon, date, timezone, dem_path=None, twilight_altitude=-6.0):
    tz = pytz.timezone(timezone)
    local_time = tz.localize(datetime(date.year, date.month, date.day, 0, 0, 0))

    sunrise = find_boundary_time(lat, lon, local_time, 'sunrise')
    sunset = find_boundary_time(lat, lon, local_time + timedelta(hours=12), 'sunset')  # Start searching for sunset 12 hours after midnight
    print(sunrise, sunset)
    if sunrise is None or sunset is None:
        return None, None

    civil_dawn = refine_twilight(lat, lon, sunrise, 'dawn', twilight_altitude, dem_path)
    civil_dusk = refine_twilight(lat, lon, sunset, 'dusk', twilight_altitude, dem_path)

    return civil_dawn, civil_dusk

# Function to get the timezone string for a given lat/lon
def get_timezone_for_latlon(lat, lon, date=None):
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=lon, lat=lat)
    if timezone_str is None:
        raise ValueError("Timezone could not be determined for the given coordinates.")

    timezone = pytz.timezone(timezone_str)
    if date is None:
        date = datetime.now().date()
    date_time = datetime(date.year, date.month, date.day, 0, 0)
    localized_date = timezone.localize(date_time)
    is_dst = localized_date.dst() != timedelta(0)

    if is_dst:
        print(f"Daylight Saving Time is in effect for {timezone_str} on {date}.")
    else:
        print(f"Standard Time is in effect for {timezone_str} on {date}.")

    return timezone_str