import array

import boto3
from boto3.dynamodb.conditions import Key
import requests
import time
from voluptuous import (
    Schema,
    ALLOW_EXTRA,
    Required,
    All,
    Length,
    Optional,
)
dynamodb = boto3.resource("dynamodb")


def submit_job_criteria_to_tdm(tdm_api_url):
    response = requests.get(tdm_api_url)
    response = response.json()
    print("Job Submitted to TDM. TDM Response is: ", response, flush=True)
    if "status" in response and response["status"] == "BUILDING":
        counter = 1
        url = f'{response["data"]}artifact/results.json'
        while True:
            print(
                "Waiting for the Build Job to complete. Results URL is: ",
                url,
                flush=True,
            )
            response = requests.get(url)
            if response.status_code == 404:
                # print(
                #     "It's not found.............. Have to wait for 20 seconds",
                #     flush=True,
                # )
                time.sleep(20)
                counter += 1
                # print("After sleep................: ", counter, counter == 20)
            else:
                print("Build Job completed.", flush=True)
                return response.json()
            if counter == 20:
                # print("Going to break: ", counter, flush=True)
                break

    return []


def pull_data_from_dynamo_db(input_params={}):
    print("input_params...........", input_params)
    # return {}

    validator = Schema(
        {
            Required("table_name"): All(str, Length(min=1)),
            Required("partition_key_index"): All(str, Length(min=1)),
            Required("partition_key"): All(str, Length(min=1)),
            Required("partition_key_value"): All(str, Length(min=1)),
            Optional("sort_key"): All(str),
            Optional("sort_key_value"): All(str),
        },
        required=True,
        extra=ALLOW_EXTRA,
    )

    validated_properties = validator(input_params)
    table = dynamodb.Table(validated_properties["table_name"])

    try:
        key_condition_expression = Key(validated_properties["partition_key"]).eq(
            validated_properties["partition_key_value"]
        )
        if "sort_key" in validated_properties:
            key_condition_expression = Key(validated_properties["partition_key"]).eq(
                validated_properties["partition_key_value"]
            ) & Key(validated_properties["sort_key"]).begins_with(
                validated_properties["sort_key_value"]
            )

        response = table.query(
            KeyConditionExpression=key_condition_expression,
            IndexName=validated_properties["partition_key_index"],
        )
        return response
    except Exception as e:
        print("Exception............", e)
        return "NO_VALUE"


def extract_work_order_number(input):
    print("extract_work_order_number.........: ", input[0]["workOrderNumber"])

    return input[0]["workOrderNumber"]


def extract_work_order_key(input):
    print("extract_work_order_key.........: ", input["Items"][0]["pk"].split(":")[-1])
    return input["Items"][0]["pk"].split(":")[-1]


def look_for_capture_event_in_order_capture_table(work_order_key):
    counter = 1
    input_params = {
        "table_name": "rpp-order-capture",
        "partition_key_index": "work_order_key-index",
        "partition_key": "work_order_key",
        "partition_key_value": work_order_key,
    }
    print("...........input_params......................", input_params)
    while True:
        response = pull_data_from_dynamo_db(input_params)
        # response = pull_order_capture_from_dynamo_db(
        #     "rpp-order-capture", work_order_key
        # )
        if len(response["Items"]):
            break
        elif counter == 20:
            print("Waiting for capture event timed out.")
            return {}
        else:
            counter += 1
        print(
            f"Waiting for the capture event to appear in the table rpp-order-capture for the "
            f"work_order_key: {work_order_key}."
        )
        time.sleep(20)

    return response

def look_for_offering_event_in_order_offering_table(work_order_key):
    counter = 1
    input_params = {
        "table_name": "rpp-order-offering",
        "partition_key_index": "work_order_key-index",
        "partition_key": "work_order_key",
        "partition_key_value": work_order_key,
    }
    print("...........input_params......................", input_params)
    while True:
        response = pull_data_from_dynamo_db(input_params)

        if len(response["Items"]):
            break
        elif counter == 20:
            print("Waiting for offering event timed out.")
            return {}
        else:
            counter += 1
        print(
            f"Waiting for the offering event to appear in the table rpp-order-offering for the "
            f"work_order_key: {work_order_key}."
        )
        time.sleep(20)

    return response


def look_for_event_with_wo_number_in_dynamodb_table(table_name, work_order_number, event_type):
    counter = 1
    input_params = {
        "table_name": table_name,
        "partition_key_index": "index_work_order_number",
        "partition_key": "work_order_number",
        "partition_key_value": work_order_number,
        "sort_key_value": event_type,
    }
    print("...........input_params......................", input_params)
    while True:
        response = pull_data_from_dynamo_db(input_params)

        if len(response["Items"]):
            break
        elif counter == 20:
            print(f"Waiting for {event_type} event timed out.")
            return {}
        else:
            counter += 1
        print(
            f"Waiting for the {event_type} event to appear in the table {table_name} for the "
            f"work_order_key: {work_order_number}."
        )
        time.sleep(20)

    return response


def look_for_event_with_wo_key_in_dynamodb_table(table_name, work_order_key, event_type):
    counter = 1
    input_params = {
        "table_name": table_name,
        "partition_key_index": "work_order_key-index",
        "partition_key": "work_order_key",
        "partition_key_value": work_order_key,
    }
    print("...........input_params......................", input_params)
    while True:
        response = pull_data_from_dynamo_db(input_params)

        if len(response["Items"]):
            break
        elif counter == 20:
            print(f"Waiting for {event_type} event timed out.")
            return {}
        else:
            counter += 1
        print(
            f"Waiting for the {event_type} event to appear in the table {table_name} for the "
            f"work_order_key: {work_order_key}."
        )
        time.sleep(20)

    return response


def validation_capture_response(response):
    print("extract_work_order_key.........: ", response["Items"][0]["pk"].split(":")[-1])
    return input["Items"][0]["pk"].split(":")[-1]


def extract_data_from_response(response, data):
    return response["Items"][0]["order"][data]

def extract_active_task_from_retailrecon_response(response, data1, data2):
    return response["Items"][0]["order"][data1][0][data2]

def extract_complete_task_1_from_retailrecon_response(response, data1, data2):
    return response["Items"][0]["order"][data1][0][data2]
def extract_complete_task_2_from_retailrecon_response(response, data1, data2):
    return response["Items"][0]["order"][data1][1][data2]

def extract_complete_task_from_retailrecon_response(response, data1, data2):
    index = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    validate = []
    for i in index:
        data = response["Items"][0]["order"][data1][i][data2]
        validate.append(data)
    return validate

def extract_data_from_recon_work_order_response(response, data):
    return response["Items"][0][data]

def extract_capture_type_from_recon_work_order_response(response, data):
    return response["Items"][1][data]
def extract_offering_type_from_recon_work_order_response(response, data):
    return response["Items"][1][data]
def extract_capture_status_from_recon_work_order_response(response, data):
    return response["Items"][0][data]

def extract_data_from_recon_vehicle_response(response, data):
    return response["Items"][0][data]
