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