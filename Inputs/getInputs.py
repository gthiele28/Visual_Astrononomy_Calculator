import time
import geocoder
from datetime import datetime

def is_date_valid(year, month, day): #important for checking validity of user input
    try:
        datetime.datetime(year, month, day)
        return True
    except ValueError:
        return False

def getInputs():

    print("Thank you for using my calculator!  Follow printed instructions, and you'll be good to go!")
    print("First, would you like to use the saved coordinates, current location or manually input a set of coordinates?")

    #loop to get location 
    while True:
        print("type 's' for saved, 'c' for current location or 'l' for custom location")
        coord_choice = input("type here: ")
        if coord_choice == 'l':
            print("For your custom coordinates, write each as a single floating point number")
            lat = input("Latitude: ")
            long = input("Longitude: ")

            loc = open("Inputs/location.txt", "w")
            loc.write(lat + "\n")
            loc.write(long)
            loc.close()

            print("Choices saved successfully.")
            break
        elif coord_choice == 'c':
            g = geocoder.ip("me")
            if g.latlng != None:
                lat, long = g.latlng
                print("Located device at ~" + str(lat) + ", " + str(long))
                
                loc = open("Inputs/location.txt", "w")
                loc.write(str(lat) + "\n")
                loc.write(str(long))
                loc.close()

                time.sleep(1)
                break

            else:
                print("Unable to locate device.  Please select another option")

        elif coord_choice == 's':
            print("Using saved data.")
            time.sleep(1)
            break
        else:
            print("Invalid Input.  Please try again.")
            time.sleep(1)
    
    #second loop, this time to get date and time intended
    #this is saved to location.txt since it can be saved and
    #used as part of scraping from astrospheric
    print("Next, I'm going to need the date and time you want me to find data for.  Please note that the websites I pull from only have accurate data within 3 days of the current date.")
    print("Would you like to use the previously saved date/time, current device date/time, or manually input one?")
    while True:
        print("type 's' for saved, 'c' for current date/time or 'd' for custom date/time")
        time_choice = input("type here: ")
        if time_choice == "s":
            print("Using saved data.")
            time.sleep(1)
            break
        elif time_choice == "c":
            date = datetime.now()

            print("Saving current local time: " + str(date))

            dt = open("Inputs/date.txt", "w")
            dt.write(str(date.year) + "\n")
            dt.write(str(date.month) + "\n")
            dt.write(str(date.day) + "\n")
            dt.write(str(date.hour) + "\n")
            dt.write(str(date.minute))
            dt.close()

            print("Choices saved successfully.")
            time.sleep(1)
            break
        elif time_choice == "d":

            print("Please input the desired date in MM/DD/YYYY format")
            date = input("type here: ")

            print("Please input the desired time in 24-hour HH:MM format")
            utime = input("type here: ")

            dt = open("Inputs/date.txt", "w")
            
            temp = date.split("/")
            dt.write(temp[2] + "\n")
            dt.write(temp[0] + "\n")
            dt.write(temp[1] + "\n")

            temp = utime.split(":")
            dt.write(temp[0] + "\n")
            dt.write(temp[1])

            dt.close()

            print("Choices saved successfully.")
            time.sleep(1)
            break
        else:
            print("Invalid Input.  Please try again.")
            time.sleep(1)
        
        print("Done!  Now collecting data")

getInputs()