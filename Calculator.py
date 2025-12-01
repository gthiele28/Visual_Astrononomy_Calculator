'''Goals for this script:
1. Read inputs from user and WeatherScraper in a .txt file
2. Do additional calculations for extra needed data
3. Determine which objects in the sky are available
4. Determine which of the user's eyepieces/which eyepiece 
size/fov combo is ideal for each object
5. return a list of objects with their sky coordinates,
common names/NGC ids to the user
'''

import numpy as np
import jplephem
import datetime
import astropy
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_body, solar_system_ephemeris
from astropy.time import Time
import astropy.units as u
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo

def find_nelm(bortle_class): 
    #calculate naked eye limiting magnitude from bortle
    #Bortle goes from 1.0 -> 9.0, and NELM goes from
    #8.0 @ 1.0 -> 7.5 @ 2.0... -> 4.0 @ 9.0 
    #each full class corresponds to .5 Magnitude, so:
    #NELM = 4.0 + .5(9 - bortle_class)

    nelm = 4.0 + (0.5 * (9 - bortle_class))
    return nelm

def find_scopelm(aperture, nelm):
    #Calculate additional light, convert to magnitudes collected, 
    #add to nelm, round for cleanness, return
    #Want aperture as an integer in millimeters and nelm as a float
    #return a float representing limiting magnitude (2 decimal places)

    aperture_cm = aperture / 10
    full_limiting_mag = nelm + (5 * np.log10(aperture_cm))
    return np.round(full_limiting_mag, decimals=2)

def is_moon_up(user_dt, lati, long):

    loc = EarthLocation(lat = lati * u.deg, lon = long * u.deg)
    t = Time(user_dt)

    moon_coords = get_body("moon", t, loc)
    moon_altaz = moon_coords.transform_to(AltAz(location=loc, obstime=t))

    altitude = moon_altaz.alt.deg

    if altitude > 0:
        return True
    else:
        return False

#increased brightness spread across sky effects diffuse objects more,
#so its effect on the SQM is much higher than on magnitude

def moon_sqm_effect(lit):
    #sqm_increase = 4(%lit/100)
    return 4 * (lit/100)

def moon_magnitude_effect(lit):
    #M_reduce = roughly 2.5 (amount lit from 0-1)
    return 2.5 * (lit/100)

#Want to go from .1 in best possible conditions to .75 in worst conditions
#Although ideally in bad seeing with no clouds worst possible would be .5
#Goal of somewhat emulating stellarium values (.1 for highest mountains/best sites, .2 for very good lowland locations, .35 for typical lowland, .5 in humid climates)
def find_atmospheric_extinction(dew, transparency, seeing, temperature, clouds):
    #Estimates magnitude/airmass extinguished by atmosphere, critical
    #For determining relative magnitude of objects
    #Assume temperatures in farenheit for this function
    #returns a float representing the coefficient
    #formula: .1 + .25 * humidity% + .2 * transparency + .2 * seeing
    
    #formula skips straight to maximum value if cloud cover above 50%
    if clouds > 50:
        print("Cloud cover above 50%, it's a bad idea to observe at this time")
        return .75
    
    relative_humidity = abs((5 * (temperature - 20 - dew)) / 100) #0-1 humidity

    transparency_float = 0.
    if transparency == "Cloudy":
        transparency_float = 1.
    elif transparency == "Poor":
        transparency_float = .8
    elif transparency == "Below Average":
        transparency_float = .6
    elif transparency == "Average":
        transparency_float = .4
    elif transparency == "Above Average":
        transparency_float = .2
    elif transparency == "Excellent":
        transparency_float = 0.
    else:
        print("unable to detect transparency value")

    seeing_float = 0.
    if seeing == "Cloudy":
        seeing_float = 1.
    elif seeing == "Poor":
        seeing_float = .8
    elif seeing == "Below Average":
        seeing_float = .6
    elif seeing == "Average":
        seeing_float = .4
    elif seeing == "Above Average":
        seeing_float = .2
    elif seeing == "Excellent":
        seeing_float = 0.
    else:
        print("unable to detect transparency value")

    return .1 + (.25 * relative_humidity) + (.2 * transparency_float) + (.2 * seeing_float)

def find_zenith(user_dt, lati, long):
    time = Time(user_dt)
    loc = EarthLocation(lat = lati * u.deg, lon = long * u.deg)

    frame = AltAz(obstime = time, location = loc)
    zenith_altaz = SkyCoord(alt = 90*u.deg, az = 0*u.deg, frame=frame)

    zenith_radec = zenith_altaz.transform_to('icrs')
    print(zenith_radec)

#Order of results from weather_info.txt (each on its own line):
#Bortle, SQM, Moon illumination %, Moonrise (24h), Moonset (24h),
#Cloud cover, Transparency, Seeing, Wind, Temperature (F), Dew Point (F)

def full_calc(weatherPath, datePath, locationPath, scopePath):
    solar_system_ephemeris.set('jpl') #set to accurate planet/moon model

    weatherFile = open(weatherPath, "r")
    dateFile = open(datePath, "r")
    locationFile = open(locationPath, "r")
    scopeFile = open(scopePath, "r")

    #Assign each value from these files to their own variables and
    #reformat them as deseired before continuing
    weatherVals = weatherFile.readlines()
    bortle = float(weatherVals[0])
    sqm = float(weatherVals[1])
    moon_illumination = float(weatherVals[2])

    cloud_cover = weatherVals[5].replace("%", "")
    cloud_cover = int(cloud_cover)

    transparency = weatherVals[6]
    seeing = weatherVals[7]

    wind = weatherVals[8].replace("mph", "")
    wind = int(wind)

    temperature = weatherVals[9]
    temperature = "".join([i for i in temperature if i.isdigit()]) #separate all non-int values to account for celsius
    temperature = int(temperature)

    dew_point = weatherVals[10]
    if dew_point.find("!!!") != -1: #dew forming on optics is a risk
        print("Bring a heater or hair dryer for your optics!  Temperature is low enough they may attract dew")
        dew_risk = True
    else:
        dew_risk = False
    dew_point = "".join([i for i in dew_point if i.isdigit()]) #separate all non-int values to account for celsius
    dew_point = int(dew_point)

    locationVals = locationFile.readlines()
    lat = float(locationVals[0])
    lon = float(locationVals[1])

    #Include timezone data for accurate location
    timezone = TimezoneFinder().timezone_at(lat=lat, lng=lon)
    dateVals = dateFile.readlines()
    if timezone:
        timezone_info = ZoneInfo(timezone)
        date_time = datetime.datetime(int(dateVals[0]), int(dateVals[1]), int(dateVals[2]), int(dateVals[3]), int(dateVals[4]), 0, 0, timezone_info)
    else:
        print("Unable to determine your time zone based on provided coordinates.  Your results may not be accurate")
        date_time = datetime.datetime(int(dateVals[0]), int(dateVals[1]), int(dateVals[2]), int(dateVals[3]), int(dateVals[4]), 0, 0)

    scopeVals = scopeFile.readlines()
    aperture_mm = float(scopeVals[0])
    f_ratio = float(scopeVals[1])

    #1. Find telescope limiting magnitude (NELM + amount of extra light collected)
    scope_lm = find_scopelm(aperture_mm, find_nelm(bortle))

    #2. Subtract from limiting magnitude and add to SQM by moon phase (if it's above the horizon)
    if is_moon_up(date_time, lat, lon):
        print("The Moon is up, potentially making it harder to view dimmer or diffuse objects")
        scope_lm -= moon_magnitude_effect(moon_illumination)
        sqm -= moon_sqm_effect(moon_illumination)
    else:
        print("The moon is not up, meaning it won't effect your viewing")

    #3. Calculate atmospheric extinction coefficient (in magnitudes/airmass)
    atmospheric_extinction_coefficient = find_atmospheric_extinction(dew_point, transparency, seeing, temperature, cloud_cover)
    print(atmospheric_extinction_coefficient)

    #4. Calculate location of Zenith in RA/DEC
    zenith = find_zenith(date_time, lat, lon)

    #5. Loop through data files and determine which are within 90deg of Zenith
    #  (will need a function to convert the strings for these values into normal floats)
    #  (and need to convert from hours, minutes, seconds, etc into degrees)

    #6. For those within 90deg of zenith, filter out those too dim to be seen
    #Use magnitude for dense/"point" objects like star clusters,
    #SQM for diffuse objects like nebulae

    #7. Store results as a .json of the raw dictionaries which meet these 
    #   condtions in a separate location

    #8. Create an additional file through which the user can check
    #   for specific objects, find brightest available objects, filter by
    #   object type, etc?

    weatherFile.close()
    dateFile.close()
    locationFile.close()
    scopeFile.close()

if __name__ == "__main__":
    full_calc("Weather/weather_info.txt", "Inputs/date.txt", "Inputs/location.txt", "Inputs/telescope.txt")