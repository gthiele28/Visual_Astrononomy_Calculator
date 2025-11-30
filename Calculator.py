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
import datetime
import astropy
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_body
from astropy.time import Time
import astropy.units as u

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
    moon_coords = get_body("moon", t)
    moon_altaz = moon_coords.transform_to(AltAz(location=loc, obstime=t))

    if moon_altaz.alt > 0 * u.deg:
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

#Order of results from weather_info.txt (each on its own line):
#Bortle, SQM, Moon illumination %, Moonrise (24h), Moonset (24h),
#Cloud cover, Transparency, Seeing, Wind, Temperature (F), Dew Point (F)

def full_calc(weatherPath, datePath, locationPath, scopePath):
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
    
    #Moonrise and moonset scraping turned out to be useless as the site is inconsistent
    #Using astropy for this will hopefully solve the problem, and also make adding planet
    #support easier in the future if there's time

    # moonrise = weatherVals[3]
    # if moonrise != "\n":
    #     moonrise = moonrise.split(":")
    #     moonrise = datetime.time(int(moonrise[0]), int(moonrise[1]), 0, 0)
    # else:
    #     moonrise = None

    # moonset = weatherVals[4]
    # if moonset != "\n":
    #     moonset = moonset.split(":")
    #     moonrise = datetime.time(int(moonset[0]), int(moonset[1]), 0, 0)
    # else:
    #     moonset = None

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
        dew_risk = True
    else:
        dew_risk = False
    dew_point = "".join([i for i in dew_point if i.isdigit()]) #separate all non-int values to account for celsius
    dew_point = int(dew_point)

    dateVals = dateFile.readlines()
    date_time = datetime.datetime(int(dateVals[0]), int(dateVals[1]), int(dateVals[2]), int(dateVals[3]), int(dateVals[4]), 0, 0)

    locationVals = locationFile.readlines()
    lat = float(locationVals[0])
    lon = float(locationVals[1])

    scopeVals = scopeFile.readlines()
    aperture_mm = float(scopeVals[0])
    f_ratio = float(scopeVals[1])

    #1. Find telescope limiting magnitude (NELM + amount of extra light collected)
    scope_lm = find_scopelm(aperture_mm, find_nelm(bortle))

    #2. Subtract from limiting magnitude and add to SQM by moon phase (if it's above the horizon)
    if is_moon_up(date_time, lat, lon):
        print("moon is up!")
    else:
        print("No it's not!")

    #3. Calculate atmospheric extinction coefficient (in magnitudes/airmass)

    #4. Calculate location of Zenith in RA/DEC

    #5. Loop through data files and determine which are within 90deg of Zenith
    #  (will need a function to convert the strings for these values into normal floats)

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