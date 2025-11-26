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

from urllib.request import urlopen

outputs = open("weather_info.txt", "w")
inputs = open("Inputs/location.txt", "r")

coords = inputs.readlines()
coords[0] = float(coords[0])
coords[1] = float(coords[1])

def get_astrospheric_data(lat, lon):
    pass

def get_lpmi_data(lat, lon):
    pass

def get_lpma_data(lat, lon):
    pass