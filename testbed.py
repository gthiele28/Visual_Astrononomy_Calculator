from astropy.coordinates import EarthLocation, AltAz, get_body
from astropy.time import Time
import astropy.units as u

def is_moon_up(latitude, longitude, time_str):
    """
    Determines if the Moon is up at a specific location and time.

    Args:
        latitude (float): Latitude in degrees.
        longitude (float): Longitude in degrees (east is positive).
        time_str (str): Time string (e.g., '2025-11-30 14:00').

    Returns:
        bool: True if the Moon is above the horizon, False otherwise.
    """
    # 1. Define the observation location
    location = EarthLocation(lat=latitude * u.deg, lon=longitude * u.deg)

    # 2. Define the observation time
    time = Time(time_str)

    # 3. Get the Moon's position in ICRS coordinates
    # This might require a one-time download of a JPL ephemeris file (~10MB)
    moon_coord = get_body("moon", time, location)

    # 4. Transform the Moon's coordinates to the local Altitude-Azimuth (horizontal) system
    frame = AltAz(obstime=time, location=location)
    moon_altaz = moon_coord.transform_to(frame)

    # 5. Check the altitude
    altitude = moon_altaz.alt.deg
    print(f"The Moon's altitude is: {altitude:.2f} degrees.")

    if altitude > 0:
        return True
    else:
        return False

# --- Example Usage ---
# Using current time and a location (e.g., San Diego, CA)
current_time = Time.now()
print(current_time)
moon_status = is_moon_up(latitude=32.7157, longitude=-117.1611, time_str=current_time.iso)

if moon_status:
    print("The Moon is currently UP.")
else:
    print("The Moon is currently DOWN (below the horizon).")