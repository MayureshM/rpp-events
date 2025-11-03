import base64
import json
from typing import Union

import boto3
import simplejson as s_json
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools.utilities.parameters import (
    GetParameterError,
    TransformParameterError,
)
from environs import Env
from voluptuous import Any, MultipleInvalid

from validation import validate_config_event

ENV = Env()
LOGGER = Logger()
TRACER = Tracer()
METRICS = Metrics(
    namespace=ENV("POWERTOOLS_METRICS_NAMESPACE", validate=Any(str)),
    service=ENV("POWERTOOLS_SERVICE_NAME", validate=Any(str)),
)
try:
    sqs_client = boto3.client("sqs")
except Exception as ex:
    LOGGER.exception("Unable to initialize sqs client.")
    sqs_client = ex

ANNOTATION_LIST = [
    "auction_id",
    "site_id",
    "work_order_number",
    "work_order_key",
    "vin",
    "sblu",
    "skey",
    "seller_number",
]


@TRACER.capture_method
def generate_error_log(message: str, error: Exception, record: dict) -> dict:
    """Reusable util function for logging errors to CloudWatch logs, et al."""
    return {
        "message": message,
        "error": error,
        "record": record,
    }


@TRACER.capture_method
def send_message(client: boto3.client, message_body: dict, queue_url: str):
    """Use boto3 to send messages to SQS queues"""
    LOGGER.debug(
        {"event": "sqs.publish.start", "queue_name": queue_url, "message": message_body}
    )
    try:
        response = client.send_message(
            QueueUrl=queue_url, MessageBody=json.dumps(message_body)
        )
    except TypeError:
        response = client.send_message(
            QueueUrl=queue_url, MessageBody=s_json.dumps(message_body)
        )
    LOGGER.debug({"event": "sqs.publish.end", "message": response})


def get_config(
    application_name=None,
    environment_name=None,
    configuration_name=None,
    transform=None,
) -> Union[str, list, dict, bytes]:
    # The following parameters, if not provided, will fall back to "Environment variables"
    # The parameter "application_name" will fall back to the environment variable "APPCONFIG_APP"
    # The parameter "environment_name" will fall back to the environment variable "APPCONFIG_ENV"
    # The parameter "configuration_name" will fall back to the environment variable "APPCONFIG_CONFIG"
    #
    # The parameter transform is used to return the encoded (i.e. json/bse64) configuration data
    # By default, it doesn't encode and return as it's stored at the source.
    # At the source, it could be stored in one of the following formats:
    # [str, list, dict, bytes]

    config = {}
    env = Env()

    application_name = (
        application_name if application_name is not None else env("APPCONFIG_APP")
    )
    environment_name = (
        environment_name if environment_name is not None else env("APPCONFIG_ENV")
    )
    configuration_name = (
        configuration_name
        if configuration_name is not None
        else env("APPCONFIG_CONFIG")
    )
    try:
        properties = {
            "application_name": application_name,
            "environment_name": environment_name,
            "configuration_name": configuration_name,
            "transform": [transform],
        }
        validate_config_event(properties)
    except MultipleInvalid as e:
        LOGGER.warning(e)
        return config

    try:
        config = parameters.get_app_config(
            configuration_name,
            environment=environment_name,
            application=application_name,
            transform=transform,
        )
    except GetParameterError:
        message_to_log = "Could not find the configuration from AppConfig"
        input_parameters = {
            "configuration_name": configuration_name,
            "environment_name": environment_name,
            "application_name": application_name,
            "transform": transform,
        }
        message_to_log = {
            "message": message_to_log,
            "input_parameters": input_parameters,
        }
        LOGGER.debug(message_to_log)
    except TransformParameterError:
        message_to_log = "Could not transform the configuration from AppConfig"
        input_parameters = {
            "configuration_name": configuration_name,
            "environment_name": environment_name,
            "application_name": application_name,
            "transform": transform,
        }
        message_to_log = {
            "message": message_to_log,
            "input_parameters": input_parameters,
        }
        LOGGER.debug(message_to_log)

    return config


@TRACER.capture_method
def annotate_record(record) -> None:
    for annotation in ANNOTATION_LIST:
        if annotation in record.keys():
            TRACER.put_annotation(annotation, record[annotation])

    return None


@TRACER.capture_method
def base64encode(data):
    return base64.b64encode(str(data).encode(encoding="UTF-8")).decode("utf-8")


@TRACER.capture_method
def push_message_to_sqs(queue_url: str, message: str, **kwargs):
    """
    Push message to a given SQS queue
    """

    try:
        response = sqs_client.send_message(
            QueueUrl=queue_url, MessageBody=message, **kwargs
        )
        LOGGER.info({"event": "sqs.send_message", "response": response})
    except (
        sqs_client.exceptions.InvalidMessageContents,
        sqs_client.exceptions.UnsupportedOperation,
    ) as exc:
        message = f"We could not push the message into SQS Queue {queue_url}"
        record = message
        reason = str(exc)
        exception = exec
        response = "N/A"
        LOGGER.exception(
            {
                "event": message,
                "record": record,
                "reason": reason,
                "exception": exception,
                "response": response,
            }
        )
        response = False

    return response
