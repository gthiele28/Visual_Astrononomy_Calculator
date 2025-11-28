import time
from datetime import datetime

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
            print("Still working on this. No changes to saved data have been made.")
            print("Please just select something else")
            time.sleep(1)
        elif coord_choice == 's':
            print("Using saved data.")
            break
        else:
            print("Invalid Input.  Please try again.")
            time.sleep(1)
    
    #second loop, this time to get date and time intended
    #this is saved to location.txt since it can be saved and
    #used as part of scraping from astrospheric
    print("Next, I'm going to need the date and time you want me to find data for.  Please note that the websites I pull from only have accurate data within 3 days of the current date")
    print("Would you like to use the previously saved date/time, current device date/time, or manually input one?")
    while True:
        print("type 's' for saved, 'c' for current date/time or 'd' for custom date/time")
        time_choice = input("type here: ")
        if time_choice == "s":
            pass
        elif time_choice == "c":
            pass
        elif time_choice == "d":
            pass
        else:
            print("Invalid Input.  Please try again.")
            time.sleep(1)

getInputs()