from NGCScraper import extract_data
import json

#Because NGC is supplemented by the IC Catalogue, which includes over
#5500 elements not previously included in the NGC catalogue, and most
#of my code is easily adapted to scrape this data from the site as well
#(modular design as intended) it made sense to use this, especially
#since the ability to include them would make adjustments for things like
#an astrophotography feature or other more in-depth add-ons more useful

#Shamelessly copy/pasting my other code to scrape
#maybe making a function for this would've been better, but eh
#As long as it works I guess

print("Allowing this script to run will overwrite the data in ic_error nums and raw_IC")
yes = input("Are you sure you want to continue? (y/n): ")

if yes == 'y':
    for i in range(2,5596): #IC starts at 2 on this site for some reason, goes up to 5595
        raw_data = open("Data Collection/raw_IC.json", 'w')
        error_locs = open("Data Collection/ic_error_nums.txt", 'w')
        
        url_x = "https://www.go-astronomy.com/ic.php?ID=" + str(i)

        try:
            collected = extract_data(url_x)
            json.dump(collected, raw_data)
            raw_data.write('\n')
            print("Catalogued up to " + str(i))
        except UnicodeDecodeError:
            error_locs.write(str(i) + '\n') #newline so i can use .readlines() to split back to list later
            print("UnicodeDecodeError at " + str(i))


    raw_data.close()
    error_locs.close()
    print("Done!")
else:
    pass