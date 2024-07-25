# Developer: Kevin Mercy
# Package: s3_process
# Module: street_lights.py

# Description: Using https://ats-api.smartlinx.tech/api/v2/, where BEARER_TOKEN must be
# issued by SmartLinx, with token stored in secret file. Provide some functions to
# interact with the API to obtain:
# LightPoints that can be programmed (we should only have one)
# Send POST dimminglevel request to this light


#____________________________________________________________________________________


import requests
import os


# Function Name: retrieve_one_functioning_light
# Parameters: None
# Purpose: Retrieve one functioning light id
# Return: id of one functioning light
def retrieve_one_functioning_light():
    # Run API call and return the one functioning light
    outdata_list = run_request_with_params()
    return outdata_list[0]["id"]

# Function Name: post_dimming_level
# Parameters: id, dim, duration
# Purpose: Using a light id, a supplied dim level and duration: makes a POST request
# to edit the Dim level of the supplied id
# Return: API response object
def post_dimming_level(id, dim, duration):
    # Street light API
    api_endpoint = "https://ats-api.smartlinx.tech/api/v2/"

    # Retrieve token from env
    bearer_token = os.environ["TOKEN"]

    # Street Light POST to DIM Route
    # /api/v2/streetlight/{id}/dimminglevel
    street_light_route = "streetlight"
    post_dim_using_id = api_endpoint + street_light_route + "/" + id + "/dimminglevel"

    # Attemping setting Auth Header using User Token Input
    token_header = "Bearer " + bearer_token
    headers = {"Authorization" : token_header}

    # Construct POST API payload that includes desired dim and duration
    dim_level_payload = {"level": int(dim), "duration": int(duration)}
    print(dim_level_payload)

    # Send post request to API
    response = requests.post(post_dim_using_id, params=dim_level_payload, headers=headers)

    # Return the API response
    return response

# Function Name: save_data
# Parameters: data, headers, get_devices, get_street_light, outdata_full_list
# Purpose: helper request function to retrieve dimming level, and associated information
# from LightPoints /id endpoint
# Gathers data of dimminglevel, id, name, coords, and meterings
# Return: List of data for all returned lights
def save_data(data, headers, get_devices, get_street_light, outdata_full_list):
    # Beginning loop iteration of LightPoint ids
    for record in data:
        # Retrieve Dim level Attribute
        get_street_light_id_dim = get_street_light + "/" + record["id"] + "/dimminglevel"
        dim_level = requests.get(get_street_light_id_dim, headers=headers).json()
        if len(dim_level) > 0:
            # Dim level added to list
            dim_display = dim_level["value"]

            # Request other attribute information
            get_device_id = get_devices + "/" + record["id"]

            # Return id, name, coords, metering
            query_field_payload = {"field[]" : ["name", "coords", "metering"]}
            id_fields = requests.get(get_device_id, params=query_field_payload, headers=headers).json()
            id_fields["dimmingLevel"] = dim_display

            # Write data to out array
            outdata_full_list.append(id_fields)

# Function Name: parse_paged_api
# Parameters: url, params, headers, get_devices, get_street_light, outdata_full_list
# Purpose: Core request function to iterate over pages in the request to get all data
# Calls save_data in order to write data to out array for additional requested fields
# Return: iterates API pages, and save_data writes out_data until there are no pages
def parse_paged_api(url, params, headers, get_devices, get_street_light, outdata_full_list):
    while url:
        response = requests.get(get_devices, params=params, headers=headers)
        data = response.json()
        # Process the data from the current page
        save_data(data, headers, get_devices, get_street_light, outdata_full_list)
        # Check if there is a next page
        if 'Link' in response.headers and 'rel="next"' in response.headers['Link']:
            next_page_url = response.headers['Link'].split(';')[0].strip('<>')
            url = next_page_url
        else:
            url = None

# Function Name: run_request_with_params
# Parameters: None
# Purpose: Run basic street-light run, to return data of commissioned light
# Return: LightPoint data which includes name, id, coords, metering, dimminglevel
def run_request_with_params():
    # API endpoint
    api_endpoint = "https://ats-api.smartlinx.tech/api/v2/"

    # Token initialization
    bearer_token = os.environ["TOKEN"]

    # Street Light Core Routes
    devices_route = "devices"
    device_types_route = "devicetypes"
    street_light_route = "streetlight"

    # Street Light API Route Endpoints
    get_devices = api_endpoint + devices_route
    get_device_types = api_endpoint + device_types_route
    get_street_light = api_endpoint + street_light_route

    # Initializing Variables
    outdata_full_list = []

    # Initialize Bearer Token Api Access Token Header for all API Requests
    token_header = "Bearer " + bearer_token
    headers = {"Authorization" : token_header}

    # Request to devicetypes to ensure LightPoint Device exists for subsequent processing
    device_type_light_point = ""
    device_types = requests.get(get_device_types, headers=headers).json()
    for device in device_types:
        # If LightPoint is found, set LightPointDevice and continue processing
        if device == "LightPoint":

            # Set light point logic and regular variables to proceed processing
            device_type_light_point = device

            # Run Filter on LightPoints to retrieve LightPoint ids if LightPoint objects exist
            devicetype_filter_payload_list = [device_type_light_point]
            devicetype_filter_payload = {'devicetype': devicetype_filter_payload_list, 'pagesize': 10, 'cursorttl': 90, 'query': 'core.unmanaged is false'}
            #ids_filtered_light_point = requests.get(get_devices, params=devicetype_filter_payload, headers=headers).json()

            # Call to helper function to pare API by pages for all data
            parse_paged_api(get_devices, devicetype_filter_payload, headers, get_devices, get_street_light, outdata_full_list)

            # Break Loop to save memory -> Only care about LightPoint object
            break

        else:
            # Run to next iteration if LightPoint is not found
            continue

    # Return the data
    return  outdata_full_list