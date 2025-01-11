import json
import requests

def save_data(data, headers, get_devices, get_street_light, outdata_full_list):
    print("SUCESSFULLY FOUND MATCHING LIGHTPOINT IDS")
    print(len(data))

    # Starting Iteration to grab all coordinate and attribute data
    print("RETREIVING COORDINATES AND ATTRIBUTES OF LIGHTPOINTS")

    # Beginning loop iteration of LightPoint ids
    for record in data:
        # Retrieve Dim level Attribute
        get_street_light_id_dim = get_street_light + "/" + record["id"] + "/dimminglevel"
        dim_level = requests.get(get_street_light_id_dim, headers=headers).json()
        if len(dim_level) > 0:
            dim_display = dim_level["value"]
            get_device_id = get_devices + "/" + record["id"]
            query_field_payload = {"field[]" : ["name", "coords", "metering"]}
            id_fields = requests.get(get_device_id, params=query_field_payload, headers=headers).json()
            id_fields["dimmingLevel"] = dim_display
            outdata_full_list.append(id_fields)


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

def post_dimming_level(id, dim, bearer_token, duration):
    api_endpoint = "https://ats-api.smartlinx.tech/api/v2/"
    print(api_endpoint)

    # Street Light POST to DIM Route
    # /api/v2/streetlight/{id}/dimminglevel
    street_light_route = "streetlight"
    post_dim_using_id = api_endpoint + street_light_route + "/" + id + "/dimminglevel"
    print(post_dim_using_id)

    # Initialize Bearer Token Api Access Token Header for all API Requests
    print("INITIALIZATION API TOKEN")
    # Attemping setting Auth Header using User Token Input
    token_header = "Bearer " + bearer_token
    headers = {"Authorization" : token_header}
    print("SUCCESSFULLY SET BEARER TOKEN HEADER")
    print(headers)

    dim_level_payload = {"level": int(dim), "duration": int(duration)}
    print(dim_level_payload)

    print("Sending request", post_dim_using_id)
    response = requests.post(post_dim_using_id, params=dim_level_payload, headers=headers)
    print("Gathered response")

    return response

def run_request_with_params():

    api_endpoint = "https://ats-api.smartlinx.tech/api/v2/"
    print(api_endpoint)

    bearer_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiNjU4MDg3N2M1Y2Q5YWMwMDU4YzYxZGFlIiwidGVuYW50IjoiQVRTX0FQSSIsInRva2VuSWQiOiJlNmVlOWNhYi03YjgzLTQyMWItYWQ3Mi01ZmFiYWYxN2Q2YjYiLCJpYXQiOjE3MDQ5ODIyNjZ9.yxyb_DEz960d5uuQffwxcVoEG6TSMTzfKJT2H_QwUhw"
    print(bearer_token)

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
    print("INITIALIZATION API TOKEN")
    # Attemping setting Auth Header using User Token Input
    token_header = "Bearer " + bearer_token
    headers = {"Authorization" : token_header}
    print("SUCCESSFULLY SET BEARER TOKEN HEADER")

    # Request to devicetypes to ensure LightPoint Device exists for subsequent processing
    print("RETREIVING LIGHTPOINT DEVICE TYPES")
    device_type_light_point = ""
    print(get_device_types)
    device_types = requests.get(get_device_types, headers=headers).json()
    for device in device_types:
        # If LightPoint is found, set LightPointDevice and continue processing
        if device == "LightPoint":

            # Set light point logic and regular variables to proceed processing
            device_type_light_point = device
            print("IDENTIFIED LIGHTPOINT DEVICE")
            print(device_type_light_point)

            # Run Filter on LightPoints to retrieve LightPoint ids if LightPoint objects exist
            print("IDENTIFYING LIGHTPOINT IDS FOR PARAMETER AND COORDINATE EXTRACTION")
            devicetype_filter_payload_list = [device_type_light_point]
            devicetype_filter_payload = {'devicetype': devicetype_filter_payload_list, 'pagesize': 10, 'cursorttl': 90, 'query': 'core.unmanaged is false'}
            #ids_filtered_light_point = requests.get(get_devices, params=devicetype_filter_payload, headers=headers).json()

            parse_paged_api(get_devices, devicetype_filter_payload, headers, get_devices, get_street_light, outdata_full_list)

            # Break Loop to save memory
            break

        else:
            # Run to next iteration if LightPoint is not found
            continue

    print(len(outdata_full_list))
    print(outdata_full_list)
    print("COMPLETED ALL PROGRAMMED API CALLS")
    print("ENDING PROGRAM")
    return outdata_full_list

def lambda_handler(event, context):
    # Retrieve required values
    try:
        dim = event['dim']
        duration = event['duration']
        token = event['token']
        id = event['id']

        response = post_dimming_level(id=id, dim=dim, bearer_token=token, duration=duration)
        if response.status_code == 200:
            return {
                'statusCode': 200,
                'body': "DIM LEVEL HAS BEEN SUCCESSFULLY POSTED"
            }
        else:
            #message = f"{"DIM LEVEL DID NOT COMPLETE SUCCESSFULLY"}"
            return {
                'statusCode': 400,
                'body': "DIM LEVEL DID NOT COMPLETE SUCCESSFULLY"
            }
    except Exception as e:
        message = f"{e}"
        return {
            'statusCode': 400,
            'body': json.dumps(message)
        }