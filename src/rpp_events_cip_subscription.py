"""Custom CloudFormation resource rpp_events cip subscription"""

import base64
import json

import boto3

# pylint: disable=unused-import
from botocore.exceptions import ClientError
from environs import Env
from requests import HTTPError
from rpp_lib.custom_resource_decorator import CustomResourceHandler
from rpp_lib.cip_requests import CIPSession
from aws_lambda_powertools import Tracer
from voluptuous import Any
from validation import validate_subscription_cfn
from util import LOGGER
from const import CIP_PUBLISH_EVENTS_SCOPE
from dynamo import (
    upsert_subscription_details,
    upsert_event_data,
    get_event_data,
    delete_event_data,
)

# get_event_data


ENV = Env()
LOG_LEVEL = ENV(
    "LOG_LEVEL", validate=Any("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG")
)
TRACER = Tracer()

# pylint: disable=invalid-name
handler = CustomResourceHandler()

# pylint: disable=broad-except
try:
    cip_session = CIPSession(scope=CIP_PUBLISH_EVENTS_SCOPE)
except Exception as ex:
    cip_session = ex

ENV = Env()
TOPIC_ARN = ENV("EVENT_BUS_ARN", validate=Any(str))
STREAM_NAME = ENV("EVENT_FIREHOSE", validate=Any(str))
SUBSCRIPTION_URL = ENV("EVENTER_SUBSCRIPTION_URL", validate=Any(str))
SUBSCRIBER_URL = ENV("EVENTER_SUBSCRIBER_URL", validate=Any(str))
SUBSCRIBER_ID = ENV("EVENTER_SUBSCRIBER_ID", validate=Any(str))


class CIPSessionException(Exception):
    """exception to be raised when CIP session returns error"""

    pass


@TRACER.capture_method
def get_current_subscription(event_name):
    """
    Retrieve the current subscription url of a subscriber for
    the given event_name
    """
    subscriber_subs_url = SUBSCRIPTION_URL
    subscriber_subs_url += "/subscriber/"
    subscriber_subs_url += SUBSCRIBER_ID
    subscriber_subs_url += "?limit=500"

    subscriptions = cip_session.get(
        subscriber_subs_url
    ).json()  # TODO: call the proper function
    for subscription in subscriptions["items"]:
        if event_name in subscription["criteria"]:
            return subscription["href"]

    raise CIPSessionException("Can't find existing subscription")


# pylint: disable=unused-argument
@TRACER.capture_method
def create_cip_subscription(event_name, expansions):
    data = {
        "subscriber": {"href": SUBSCRIBER_URL},
        "criteria": [{"type": {"pattern": event_name}}],
    }

    try:
        response = cip_session.post(
            url=SUBSCRIPTION_URL,
            json=data,
        )
        LOGGER.info(
            {
                "message": "Created/Updated new subscription",
                "response": response,
                "data": data,
            }
        )
        subscription_id = response.headers["Location"]

    except HTTPError as httpe:
        if httpe.response.status_code != 409:
            raise httpe

        try:
            data = {"expansions": expansions}
            subscription_id = get_current_subscription(event_name)
            response = cip_session.post(url=subscription_id, json=data)
            LOGGER.info(
                {
                    "message": "subscription already exists,\
                    updated instead",
                }
            )
        except HTTPError as http_error:
            LOGGER.exception(http_error)
            raise http_error

    except KeyError as ex:
        LOGGER.exception(ex)
        LOGGER.error(response.headers)
        raise CIPSessionException(response.headers)

    LOGGER.info({"Subscription_Data": data, "Subsciption_id": subscription_id})
    return subscription_id


@TRACER.capture_method
def delete_dynamodb_subscription(event_name, stack_name) -> dict:
    """
    Delete subscription data from DynamoDB for the given event_name

    Returns:
        int: Number of services remaining after deletion. Returns -1 if no event data
                or details attribute found, 0 if no services remain, or positive number
                indicating count of remaining services.
    """

    # Get the event data from DynamoDB
    event_data = get_event_data(event_name)
    LOGGER.info(
        {"message": "Fetched event data from DynamoDB", "event_data": event_data}
    )

    if "details" not in event_data:
        LOGGER.warning(f"No details found for event_name: {event_name}")
        return event_data
    elif not event_data:
        LOGGER.warning(f"No event data found for event_name: {event_name}")
        return {}

    # Remove the service with the given stack_name
    aggregated_details = {}
    aggregated_expansions = set()
    for service_name, service_data in event_data["details"].items():
        if service_name == stack_name:
            continue
        aggregated_details[service_name] = service_data
        aggregated_expansions.update(service_data.get("expand", []))

    # Maintain the order of the original expansions
    event_data["expansions"] = [
        exp for exp in event_data.get("expansions", []) if exp in aggregated_expansions
    ]
    event_data["details"] = aggregated_details

    # If details is empty, remove the event data from DynamoDB entirely
    if not event_data["details"]:
        LOGGER.info(f"About to call delete_event_data for {event_name}")
        delete_event_data(event_name)
        LOGGER.info(f"Call to delete_event_data finished for {event_name}")
    else:
        # Remove the event_type from event_data (event_type is the primary key)
        if "event_type" in event_data:
            del event_data["event_type"]

        # Update the event data back to DynamoDB
        upsert_event_data(event_name, event_data)
        LOGGER.info(
            {
                "message": f"Updated event data for {event_name} after service deletion",
                "event_data": event_data,
            }
        )

    # Return the number of services remaining
    LOGGER.info({"message": "Returning event data after deletion", "event_data": event_data})
    return event_data


@TRACER.capture_method
def delete_cip_subscription(
    event_name: str, event_data: dict, force=False
):
    client = boto3.client("sns")
    subscription_url = event_data.get("subscription_id", "")
    sns_subscriptions = client.list_subscriptions_by_topic(TopicArn=TOPIC_ARN)
    LOGGER.debug({"sns_subscriptions": sns_subscriptions})
    event_list = []
    for subscription in sns_subscriptions["Subscriptions"]:
        sns = boto3.resource("sns")
        sub = sns.Subscription(subscription["SubscriptionArn"])
        sub.load()
        try:
            event_list.extend(json.loads(sub.attributes["FilterPolicy"])["event"])
            LOGGER.debug(
                {
                    "message": "Another sub for event found, skipping delete",
                    "subscription": subscription,
                    "attributes": sub.attributes,
                }
            )
        except KeyError as key_error:
            LOGGER.warning(
                {
                    "message": "No event FilterPolicy, deleting",
                    "subscription": subscription,
                    "attributes": sub.attributes,
                    "error": str(key_error),
                }
            )
            delete_sns_subscriber(subscription["SubscriptionArn"])

    LOGGER.debug(
        {
            "event_name": event_name,
            "sns_list": sns_subscriptions["Subscriptions"],
            "no_delete_list": event_list,
            "force": force,
            "Subscription": str(subscription_url),
        }
    )

    response = None
    if event_name not in event_list or len(event_data.get("details", {})) == 0 or force:
        try:
            # response = cip_session.delete(subscription_url)  # TODO: call the proper function
            response = cip_session.delete(subscription_url)
        except HTTPError as httpe:
            if httpe.response.status_code != 404:
                LOGGER.exception(httpe)
                raise httpe

            LOGGER.warning(
                {
                    "event": "404 NOT FOUND, on delete",
                    "Subscription": str(subscription_url),
                    "event_name": event_name,
                }
            )

        LOGGER.info({"Subscription": subscription_url, "Deleted": response})
    else:
        LOGGER.warning(
            {
                "Subscription": str(subscription_url) + " NOT Deleted",
                "Reason": str(event_name) + " has other services are using it",
                "no_delete_list": str(event_list),
            }
        )

    return response


@TRACER.capture_method
def create_sns_subscriber(protocol, arn, event_list):
    client = boto3.client("sns")

    if protocol not in ("lambda", "sqs"):
        raise NotImplementedError

    sub = client.subscribe(
        TopicArn=TOPIC_ARN, Protocol=protocol, Endpoint=arn, ReturnSubscriptionArn=True
    )

    client.set_subscription_attributes(
        SubscriptionArn=sub["SubscriptionArn"],
        AttributeName="FilterPolicy",
        AttributeValue='{"event": ["' + '","'.join(event_list) + '"]}',
    )
    return sub


@TRACER.capture_method
def update_sns_subscriber(protocol, arn, event_list, subscription_arn):
    """
    Update SNS subscriber
    - If found overwrite FilterPolicy with event_list
    - If not found create new subscriber
    """

    try:
        sns = boto3.resource("sns")
        sub = sns.Subscription(subscription_arn)
        sub.set_attributes(
            AttributeName="FilterPolicy",
            AttributeValue='{"event": ["' + '","'.join(event_list) + '"]}',
        )
    except sns.meta.client.exceptions.NotFoundException:
        new_sub = create_sns_subscriber(protocol, arn, event_list)
        subscription_arn = new_sub["SubscriptionArn"]

    return subscription_arn


@TRACER.capture_method
def delete_sns_subscriber(subscription_arn):
    """
    Delete sns subscriber
    if found delete subscriber
    """

    sns = boto3.resource("sns")
    try:
        LOGGER.debug("Deleting subscription: %s", subscription_arn)
        sub = sns.Subscription(subscription_arn)
        sub.load()
        sub.delete()
    except KeyError:
        pass
    return subscription_arn


@TRACER.capture_method
def create_targets(properties, event_list, data, physical_resource_id):
    """Create event target subscribers"""
    try:
        queue_arn = properties["Targets"]["SQS"]
        sub = create_sns_subscriber(
            protocol="sqs", arn=queue_arn, event_list=event_list
        )
        physical_resource_id.update({"sqs": sub["SubscriptionArn"]})
        data.update({"SQSSubscriptionArn": sub["SubscriptionArn"]})
        LOGGER.debug(
            {
                "properties": properties,
                "event_list": event_list,
                "data": data,
                "pysical_resource_id": physical_resource_id,
                "create_sqs_target_response": sub,
            }
        )
    except KeyError:
        pass

    try:
        func_arn = properties["Targets"]["Lambda"]
        sub = create_sns_subscriber(
            protocol="lambda", arn=func_arn, event_list=event_list
        )
        physical_resource_id.update({"lambda": sub["SubscriptionArn"]})
        data.update({"LambdaSubscriptionArn": sub["SubscriptionArn"]})
        LOGGER.debug(
            {
                "properties": properties,
                "event_list": event_list,
                "data": data,
                "pysical_resource_id": physical_resource_id,
                "create_lambda_target_response": sub,
            }
        )
    except KeyError:
        pass


@TRACER.capture_method
def create_cip_source(physical_resource_id, event_list, expand_dict, stack_name):
    for event_name in event_list:
        expansions = expand_dict.get(event_name, [])
        subscription_id = create_cip_subscription(event_name, expansions)
        physical_resource_id.update({event_name: subscription_id})

        # Create subscription data
        subscription_data = {
            "expand": expansions,
            "subscription_id": subscription_id,
        }

        # Add target information if available
        if "sqs" in physical_resource_id:
            subscription_data["sqs"] = physical_resource_id["sqs"]
        if "lambda" in physical_resource_id:
            subscription_data["lambda"] = physical_resource_id["lambda"]

        # Use the dedicated subscription details function
        upsert_subscription_details(event_name, stack_name, subscription_data)


@TRACER.capture_method
def update_targets(properties, event_list, data, physical_resource_id):
    """Update event target subscribers"""
    try:
        sub_arn = update_sns_subscriber(
            protocol="sqs",
            arn=properties["Targets"]["SQS"],
            event_list=event_list,
            subscription_arn=physical_resource_id["sqs"],
        )
        physical_resource_id.update({"sqs": sub_arn})
        data.update({"SQSSubscriptionArn": sub_arn})
    except KeyError:
        try:
            subscription_arn = physical_resource_id["sqs"]
            if subscription_arn:
                delete_sns_subscriber(subscription_arn)
        except KeyError:
            pass

    try:
        sub_arn = update_sns_subscriber(
            protocol="lambda",
            arn=properties["Targets"]["Lambda"],
            event_list=event_list,
            subscription_arn=physical_resource_id["lambda"],
        )
        physical_resource_id.update({"lambda": sub_arn})
        data.update({"LambdaSubscriptionArn": sub_arn})
    except KeyError:
        try:
            delete_sns_subscriber(physical_resource_id["lambda"])
        except KeyError:
            pass


# pylint: disable=too-many-arguments
@TRACER.capture_method
def update_cip_source(
    event_list, expand_dict, delete_event_list, physical_resource_id, stack_name
):
    LOGGER.info({"message": "Logging attributes for update_cip_source",
                 "event_list": event_list,
                 "expand_dict": expand_dict,
                 "delete_event_list": delete_event_list,
                 "physical_resource_id": physical_resource_id,
                 "stack_name": stack_name
                 })
    for event_name in event_list:
        expansions = expand_dict.get(event_name, [])

        subscription_id = create_cip_subscription(event_name, expansions)
        physical_resource_id.update({event_name: subscription_id})
        LOGGER.info(f"Physical resource id after update for {event_name}: {physical_resource_id}")

        # Create subscription data
        subscription_data = {
            "expand": expansions,
            "subscription_id": subscription_id,
        }

        # Add target information if available
        if "sqs" in physical_resource_id:
            subscription_data["sqs"] = physical_resource_id["sqs"]
        if "lambda" in physical_resource_id:
            subscription_data["lambda"] = physical_resource_id["lambda"]

        # Use the dedicated subscription details function
        upsert_subscription_details(event_name, stack_name, subscription_data)

    for event_name in delete_event_list:
        LOGGER.debug({"event_name": event_name})
        event_data = delete_dynamodb_subscription(event_name, stack_name)
        LOGGER.info({"Test Message": "Checking values in update_cip_source before delete_cip_subscription",
                     "event_name": event_name,
                     "physical_resource_id": physical_resource_id,
                     "event_data": event_data})
        delete_cip_subscription(
            event_name, event_data
        )

    # TODO: Handle deletion of old subscriptions when delete_event_list is implemented
    # for event_name in delete_event_list:
    #     delete_cip_subscription(event_name, physical_resource_id[event_name])


@TRACER.capture_method
def delete_targets(physical_resource_id):
    """delete target subscriptions"""
    try:
        delete_sns_subscriber(physical_resource_id["sqs"])
    except KeyError:
        pass

    try:
        delete_sns_subscriber(physical_resource_id["lambda"])
    except KeyError:
        pass


@TRACER.capture_method
def delete_cip_source(event_list, physical_resource_id, stack_name):
    """delete cip subscriptions"""
    LOGGER.debug(
        {"event_list": event_list, "physical_resource_id": physical_resource_id}
    )

    for event_name in event_list:
        LOGGER.debug({"event_name": event_name})
        event_data = delete_dynamodb_subscription(event_name, stack_name)
        LOGGER.info({"Test Message": "Checking values in delete_cip_source before delete_cip_subscription",
                     "event_name": event_name,
                     "physical_resource_id": physical_resource_id,
                     "event_data": event_data})
        delete_cip_subscription(
            event_name, event_data
        )


@TRACER.capture_lambda_handler
@handler.create
def create_subscription(event, context):
    LOGGER.info({"event": event})
    # pylint: disable=raising-non-exception
    if isinstance(cip_session, Exception):
        LOGGER.exception(cip_session)
        raise cip_session

    properties = validate_subscription_cfn(event["ResourceProperties"])

    # Extract stack name from CloudFormation event
    stack_id = event["StackId"]
    stack_name = stack_id.split(":")[-1].split("/")[1]

    physical_resource_id = {}
    data = {}
    try:
        event_list = properties["Source"]["Eventer"]["Events"]
        expand_dict = properties["Source"]["Eventer"]["Expansions"]

        create_targets(
            properties=properties,
            event_list=event_list,
            data=data,
            physical_resource_id=physical_resource_id,
        )

        create_cip_source(physical_resource_id, event_list, expand_dict, stack_name)
    except KeyError:
        pass

    data.update({"TopicArn": TOPIC_ARN})
    data.update({"StreamName": TOPIC_ARN})

    LOGGER.info(
        {
            "data": data,
            "physical_resource_id": physical_resource_id,
            "event_list": event_list,
            "expand_dict": expand_dict,
        }
    )

    return (
        data,
        base64.urlsafe_b64encode(json.dumps(physical_resource_id).encode()).decode(),
    )


@TRACER.capture_lambda_handler
@handler.update
def update_subscription(event, context):
    LOGGER.info({"event": event})
    # pylint: disable=raising-non-exception, too-many-locals
    if isinstance(cip_session, Exception):
        LOGGER.exception(cip_session)
        raise cip_session

    data = {}
    old_physical_id = event["PhysicalResourceId"]
    # Decode the old physical ID but maintain its original form for return
    physical_resource_id = json.loads(
        base64.urlsafe_b64decode(old_physical_id.encode()).decode()
    )

    properties = validate_subscription_cfn(event["ResourceProperties"])
    old_properties = validate_subscription_cfn(event["OldResourceProperties"])

    # Extract stack name from CloudFormation event
    stack_id = event["StackId"]
    stack_name = stack_id.split(":")[-1].split("/")[1]

    try:
        event_list = properties["Source"]["Eventer"]["Events"]
        expand_dict = properties["Source"]["Eventer"]["Expansions"]
        old_event_list = old_properties["Source"]["Eventer"]["Events"]

        # Get list of events being removed
        delete_event_list = set(old_event_list) - set(event_list)

        # First handle updates to targets
        update_targets(
            properties=properties,
            event_list=event_list,
            data=data,
            physical_resource_id=physical_resource_id,
        )

        # Handle CIP source updates
        update_cip_source(
            event_list=event_list,
            expand_dict=expand_dict,
            delete_event_list=delete_event_list,
            physical_resource_id=physical_resource_id,
            stack_name=stack_name,
        )

        # Use the original physical ID to prevent replacement
        data["PhysicalResourceId"] = old_physical_id

    except KeyError as e:
        LOGGER.warning({
            "message": "KeyError during update",
            "error": str(e),
            "stack_name": stack_name
        })

    data.update({"TopicArn": TOPIC_ARN})
    data.update({"StreamName": TOPIC_ARN})

    # Return the same physical ID that was passed in to prevent replacement
    return data, old_physical_id


@TRACER.capture_lambda_handler
@handler.delete
def delete_subscription(event, context):
    LOGGER.info({"event": event})
    # pylint: disable=raising-non-exception
    if isinstance(cip_session, Exception):
        LOGGER.exception(cip_session)
        raise cip_session

    data = {}
    stack_id = event["StackId"]
    stack_name = stack_id.split(":")[-1].split("/")[1]
    properties = validate_subscription_cfn(event["ResourceProperties"])
    physical_resource_id = json.loads(
        base64.urlsafe_b64decode(event["PhysicalResourceId"].encode()).decode()
    )

    try:
        event_list = properties["Source"]["Eventer"]["Events"]
        try:
            delete_targets(physical_resource_id)
        except ClientError as c_err:
            LOGGER.warning(
                {
                    "message": "no aws target found to delete, skipping",
                    "exception": str(c_err),
                    "properties": properties,
                    "event_list": event_list,
                }
            )

        delete_cip_source(event_list, physical_resource_id, stack_name)
    except KeyError:
        pass

    return data, json.dumps(physical_resource_id)
