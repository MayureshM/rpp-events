import boto3
import json
from datetime import datetime
from rpp_lib.manheim_requests import Session
from rpp_lib.rpc import get_consignment
import eb_validation as validations
import dynamo
from environs import Env
from voluptuous import Any
from new_config import load_app_config
from event_bridge import send_to_event_bus

# Utilities
from util import LOGGER, TRACER, annotate_record, base64encode, push_message_to_sqs
from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent, event_source
from aws_lambda_powertools.utilities.parser import envelopes
from codeguru_profiler_agent import with_lambda_profiler
from aws_lambda_powertools import Metrics
from aws_lambda_powertools.metrics import MetricUnit, single_metric
from deepdiff import DeepDiff

sm = boto3.client("secretsmanager")

mashery = json.loads(sm.get_secret_value(SecretId="mashery_ca_aws")["SecretString"])

try:
    session = Session(client_id=mashery["client_id"], password=mashery["client_secret"])
except Exception as ex:
    session = ex

METRICS = Metrics()
app_config = load_app_config()

ENV = Env()
PROFILE_GROUP = name = ENV("AWS_CODEGURU_PROFILER_GROUP_NAME", validate=Any(str))
EVENT_QUEUE_URL = ENV("EVENT_DLQ_URL", validate=Any(str))
UPDATED_EVENT_TYPE = "RETAILRECON.ORDERS.UPDATED"

LABOR_TARGETS = ("approved", "labor_time", "repaired", "skipped", "needs_parts")
LABOR_EVENT_NAME = {
    "INSERT": {"event_name": "RECONINVENTORY.LABORS.CREATED", "image": "NewImage"},
    "MODIFY": {"event_name": "RECONINVENTORY.LABORS.UPDATED", "image": "NewImage"},
    "REMOVE": {"event_name": "RECONINVENTORY.LABORS.DELETED", "image": "OldImage"}
}
PART_LABOR_TARGETS = ("ip_part_status", "order_received_time", "order_sent_time", "part_name", "approved")
PART_LABOR_EVENT_NAME = {
    "INSERT": {"event_name": "RECONINVENTORY.PARTS.CREATED", "image": "NewImage"},
    "MODIFY": {"event_name": "RECONINVENTORY.PARTS.UPDATED", "image": "NewImage"},
    "REMOVE": {"event_name": "RECONINVENTORY.PARTS.DELETED", "image": "OldImage"}
}


@with_lambda_profiler(profiling_group_name=PROFILE_GROUP)
@METRICS.log_metrics(capture_cold_start_metric=True)
@TRACER.capture_lambda_handler
@LOGGER.inject_lambda_context
@event_source(data_class=EventBridgeEvent)
def handler(event: EventBridgeEvent, _):
    """ Process EventBridge events and post them to eventer. """

    TRACER.put_metadata(key="EventBridgeEvent", value=event)
    LOGGER.debug({"event": event})
    try:
        if event.detail_type == "RECONINVENTORY.DATA":
            dynamoDB_stream_record = validations.validate_eb_event(
                event=event.raw_event,
                envelope=envelopes.EventBridgeEnvelope,
            )
            LOGGER.debug({"dynamoDB_stream_record": dynamoDB_stream_record.dict()})
            # handler based on prefix
            prefix = dynamoDB_stream_record.dynamodb.Keys["sk"].split(":")[0]
            if prefix == "labor":
                _labor_event_handler(dynamoDB_stream_record.dict())
            prefix = dynamoDB_stream_record.dynamodb.Keys["sk"].split("#")[0]
            if prefix == "part":
                _part_labor_event_handler(dynamoDB_stream_record.dict())
        else:
            validated_event = validations.validate_event_detail(
                event=event.raw_event,
                envelope=envelopes.EventBridgeEnvelope,
            )
            send_eventer_events(validated_event.__dict__, event.detail_type)
    except Exception as ex:
        LOGGER.exception(ex)
        push_message_to_sqs(EVENT_QUEUE_URL, json.dumps(event.raw_event))


@TRACER.capture_method
def send_eventer_events(event_detail, event_type):
    """send_eventer_events.

    :param event_detail:
    :param event_type:
    """

    if isinstance(session, Exception):
        LOGGER.exception(session)
        raise session

    annotate_record(event_detail)

    event_workorder_path = (
        app_config.get("rpp-events", {}).get("event_href_base_url", "")
        + app_config.get("rpp-events", {}).get("event_href_workorder_path", "")
    )

    site_id = event_detail["site_id"]

    work_order_number = event_detail["work_order_number"]

    href = event_workorder_path + base64encode(event_detail["work_order_key"])
    event_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    prefix, _, work_order_key = event_detail.get("work_order_key").partition(":")
    consignment = get_consignment(work_order_key=work_order_key)
    event_body = {
        "href": href,
        "createdTimestamp": event_datetime,
        "consignment": {
            "href": consignment.get("href"),
            "operatingLocation": {
                "href": f"{session._base_url}/locations/id/{site_id}"
            },
            "referenceId": {"workOrderNumber": work_order_number},
        },
        "manheimAccountNumber": str(event_detail["dealer_number"]),
    }

    TRACER.put_metadata(
        key="event_body",
        value={"event_type": event_type, "resource": href, "body": event_body},
    )

    _send_task_event(
        event_type=event_type,
        resource=href,
        body=event_body,
        work_order_key=event_detail["work_order_key"],
        work_order_number=work_order_number,
        site_id=site_id,
    )
    _send_updated_event(
        resource=href,
        body=event_body,
        work_order_key=event_detail["work_order_key"],
        work_order_number=work_order_number,
        site_id=site_id,
    )


@TRACER.capture_method
def _send_task_event(
    event_type, resource, body, work_order_key, work_order_number, site_id
):
    if isinstance(session, Exception):
        LOGGER.exception(session)
        raise session

    event_object = {
        "eventType": event_type,
        "resource": resource,
        "body": body,
    }

    LOGGER.debug(event_object)

    session.post("/events", json=event_object)
    _add_event_metrics(
        event_type=event_type,
        work_order_key=work_order_key,
        site_id=site_id,
    )


@TRACER.capture_method
def _send_updated_event(resource, body, work_order_key, work_order_number, site_id):
    if isinstance(session, Exception):
        LOGGER.exception(session)
        raise session

    active_tasks, completed_tasks = dynamo.get_active_and_completed_tasks(
        pk=work_order_key
    )
    LOGGER.debug({"workOrderKey": work_order_key, "activeTasksToSend": active_tasks})
    LOGGER.debug(
        {"workOrder_key": work_order_key, "completedTasksToSend": completed_tasks}
    )

    body.update({"activeTasks": active_tasks})
    body.update({"completedTasks": completed_tasks})

    event_object = {
        "eventType": UPDATED_EVENT_TYPE,
        "resource": resource,
        "body": body,
    }

    LOGGER.debug({"eventToSend": event_object})

    session.post("/events", json=event_object)
    _add_event_metrics(
        event_type=UPDATED_EVENT_TYPE,
        work_order_key=work_order_key,
        site_id=site_id,
    )


@TRACER.capture_method
def _labor_event_handler(dynamoDB_stream_record):
    """ Labor event handler. """
    if dynamoDB_stream_record["eventName"] == "MODIFY":
        dynamodb_old_image = dynamoDB_stream_record["dynamodb"]["OldImage"]
        dynamodb_new_image = dynamoDB_stream_record["dynamodb"]["NewImage"]
        new_approved = dynamodb_new_image.get("approved")
        old_approved = dynamodb_old_image.get("approved")
        # the event is only sent when it is approved or disapproved
        if new_approved != "Y" and (old_approved not in ("", "Y") or new_approved != "N"):
            return

        event_workorder_path = (
            app_config.get("rpp-events", {}).get("event_href_base_url", "")
            + app_config.get("rpp-events", {}).get("event_href_workorder_path", "")
        )
        work_order_key = dynamoDB_stream_record["dynamodb"]["Keys"]["pk"].split(":")[1]
        href = event_workorder_path + base64encode(work_order_key)
        dynamodb_event_name = dynamoDB_stream_record["eventName"]
        event_type = LABOR_EVENT_NAME[dynamodb_event_name]["event_name"]
        labor = dynamoDB_stream_record["dynamodb"][LABOR_EVENT_NAME[dynamodb_event_name]["image"]]

        # event to send to EB
        event_object = {
            "href": href,
            "labor": labor,
        }

        updated_fields = get_updated_fields(dynamodb_old_image, dynamodb_new_image)
        if len(updated_fields.keys()) > 0:
            event_object["updated_fields"] = updated_fields
            send_to_event_bus(event_object, event_type)


@TRACER.capture_method
def _part_labor_event_handler(dynamoDB_stream_record):
    """ Part labor event handler. """
    LOGGER.debug({"part_labor": dynamoDB_stream_record})

    if "approved" not in dynamoDB_stream_record["dynamodb"]["NewImage"]:
        return

    event_workorder_path = (
        app_config.get("rpp-events", {}).get("event_href_base_url", "")
        + app_config.get("rpp-events", {}).get("event_href_workorder_path", "")
    )
    work_order_key = dynamoDB_stream_record["dynamodb"]["Keys"]["pk"].split(":")[1]
    href = event_workorder_path + base64encode(work_order_key)
    dynamodb_event_name = dynamoDB_stream_record["eventName"]
    event_type = PART_LABOR_EVENT_NAME[dynamodb_event_name]["event_name"]
    part = dynamoDB_stream_record["dynamodb"][PART_LABOR_EVENT_NAME[dynamodb_event_name]["image"]]

    # event to send to EB
    event_object = {
        "href": href,
        "part": part,
    }

    if dynamoDB_stream_record["eventName"] == "MODIFY":
        differences = DeepDiff(dynamoDB_stream_record["dynamodb"]["OldImage"], dynamoDB_stream_record["dynamodb"]["NewImage"])
        updated_fields = {}
        for updated_field in list(differences.affected_root_keys):
            if updated_field in PART_LABOR_TARGETS:
                new_value = None
                if updated_field in dynamoDB_stream_record["dynamodb"]["NewImage"]:
                    new_value = dynamoDB_stream_record["dynamodb"]["NewImage"][updated_field]
                updated_fields[updated_field] = new_value

        event_object["updated_fields"] = updated_fields

    if len(event_object["updated_fields"].keys()) > 0:
        send_to_event_bus(event_object, event_type)


def get_updated_fields(dynamodb_old_image, dynamodb_new_image):
    differences = DeepDiff(dynamodb_old_image, dynamodb_new_image)
    updated_fields = {}
    differences_list = list(differences.affected_root_keys)

    old_approved = dynamodb_old_image.get("approved")
    new_approved = dynamodb_new_image.get("approved")

    if len(differences_list) > 0:
        for updated_field in differences_list:
            if updated_field in LABOR_TARGETS:
                new_value = None
                if updated_field in dynamodb_new_image:
                    new_value = dynamodb_new_image[updated_field]
                updated_fields[updated_field] = new_value

        if len(updated_fields) > 0:
            updated_fields["approved"] = new_approved
            labor_was_approved = old_approved in (None, "", "N") and new_approved == "Y"
            if labor_was_approved:
                updated_fields["labor_time"] = dynamodb_new_image.get("labor_time")
                updated_fields["needs_parts"] = dynamodb_new_image.get("needs_parts")
            if old_approved == "":
                updated_fields["is_loop_back"] = "Y"

            # when the labor is approved or
            # when parts needed flag is modified and the labor is still approved
            if updated_fields.get("needs_parts") == "Y":
                updated_fields["parts_count"] = dynamo.get_parts_count(
                    dynamodb_new_image.get("pk"),
                    dynamodb_new_image.get("sk")
                )

    return updated_fields


@TRACER.capture_method
def _add_event_metrics(event_type, work_order_key, site_id):
    METRICS.add_dimension(name="EventType", value=event_type)
    METRICS.add_metric(name=site_id, unit=MetricUnit.Count, value=1)
    with single_metric(name=event_type, unit=MetricUnit.Count, value=1) as metric:
        metric.add_dimension(name="EventTarget", value="Eventer")
