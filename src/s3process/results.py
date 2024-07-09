# Module Name: results.py
# Purpose: Using public S3 link, download .csv data products for results, and for
# times, and correspond pandas df of turn on/off times for each light.
# Developer: Kevin Mercy

#____________________________________________________________________________________

import requests
import pandas as pd

# Function Name: get
# Purpose: Using url to a s3 bucket .csv file, return the message content
# Parameters: S3 url .csv file
# Return: If status_code is 200 then response.text, else False
def get(url):
    # Get response using requests to url
    response = requests.get(url)
    # If 200, proceed to processing
    if response.status_code == 200:
        # Grab the content and return it to user, don't save .csv
        output = response.text
        return output
    # Grab other code and send to user
    else:
        print(response.status_code)
        return False

# Function Name: process
# Purpose: Process a requests message body for csv content and convert to pandas
# datafrmae
# Parameters: csv response content from url
# Return: If array content, pandas df obj, else False
def process(csv):
        try:
            # Split message into lines
            lines = csv.splitlines()
            # Assuming more than two lines exist, process them
            if len(lines) >= 2:
                # Grab header, which should be first line
                header = lines[0]
                # Convert header into array fro pandas
                header_new = header.split(",")
                # Create data array for rest of pandas processing
                data = []
                # Convert data content into arrays using split
                for i in range(1, len(lines)):
                    row_arr = lines[i].split(",")
                    data.append(row_arr)
                # Try converting to pandas df or error out
                if len(header_new) == 3:
                    df = pd.DataFrame(data, columns=header_new)
                    return(df)
                else:
                    print("Error in csv data, not following EvariNum, Dim, SUM header")
                    return False
            else:
                print("No output in csv object")
                return False
        except Exception as e:
            print("Ouput in df processing")
            print(e)
            return False