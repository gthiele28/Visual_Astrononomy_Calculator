print("Thank you for using my calculator!  Answer these questions, then run weatherScraper and Calculator (in that order)")
print("First, would you like to use the saved coordinates, current location or manually input a set of coordinates")
print("type 's' for saved, 'c' for current location or 'l' for custom location")

coord_choice = input("type here: ")
if coord_choice == 'l':
    print("For your custom coordinates, write each as a single floating point number")
    lat = input("Latitude: ")
    long = input("Longitude: ")

    loc = open("location.txt", "w")
    loc.write(lat + "\n")
    loc.write("test\n")
    loc.write(long)
    loc.close()

    print("Choices saved successfully.")
elif coord_choice == 'c':
    print("Still working on this. No changes to saved data have been made.")
elif coord_choice == 's':
    print("Using saved data.")