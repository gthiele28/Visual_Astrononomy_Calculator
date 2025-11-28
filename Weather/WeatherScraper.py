#WE NEED (GUESSING)
#Temperature
#Humidity
#Dew point (?)
#Air quality (?)
#Light Pollution (Bortle Class Ideal) - found in lpma
#Moonrise/Moonset - found in lpma
#Moon % illuminated - found in lpma
#Altitude (?) 
#SQM - found in lpma

#USING ONLY LOCATION AS INPUTS

import selenium
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

outputs = open("Weather/weather_info.txt", "w")
inputs = open("Inputs/location.txt", "r")

coords = inputs.readlines()
coords[0] = float(coords[0])
coords[1] = float(coords[1])

#TODO: IF YOU DON'T HAVE AN M SERIES MAC, DOWNLOAD A DIFFERENT VERSION,
#DRAG IT HERE AND CHANGE THE FOLDER NAME IN PATH HERE TO MATCH
#IF YOU ALSO USE AN ARM-64 MAC, JUST LEAVE THIS AND IT WILL WORK
path = "chromedriver-mac-arm64/chromedriver"


def from_html(source, id, cut_s, cut_f):
    #given html source code and an id to search for,
    #return the value stored for that id within the HTML
    #Arguments:
    #source: html source code, ideally a string
    #id: a string to search for (the value is on the right of it)
    #cut_s: a shorter string which occurs directly to the left of the value
    #cut_f: whatever is directly to the right of the value
    #i.e.: source = <div id="blah">value</div>
    #to get value:
    #id = '''id="blah''', cut_s = '">', cut_f = "</div>"
    #rtype: string containing target value

    start = source.find(id)
    end = source.find(cut_f, start)
    source = source[start:end + len(cut_f) + 1] #tried to unhardcode 300 and it shat itself

    start = source.find(cut_s)
    end = source.find(cut_f)

    return source[start + len(cut_s):end]


def get_astrospheric_data(lat, lon):
    url = "https://www.astrospheric.com/?Latitude=" + str(lat) + "&Longitude=" +  str(lon) + "&Loc=Forecast"    
    
    cService = webdriver.ChromeService(executable_path=path)
    driver = webdriver.Chrome(service=cService)
    driver.get(url)

    #If a forecast limit is hit, wait 20 seconds then click try again
    #since that's the longest possible wait time the site gives
    #If the date is invalid or anything else, just return average for all
    #transparency data, 0% cloud cover, etc. since that's easier

    #make sure user-provided date/time is valid, if not just default to
    #current system date/time to prevent errors later on
    try:
        dfile = open("Inputs/date.txt", "r")
        date = dfile.readlines()
        user_dt = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(date[3]), int(date[4]), 0, 0)
        print("Now finding data for " + str(user_dt))
    except ValueError:
        print("user-provided date/time is invalid.  Continuing with current system time instead.")
        user_dt = datetime.datetime.now()

    #Seems like selenium driver never triggers this, but
    #still good practice to keep in although testing is impossible
    try:
        error = driver.WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "s_ForecastError"))
        )
        print("ForecastError found, waiting out rate limit")
        time.sleep(11) #1 extra second for safety
        driver.navigate.refresh()
    except Exception:
        print("ForecastError not found, continuing as normal")

    #now, we just need to find if there's a container which has the date
    #and hour we want, if it there is we just click on it then take the data
    #related to it from the 6 boxes on the bottom.
    day_of_week = user_dt.weekday()
    if day_of_week == 0:
        day_of_week = "Mon"
    elif day_of_week == 1:
        day_of_week = "Tue"
    elif day_of_week == 2:
        day_of_week = "Wed"
    elif day_of_week == 3:
        day_of_week = "Thu"
    elif day_of_week == 4:
        day_of_week = "Fri"
    elif day_of_week == 5:
        day_of_week = "Sat"
    elif day_of_week == 6:
        day_of_week = "Sun"

    search_string = day_of_week + " " + str(user_dt.day)

    #Determine if the user's date is findable based on the list on the site
    forecastContainer = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "d_ForecastContainer"))
    )
    dates = forecastContainer.find_elements(By.CLASS_NAME, "s_DayMarker")
    first_date = dates[0].text
    print(first_date)
    first_hour = forecastContainer.find_element(By.ID, "hid0")
    hour_num = first_hour.text
    try:
        first_hour.find_element((By.CSS_SELECTOR, "span[style*='font-weight: bold;]'"))
        #only done if the PM indicator (bold style span) is located
        hour_num += 12
        if hour_num == 24:
            hour_num = 0 #adjust to account for midnight
    except Exception:
        print("didn't find it")
        pass

    print(hour_num)
    driver.close()
    return []

#LPMA moonrise/moonset data only relevant if date given matches
#Current date.  It's possible calculating those numbers manually
#instead in this case may be the better option to estimate, but
#that can wait for a basic version to be completed.

def get_lpma_data(lat, lon):
    '''Given latitude and longitude, use Selenium to get
    accurate light pollution data through a dummy web browser
    Both inputs should be floats, and the output:
    [bortle class (float), sqm (float), moon illumination % 
    (float 0-100), moonrise(string, time, 24h format), moonset(string, time, 24h format)]'''
    
    url = "https://lightpollutionmap.app/?lat=" + str(lat) + "&lng=" + str(lon) + "&zoom=17"

    cService = webdriver.ChromeService(executable_path=path)
   
    driver = webdriver.Chrome(service=cService)

    driver.get(url)
    
    #Get bortle class, wait for site to load a value into it and make it visible
    bortle_place = WebDriverWait(driver, 10.).until(
        EC.visibility_of_element_located((By.ID, "pollution-value"))
    )
    bortle = bortle_place.text

    #Not an option for sqm, so to load it we have to sort thru the source code
    html_content = driver.page_source
    sqm = from_html(html_content, "sqm-value", '''="">''', "</div>")


    illumination_percent = from_html(html_content, '''id="moon-illumination"''',">", "%</span>")
    
    #hard to get an identifier, so preorganize by cutting size down early
    moon_code = html_content[html_content.find('''<div id="moon-times-list"'''): html_content.find('''<span id="current-time"''')]
    moonrise = from_html(moon_code, '''<span class="font-medium">''', '''<span class="font-medium">''', "</span>")

    #need same class for both moon times to avoid getting caught by text changes, trim again
    moon_code = moon_code[moon_code.find('''<span class="font-medium">''') + len('''<span class="font-medium">'''):]
    moonset = from_html(moon_code, '''<span class="font-medium">''', '''<span class="font-medium">''', "</span>")

    driver.close()
    return [float(bortle), float(sqm), float(illumination_percent), moonrise, moonset]

#print(get_lpma_data(coords[0],coords[1]))
print(get_astrospheric_data(coords[0], coords[1]))