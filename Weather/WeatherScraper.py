#WE NEED (GUESSING)
#Temperature
#Humidity
#Dew point (?)
#Air quality (?)
#Light Pollution (Bortle Class Ideal) (use lightpollutionmap.app)
#Moonrise/Moonset (?)
#Moon % illuminated (?)
#Altitude (?) lightpollutionmap.info
#SQM lightpollutionmap.info

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
    (float 0-100), moonrise(string, time), moonset(string, time)]'''
    
    url = "https://lightpollutionmap.app/?lat=" + str(lat) + "&lng=" + str(lon) + "&zoom=17"

    #TODO: IF YOU DON'T HAVE AN M SERIES MAC, DOWNLOAD A DIFFERENT VERSION
    #IF YOU ALSO USE AN ARM-64 MAC, JUST LEAVE THSI AND IT WILL WORK
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
    start = html_content.find("sqm-value")
    html_content = html_content[start:start + 300]

    cut_s = '''="">'''
    cut_f = "</div>"
    start = html_content.find(cut_s)
    end = html_content.find(cut_f)

    sqm = html_content[start + len(cut_s):end]
    
    driver.close()
    return [float(bortle), float(sqm)]

print(get_lpma_data(coords[0],coords[1]))