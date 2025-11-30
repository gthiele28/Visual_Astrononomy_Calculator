'''Goals for this script:
1. Read inputs from user and WeatherScraper in a .txt file
2. Do additional calculations for extra needed data
3. Determine which objects in the sky are available
4. Determine which of the user's eyepieces/which eyepiece 
size/fov combo is ideal for each object
5. return a list of objects with their sky coordinates,
common names/NGC ids to the user
'''

def find_nelm(bortle_class): 
    #calculate naked eye limiting magnitude from bortle
    #Bortle goes from 1.0 -> 9.0, and NELM goes from
    #8.0 @ 1.0 -> 7.5 @ 2.0... -> 4.0 @ 9.0 
    #each full class corresponds to .5 Magnitude, so:
    #NELM = 4.0 + .5(9 - bortle_class)

    nelm = 4.0 + (0.5 * (9 - bortle_class))
    return nelm

#Order of results from weather_info.txt (each on its own line):
#Bortle, SQM, Moon illumination %, Moonrise (24h), Moonset (24h),
#Cloud cover, Transparency, Seeing, Wind, Temperature (F), Dew Point (F)

def full_calc(weatherPath, datePath, locationPath):
    weatherFile = open(weatherPath, "r")
    dateFile = open(datePath, "r")
    locationFile = open(locationPath, "r")

    #Assign each value from these files to their own variables and
    #reformat them as deseired before continuing

    #0. Add ability to take telescope measurements to getInputs.py,
    #   Include default numbers for naked eye and binocular setting?

    #1. Find telescope limiting magnitude (NELM + amount of extra light collected)

    #2. Add to limiting magnitude and SQM by moon phase

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

if __name__ == "__main__":
    full_calc("Weather/weather_info.txt", "Inputs/date.txt", "Inputs/location.txt")