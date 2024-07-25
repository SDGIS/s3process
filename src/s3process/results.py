# Developer: Kevin Mercy
# Package: s3_process
# Module: results.py

# Description: Using public S3 link for csvs files, download and process two formats.
# results.csv -> Process a results.csv to retrieve pandas df of all light EvariNum and
# selected DIM level from other processing
# dates.csv -> Process a dates.csv to receive the correct turn on/off time for all
# EvariNums and dates within file


#____________________________________________________________________________________


import requests
import pandas as pd
from datetime import datetime
import pytz

# Function Name: get
# Parameters: S3 url .csv file
# Purpose: Using url to a s3 bucket, download the .csv file, and
# return the message content
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

# Function Name: process_results
# Parameters: csv response content from url
# Purpose: Process a requests message body for csv results content and convert to pandas
# datafrmae
# Return: If array content, pandas df obj, else False
def process_results(csv):
    try:
        # Split message into lines
        lines = csv.splitlines()
        # Assuming more than two lines exist, process them
        if len(lines) >= 2:
            # Grab header, which should be first line
            header = lines[0]
            # Convert header into array for pandas
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

# Function Name: process_datetime
# Parameters: List of turn on and turn off times in timezone los angeles
# Purpose: Convert data in table to PST
# Return: Start and end time
def process_datetime(data):
    # Variable declaration
    date_aware_data = []

    # Add in EvariNum
    date_aware_data.append(data[0])

    # Set timezone for date
    pst_timezone = pytz.timezone('America/Los_Angeles')

    # Retrieve dawn time, and make it Pacific
    datetime_obj_dawn = datetime.strptime(data[3] + ' ' + data[4], '%Y-%m-%d %H:%M')
    datetime_obj_dawn = pst_timezone.localize(datetime_obj_dawn)
    date_aware_data.append(datetime_obj_dawn)

    # Retrieve dusk time, and make it Pacific
    datetime_obj_dusk = datetime.strptime(data[3] + ' ' + data[5], '%Y-%m-%d %H:%M')
    datetime_obj_dusk = pst_timezone.localize(datetime_obj_dusk)
    date_aware_data.append(datetime_obj_dusk)

    # Return the time aware datetimes
    return date_aware_data

# Function Name: process_hours
# Parameters: csv response content from url
# Purpose: Process a requests message body for csv hours content and convert to pandas
# dataframe
# Return: If array content, pandas df obj, else False
def process_hours(csv):
    try:
        # Split message into lines
        lines = csv.splitlines()
        # Assuming more than two lines exist, process them
        if len(lines) >= 2:
            # Grab header, which should be first line
            header = ["EvariNum", "DawnDatetime", "DuskDatetime"]
            # Create data array for rest of pandas processing
            data = []
            # Convert data content into arrays using split
            for i in range(1, len(lines)):
                row_arr = lines[i].split(",")
                #print(row_arr)
                date_aware_row = process_datetime(row_arr)
                data.append(date_aware_row)
            # Try converting to pandas df or error out
            df = pd.DataFrame(data, columns=header)
            return(df)
        else:
            print("No output in csv object")
            return False
    except Exception as e:
        print("Ouput in df processing")
        print(e)
        return False