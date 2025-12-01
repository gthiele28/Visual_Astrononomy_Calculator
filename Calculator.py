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
import ast
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

#Want to go from .1 in best possible conditions to .65 in worst conditions
#Although ideally in bad seeing with no clouds worst possible would be .5
#Goal of somewhat emulating stellarium values (.1 for highest mountains/best sites, .2 for very good lowland locations, .35 for typical lowland, .5 in humid climates)
def find_atmospheric_extinction(dew, transparency, seeing, temperature, clouds):
    #Estimates magnitude/airmass extinguished by atmosphere, critical
    #For determining relative magnitude of objects
    #Assume temperatures in farenheit for this function
    #returns a float representing the coefficient
    #formula: .1 + .25 * humidity% + .15 * transparency + .15 * seeing
    
    #formula skips straight to maximum value if cloud cover above 50%
    if clouds > 50:
        print("Cloud cover above 50%, it's a bad idea to observe at this time")
        return .75
    
    relative_humidity = abs((5 * (temperature - 20 - dew)) / 100) #0-1 humidity

    transparency = transparency.replace("\n", "")
    seeing = seeing.replace("\n", "")

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
        print("unable to detect seeing value")

    return .1 + (.25 * relative_humidity) + (.15 * transparency_float) + (.15 * seeing_float)

def find_zenith(user_dt, lati, long):
    time = Time(user_dt)
    loc = EarthLocation(lat = lati * u.deg, lon = long * u.deg)

    frame = AltAz(obstime = time, location = loc)
    zenith_altaz = SkyCoord(alt = 90*u.deg, az = 0*u.deg, frame=frame)

    zenith_radec = zenith_altaz.transform_to('icrs')
    print(zenith_radec)
    return zenith_radec

#Given the dictionary with the entry, it determines whether the object is in the night sky currently
#It also returns angular separation to save some computation time for can_be_resolved
def is_above_horizon(entry, zenith,limit=90.):
    try:
        ra_set = entry["Right Ascension"].split(":")
        dec_set = entry["Declination"].split(":")
        dec_set[2] = dec_set[2].replace("PM", "")
    except KeyError:
        return [False] #skip objects without the full coordinate set to avoid errors

    ra_deg = 15 * (float(ra_set[0]) + float(ra_set[1])/60 + float(ra_set[2])/3600)

    if float(dec_set[0]) < 0:
        sign = -1
    else:
        sign = 1
    
    dec_deg = sign * (abs(float(dec_set[0])) + float(dec_set[1])/60 + float(dec_set[2])/3600)

    sky_location = SkyCoord(ra=ra_deg*u.deg, dec=dec_deg*u.deg)

    distance = sky_location.separation(zenith).deg

    if distance < limit:
        return [True, distance]
    else:
        return [False, distance]

def can_be_resolved(entry, lm, sqm, separation_deg, atmospheric_extinction_coefficient=.1):
    try:
        magnitude = float(entry["V-mag (visual)"])
    except KeyError:
        try:
            magnitude = float(entry["B-mag (blue)"])
        except KeyError:
            magnitude = None
    
    try:
        surface_brightness = entry["Surface brightness"]
        surface_brightness = surface_brightness.replace("mag/arcsec<sup>2</sup>", "")
        surface_brightness = float(surface_brightness)
    except KeyError:
        surface_brightness = None

    if magnitude == None and surface_brightness == None:
        return False

    airmasses = 1/np.cos(np.deg2rad(separation_deg))

    if magnitude != None and surface_brightness != None:
        magnitude = magnitude + (atmospheric_extinction_coefficient * airmasses)
        surface_brightness = surface_brightness + (atmospheric_extinction_coefficient * airmasses)
        
        #if telescope can pick up object and it's brighter than black sky
        if lm > magnitude and sqm > surface_brightness:
            return True
        else:
            return False
    elif magnitude != None:
        magnitude = magnitude + (atmospheric_extinction_coefficient * airmasses)
        if lm > magnitude:
            return True
        else:
            return False
    elif sqm != None: #this one may cause some false positives, but I doubt an object won't have magnitude and get this far
        surface_brightness = surface_brightness + (atmospheric_extinction_coefficient * airmasses)
        if sqm > surface_brightness:
            return True
        else:
            return False
    else: #catch anything slipping thru the cracks
        return False



#Order of results from weather_info.txt (each on its own line):
#Bortle, SQM, Moon illumination %, Moonrise (24h), Moonset (24h),
#Cloud cover, Transparency, Seeing, Wind, Temperature (F), Dew Point (F)

def full_calc(weatherPath, datePath, locationPath, scopePath, datapaths):
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
    #It's worth noting that, unlike moonlight, both magnitude and surface brightness
    #experience the same extinction coefficient and airmasses
    atmospheric_extinction_coefficient = find_atmospheric_extinction(dew_point, transparency, seeing, temperature, cloud_cover)
    print(atmospheric_extinction_coefficient)

    #4. Calculate location of Zenith in RA/DEC
    zenith = find_zenith(date_time, lat, lon)
    
    #4.5 Create "horizon buffer" for high light-pollution areas
    if bortle > 7.0:
        limit = 83.
    elif bortle > 8.0:
        limit = 75.
    else:
        limit = 90.

    visible_in_sky = []
    for i in datapaths:
        curr_file = open(i, "r")
        entries = curr_file.readlines()
        for j in entries:
            #5. Loop through data files and determine which are within 90deg of Zenith
            #  (will need a function to convert the strings for these values into normal floats)
            #  (and need to convert from hours, minutes, seconds, etc into degrees)
            curr_entry = ast.literal_eval(j) #load string as a full dictionary
            horizon = is_above_horizon(curr_entry, zenith, limit)
            if horizon[0]:
                #6. For those within 90deg of zenith, filter out those too dim to be seen
                #Use magnitude for dense/"point" objects like star clusters,
                #SQM for diffuse objects like nebulae
                if can_be_resolved(curr_entry, scope_lm, horizon[1], atmospheric_extinction_coefficient):
                    visible_in_sky.append(curr_entry)
                    try:
                        print("Visible Object Found! " + curr_entry["NGC"])
                    except KeyError:
                        try:
                            print("Visible Object Found! " + curr_entry["IC"])
                        except KeyError:
                            print("No clue what this is, but you found something!")

    #7. Store results as a .json of the raw dictionaries which meet these 
    #   condtions in a separate location

    #8. Print brightest 20 objects to the user

    weatherFile.close()
    dateFile.close()
    locationFile.close()
    scopeFile.close()

if __name__ == "__main__":
    datapaths = ["Data Collection/Complete Datasets/raw_NGC.json", "Data Collection/Complete Datasets/raw_IC.json"]
    full_calc("Weather/weather_info.txt", "Inputs/date.txt", "Inputs/location.txt", "Inputs/telescope.txt", datapaths)