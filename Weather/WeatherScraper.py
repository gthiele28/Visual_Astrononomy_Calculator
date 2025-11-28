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

import time
import selenium
from selenium import webdriver
import selenium.webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

outputs = open("Weather/weather_info.txt", "w")
inputs = open("Inputs/location.txt", "r")

coords = inputs.readlines()
coords[0] = float(coords[0])
coords[1] = float(coords[1])

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
    pass

#without a complex "state" impossible to get data from this site
#may not be able to get needed data from here. Use a set of points
#and find a line of best fit with plotting?
def get_lpmi_data(lat, lon):
    pass

#After some testing, it's clear that simply taking data won't work
#the site needs to let some Javascript run and fill in gaps or else
#no data will be received and can't be scraped for by my scripting
#therefore, selenium may be the only way to get this data
def get_lpma_data(lat, lon):
    '''Given latitude and longitude, use Selenium to get
    accurate light pollution data through a dummy web browser
    Both inputs should be floats, and the output:
    [bortle class (float), sqm (float), moon illumination % 
    (float 0-100), moonrise(string, time, 24h format), moonset(string, time, 24h format)]'''
    
    url = "https://lightpollutionmap.app/?lat=" + str(lat) + "&lng=" + str(lon) + "&zoom=17"

    #TODO: IF YOU DON'T HAVE AN M SERIES MAC, DOWNLOAD A DIFFERENT VERSION,
    #DRAG IT HERE AND CHANGE THE FOLDER NAME IN PATH HERE TO MATCH
    #IF YOU ALSO USE AN ARM-64 MAC, JUST LEAVE THIS AND IT WILL WORK
    cService = webdriver.ChromeService(executable_path="chromedriver-mac-arm64/chromedriver")
   
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

print(get_lpma_data(coords[0],coords[1]))