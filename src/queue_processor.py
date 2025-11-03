import json
from json import JSONDecodeError

import boto3
from aws_lambda_powertools import Tracer
from aws_lambda_powertools.metrics import MetricUnit
from environs import Env
from voluptuous import Any, MultipleInvalid

from util import generate_error_log, send_message
from validation import (
    validate_eventer_event,
    validate_inspection_repair_event,
    validate_pe_event,
    validate_rpp_event,
)
from util import LOGGER, METRICS, annotate_record
from rpp_lib.cip_requests import CIPSession
from const import CIP_EXPAND_SCOPE, EXISTING_MASHERY_EVENT_TYPES
from dynamo import get_event_data


ENV = Env()
TRACER = Tracer()

SNS = boto3.client("sns")
QUEUE = boto3.client("sqs")
TOPIC_ARN = ENV("EVENT_BUS_ARN", validate=Any(str))
CHARGES_DLQ_URL = ENV("CHARGES_DLQ_URL", validate=Any(str))
METRIC_NAME = ENV("METRIC_NAME", validate=Any(str))
METRIC_COUNT = ENV("METRIC_COUNT", validate=Any(str))
CIP_EXPANSION_URL = ENV("CIP_EXPANSION_URL", validate=Any(str))

# pylint: disable=broad-except
try:
    cip_session = CIPSession(scope=CIP_EXPAND_SCOPE)
except Exception as ex:
    cip_session = ex


@TRACER.capture_method
def remove_message_from_queue(record, exception):
    """SQS doesn't automatically remove message from a queue, so we'll use boto3 to remove them."""
    url = QUEUE.get_queue_url(
        QueueName=record["eventSourceARN"].split(":")[-1],
        QueueOwnerAWSAccountId=record["eventSourceARN"].split(":")[-2],
    )["QueueUrl"]
    QUEUE.delete_message(QueueUrl=url, ReceiptHandle=record["receiptHandle"])
    LOGGER.error(
        {
            "deleted": record["receiptHandle"],
            "QueueUrl": url,
            "record": record["body"],
            "error": exception,
        }
    )


@METRICS.log_metrics
@TRACER.capture_lambda_handler
def eventer_handler(event, context):
    LOGGER.info({"event": event})
    for record in event["Records"]:
        try:
            message = validate_eventer_event(json.loads(record["body"]))
            # Check if event type requires CIP expansion
            if message["eventType"] not in EXISTING_MASHERY_EVENT_TYPES:
                # pylint: disable=raising-non-exception
                if isinstance(cip_session, Exception):
                    LOGGER.exception(cip_session)
                    raise cip_session

                try:
                    # Query DynamoDB for expansions based on event type
                    dynamo_event_data = get_event_data(message['eventType'])
                    expansions = dynamo_event_data.get('expansions', [])

                    LOGGER.info({
                        "message": "Sending expansion request to CIP",
                        "cip_expansion_url": CIP_EXPANSION_URL,
                        "event_type": message["eventType"],
                        "expansions": expansions,
                        "message_body": message['body']
                    })
                    # Prepare request body for CIP
                    if expansions:
                        request_body = {
                            'body': message['body'],
                            'expansions': expansions
                        }

                        response = cip_session.post(
                            url=CIP_EXPANSION_URL,
                            json=request_body
                        )
                        if response.ok:
                            expanded_message = response.json()
                            message['body'] = expanded_message
                        else:
                            LOGGER.error(f"CIP expansion failed with status {response.status_code}")
                        LOGGER.info({
                            "message": "CIP expansion successful",
                            "expanded_message": message,
                            "CIP expansion response": {response},
                            "CIP expansion response status": response.status_code
                        })
                        LOGGER.info(f"CIP expansion response status: {response.status_code}")
                except ConnectionError as conn_error:
                    LOGGER.error(f"Connection error during CIP expansion: {conn_error}")
                    return
                except TimeoutError as timeout_error:
                    LOGGER.error(f"Timeout error during CIP expansion: {timeout_error}")
                    return
                except Exception as e:
                    LOGGER.error(f"Failed to process expansion request: {e}")
                    return

            response = SNS.publish(
                TopicArn=TOPIC_ARN,
                Message=json.dumps(message),
                Subject="Eventer Event " + str(message["eventType"]),
                MessageStructure="string",
                MessageAttributes={
                    "event": {"DataType": "String", "StringValue": message["eventType"]}
                },
            )
            LOGGER.info({"Response": response})
            annotate_record(record)
            METRICS.add_metric(name=METRIC_COUNT, unit=MetricUnit.Count, value=1)
            METRICS.add_dimension(name=METRIC_NAME, value=message["eventType"])

        except JSONDecodeError as json_error:
            remove_message_from_queue(record, json_error)

        except MultipleInvalid as validation_error:
            remove_message_from_queue(record, validation_error)


@METRICS.log_metrics
@TRACER.capture_lambda_handler
def inspection_repair_handler(event, context):
    LOGGER.info({"event": event})
    for record in event["Records"]:
        try:
            message = validate_inspection_repair_event(json.loads(record["body"]))
            response = SNS.publish(
                TopicArn=TOPIC_ARN,
                Message=json.dumps(message),
                Subject="Inspection Repair Event \
                "
                + str(message["eventType"]),
                MessageStructure="string",
                MessageAttributes={
                    "event": {"DataType": "String", "StringValue": message["eventType"]}
                },
            )
            LOGGER.info({"Response": response})
            annotate_record(record)
            METRICS.add_metric(name=METRIC_COUNT, unit=MetricUnit.Count, value=1)
            METRICS.add_dimension(name=METRIC_NAME, value=message["eventType"])

        except JSONDecodeError as json_error:
            remove_message_from_queue(record, json_error)
        except MultipleInvalid as validation_error:
            remove_message_from_queue(record, validation_error)


@METRICS.log_metrics
@TRACER.capture_lambda_handler
def pe_handler(event, context):
    LOGGER.info({"event": event})
    for record in event["Records"]:
        try:
            message = validate_pe_event(json.loads(record["body"]))
            response = SNS.publish(
                TopicArn=TOPIC_ARN,
                Message=json.dumps(message),
                Subject="Prioritization engine Event \
                "
                + str(message["eventType"]),
                MessageStructure="string",
                MessageAttributes={
                    "event": {"DataType": "String", "StringValue": message["eventType"]}
                },
            )
            LOGGER.info({"Response": response})
            annotate_record(record)
            METRICS.add_metric(name=METRIC_COUNT, unit=MetricUnit.Count, value=1)
            METRICS.add_dimension(name=METRIC_NAME, value=message["eventType"])
        except JSONDecodeError as json_error:
            remove_message_from_queue(record, json_error)
        except MultipleInvalid as validation_error:
            remove_message_from_queue(record, validation_error)


@METRICS.log_metrics
@TRACER.capture_lambda_handler
def charges_handler(event, _):
    LOGGER.info({"charges handler event": event})
    for record in event["Records"]:
        try:
            message = json.loads(record["body"])
            if message:
                response = SNS.publish(
                    TopicArn=TOPIC_ARN,
                    Message=json.dumps(message),
                    Subject="charges event",
                    MessageStructure="string",
                    MessageAttributes={
                        "event": {
                            "DataType": "String",
                            "StringValue": "charges",
                        },
                    },
                )
                LOGGER.debug(
                    {"Charges queue processor SNS publish event response": response}
                )
        except JSONDecodeError as json_error:
            LOGGER.error(
                generate_error_log(
                    message="Charges event record failed JSON decode, sending to DLQ",
                    error=json_error,
                    record=message,
                )
            )
            send_message(client=QUEUE, message_body=record, queue_url=CHARGES_DLQ_URL)
        except MultipleInvalid as validation_error:
            LOGGER.error(
                generate_error_log(
                    message="Charges event record failed validation, sending to DLQ",
                    error=validation_error,
                    record=message,
                )
            )
            send_message(client=QUEUE, message_body=record, queue_url=CHARGES_DLQ_URL)
        except Exception as e:
            LOGGER.error(
                generate_error_log(
                    message="Unexpected exception during charges event processing, sending to DLQ",
                    error=e,
                    record=message,
                )
            )
            send_message(client=QUEUE, message_body=record, queue_url=CHARGES_DLQ_URL)


@METRICS.log_metrics
@TRACER.capture_lambda_handler
def rpp_handler(event, context):
    """rpp event queue handler"""
    LOGGER.info({"event": event})
    topic_arn = ENV("EVENT_BUS_ARN", validate=Any(str))
    for record in event["Records"]:
        try:
            message = validate_rpp_event(json.loads(record["body"]))
            response = SNS.publish(
                TopicArn=topic_arn,
                Message=json.dumps(message),
                Subject="Recon Production Platform Event \
                "
                + str(message["event_type"]),
                MessageStructure="string",
                MessageAttributes={
                    "event": {
                        "DataType": "String",
                        "StringValue": message["event_type"],
                    }
                },
            )
            LOGGER.info({"Response": response})
            annotate_record(record)
            METRICS.add_metric(name=METRIC_COUNT, unit=MetricUnit.Count, value=1)
            METRICS.add_dimension(name=METRIC_NAME, value=message["event_type"])

        except JSONDecodeError as json_error:
            remove_message_from_queue(record, json_error)

        except MultipleInvalid as validation_error:
            remove_message_from_queue(record, validation_error)
