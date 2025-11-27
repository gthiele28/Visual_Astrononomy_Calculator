#Since 4 total objects caused an error in the scraper, I manually
#Added their tables to a .txt file, with each table copied to a separate
#row.  I will then "borrow" some of my code and take their data, adding it
#to a third file ("raw_extras.json")

#I added some code to replace "�" with the intended apostrophe and
#\u00b0 with &deg; to match the remainder of the objects in my database
#more closely

import json
input = open("Data Collection/error_tables.txt", "r")
file = open("Data Collection/raw_extras.json", "w")

#This will run borderline instantly without internet since text is local,
#So no point having a safety confirmation

for table in input.readlines():
    data = {}

    row_ids = "<tr>"
    row_idf = "</tr>"

    label_ids = "<strong>"
    label_idf = "</strong>"

    label_ds = "</td><td>"
    label_df = "</td></tr>"

    while table.find(row_ids) != -1:

        curr = table[table.find(row_ids):table.find(row_idf) + len(row_idf)]

        key = curr[curr.find(label_ids) + len(label_ids): curr.find(label_idf) - 1]
        val = curr[curr.find(label_ds) + len(label_ds): curr.find(label_df)]

        if key == "Common name":
            print("found")
            val = val.replace("�", "'")
        elif key == "Angle (major axis)":
            print("found 2")
            val = val.replace("°", "&deg;")

        data[key] = val

        table = table[table.find(row_idf) + len(row_idf):]
    
    json.dump(data, file)
    file.write('\n')

file.close()
input.close()
print("Done!")