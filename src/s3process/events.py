# Developer: Kevin Mercy
# Package: s3_process
# Module: events.py

# Description: Connect using env variables of AWS configuration to access boto3
# lambda function and sceduler cli from AWS

# _____________________________________________________________________________________


import boto3
import datetime as datetime
import json


# Function Name: list_lambda_function
# Parameters: None
# Description: Using AWS specified in env, list all lambda functions available to user
# Return: printed list of lambda functions available to user
def list_lambda_function():
    # Boto3 connection to aws lambda client
    client = boto3.client("lambda", region_name="us-east-2")

    # Use the paginator to list the functions
    paginator = client.get_paginator("list_functions")
    response_iterator = paginator.paginate()

    # Begin transcribing the lambda functions in account
    print("Here are the Lambda functions in your account:")
    for page in response_iterator:
        for function in page["Functions"]:
            print(f"  {function['FunctionName']}")


# Function Name: schedule_event
# Parameters: time, timezone, lambda_arn, payload, role_arn
# payload -> {'dim' : 'value', 'id' : 'value', 'token' : 'value', 'duration': 'value'}
# time as datetime object
# timezone as string format from AWS website
# arns for lambda function, and role which has lambda and sceduler trust policies in AWS
# Description: Scedule a one-time event using input parameters, invokes lambda call
# to POST to street-lights API
# Return: response from sceduler client
def schedule_event(time, timezone, lambda_arn, payload, role_arn):
    # Boto3 Sceduler client
    client = boto3.client("scheduler", region_name="us-east-2")

    # Name of the event REQUIRED
    event_name = "LambdaInvokeEvent"

    # Time of scedule using syntax:
    # at(yyyy-mm-ddThh:mm:ss) -> REQUIRED
    time = time.strftime("%Y-%m-%dT%H:%M:%S")
    scedule_time = "at(" + time + ")"

    # Flexible Time Winow REQUIRED
    flexible_time_window = {"Mode": "OFF"}

    # Target payload for "Invoke Lambda" REQUIRED
    target_json = {"Arn": lambda_arn, "Input": json.dumps(payload), "RoleArn": role_arn}

    # State of event after programming - optional
    state = "ENABLED"

    # Action after compeltion of event - optional
    action_complete = "DELETE"

    # Display parameters to user for complete API call to sceduler
    print(
        event_name,
        state,
        action_complete,
        scedule_time,
        timezone,
        flexible_time_window,
        target_json,
    )

    # Trigger scedule creation
    response = client.create_schedule(
        Name=event_name,
        State=state,
        ActionAfterCompletion=action_complete,
        ScheduleExpression=scedule_time,
        ScheduleExpressionTimezone=timezone,
        FlexibleTimeWindow=flexible_time_window,
        Target=target_json,
    )

    # Update user on response
    print("SENT TO SCEDULE SENT TO AWS")
    print(response)

    # Return the response to user
    return response
