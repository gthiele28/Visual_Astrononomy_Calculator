from Inputs import getInputs
from Weather import WeatherScraper
import Outputs.Calculator as Calculator

#change these to whatever file paths you want to sort through
datapaths = ["Data Collection/Complete Datasets/raw_NGC.json", "Data Collection/Complete Datasets/raw_IC.json", "Data Collection/Complete Datasets/raw_extras.json"]

#TODO: IF YOU DON'T HAVE AN M SEIES MAC AND CHROME VERSION 142:
#DOWNLOAD A DIFFERENT VERSION OF CHROMEDRIVER, DRAG IT HERE 
#AND CHANGE THE FOLDER NAME IN PATH HERE TO MATCH. IF YOU ALSO USE 
#AN ARM-64 MAC AND CHROME 142, JUST LEAVE THIS AND IT WILL WORK
path = "chromedriver-mac-arm64/chromedriver"

#TODO: LIST OF COMMANDS TO RUN TO INSTALL REQUIRED LIBRARIES
#pip install json
#pip install urllib
#pip install time
#pip install geocoder
#pip install datetime
#pip install numpy
#pip install ast
#pip install astropy
#pip install timezonefinder
#pip install zoneinfo
#pip install selenium

getInputs.getInputs()
WeatherScraper.full_weather_scrape(path)
Calculator.full_calc("Weather/weather_info.txt", "Inputs/date.txt", "Inputs/location.txt", "Inputs/telescope.txt", datapaths)