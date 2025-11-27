from urllib.request import urlopen
import json

demo_url = "https://www.go-astronomy.com/ngc.php?ID=1"

def extract_data(url):
    '''Extract data from a url passed in,
       return dictionary with data and labels
       from the table'''
    
    page = urlopen(url)

    html_raw = page.read()

    html = html_raw.decode("utf-8")

    table_start = html.find("<tbody>")
    table_end = html.find("</tbody>")

    table = html[table_start:table_end]

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

        data[key] = val

        table = table[table.find(row_idf) + len(row_idf):]
    
    return data




#To avoid errors, I tried implementing try/catch which will block
#my code from crashing when I find � characters, and will dump
#a list of all i values into a separate error-location file

#Runtime roughly 1 hour, try/catch triggered 3 times total
#must update those 3 in a separate script and append to end of raw_NGC
if __name__ == "__main__": #prevent ngc scraping from running unless this file is run
    print("Running this will overwrite raw_NGC.json and ngc_error_nums, erasing your data.")
    go = input("Are you sure? (y/n): ")
    if go == 'y':
        raw_data = open("Data Collection/raw_NGC.json", 'w') #different filename than raw_NGC(which has actual results) to prevent me from overwriting it
        error_locs = open("Data Collection/ngc_error_nums.txt", "w")

        for i in range(1,8374): #multiple loops used, ignore these values
            url_x = "https://www.go-astronomy.com/ngc.php?ID=" + str(i)

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