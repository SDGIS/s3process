# s3process Package
This package contains three modules: results, events, street-lights. These modules contain
custom functions to interact with specific data from S3 and utilize the AWS boto3 lambda and
scheduler clients.

### results
1. Process results.csv into pandas df (results.csv contains EvariNum, DIM, SUM header)
```
from s3process.results import get, process_results
url = "s3-url/results.csv"
out = get(url)
df = process_results(out)
```
2. Process dates.csv into pandas df (dates.csv contains EvariNum, Dawn, Dusk header)
```
url = "s3-url/output.csv"
out = get(url)
df = process_hours(out)
```

### street_lights
1. POST desired dim level and duration to a LightPoint in integrated StreetLights API.
This requires a custom bearer token specified in env settings from StreetLights API to
function.
```
response = post_dimming_level(light_id, dim, duration)
```
2. GET street lights id to RUN POST. Same requirments as POST request.
```
light_id = retrieve_one_functioning_light()
```

### events
1. Connect to AWS boto3 lambda client and list all lambda functions available to user.
Requires AWS credentials specified in env.
```
list_lambda_function()
```
2. Scedule an event to invoke lambda function -> Requires AWS credentials, lambda arn,
and role_arn. Must setup lambda payload with lambda input json requirments.
```
response = schedule_event(
    time=time,
    timezone="UTC",
    lambda_arn=lambda_arn,
    payload=lambda_payload,
    role_arn=role_arn,
)
print(response)
```

#### Notes
- Packaged on Docker Image: amd64/amazonlinux:latest using python3 and pyproject.toml
- Required .env with AWS credentials, lambda arn, role arn, and token for StreetLights