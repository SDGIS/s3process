# Developer: Kevin Mercy
# Package: s3_process
# Module: ubiquita.py

# Description: Using ubiquita, setup crentials in the background and make-up GET
# request for ALL light values, and POST Request to set a light value

# ____________________________________________________________________________________


import requests
import time
import os
import json
import csv

# Helper Function: write_json
# Writes response_body to json data
def write_json(in_f, json_data):
    print("Retrieved %s records", len(json_data["data"]))
    with open(in_f, "w") as f:
        json.dump(json_data, f)

# Helper Function: read_json
# Writes response_body to json data
def read_json(in_f):
    data = {}
    with open(in_f, "r") as f:
        data = json.load(f)
        return data

def write_csv(in_json, out_csv):
    # Load JSON data
    data = {}
    with open(in_json, "r") as f:
        data = json.load(f)

    # Writing to CSV
    with open(out_csv, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["id", "dim"])
        writer.writeheader()  # Write the header
        for record in data["data"]:
            writer.writerow(record)  # Write each record

# Helper Function: get_organized_id_and_dim
# From dict, returns organized id,dim dict
def get_organized_id_and_dim(in_data):
    print(len(in_data["data"]))
    outdata = {}
    outdata["data"] = []
    for record in in_data["data"]:
        distilled_data = {}
        distilled_data["id"] = record["id"]
        distilled_data["dim"] = record["powerFactorState"]
        outdata["data"].append(distilled_data)
    return outdata

# Step 1: Requesting a Bearer Token
def get_bearer_token(client_id, client_secret, token_api):
    # Set up the payload with client credentials
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }

    # Send a POST request to the token endpoint
    response = requests.post(token_api, data=payload)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse and return the access token
        token_info = response.json()
        return token_info['access_token']
    else:
        raise Exception("Error fetching token: " + response.text)

# Step 2: Use the Bearer Token to make an authorized request
def make_authorized_request(bearer_token, url, params):
    headers = {
        'Authorization': f'Bearer {bearer_token}'
    }

    # Make a GET request to a protected resource
    response = requests.get(url, headers=headers, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Error making API request: " + response.text)

# Function: query the nodelist url for all IDs/DIMs
# First Registered API Request
def make_nodeslist_request(url, client_id, client_secret, token_url):
    # Get the Bearer Token
    bearer_token = get_bearer_token(client_id, client_secret, token_url)

    # Make an authorized API request
    get_nodes_endpoint = url + "getnodeslist"
    print(get_nodes_endpoint)

    params = {
        #"node_status" : 1,
        #"rssi": "excellent",
        "page": 1,
        "per_page": 1
    }

    api_response = make_authorized_request(bearer_token, get_nodes_endpoint, params)

    print(len(api_response))

    return api_response

def make_node_request_by_id(url, client_id, client_secret, token_url, id):
    # Get the Bearer Token
    bearer_token = get_bearer_token(client_id, client_secret, token_url)

    # Make an authorized API request
    get_nodes_id_endpoint = url + "nodes/" + id
    print(get_nodes_id_endpoint)

    params = {
        #"node_status" : 1,
        #"rssi": "excellent",
        #"page": 1,
        #"per_page": 1
        "type" : "light"
    }

    api_response = make_authorized_request(bearer_token, get_nodes_id_endpoint, params)

    return api_response

def make_post_dim_request_to_light_by_id(url, client_id, client_secret, token_url, id, dim_value):
    # Get the Bearer Token
    bearer_token = get_bearer_token(client_id, client_secret, token_url)

    # Make an authorized API request
    post_dim_endpoint = url + "nodes/setLightDim/"
    print(post_dim_endpoint)

    params = {
        "id_list": [
            {
            "id": id
            }
        ],
        "value": dim_value,
        "node_level_type_id": 1,
        "dim_type": "LD1State"
    }


    api_response = make_authorized_request(bearer_token, post_dim_endpoint, params)
    return api_response