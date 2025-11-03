"""Custom CloudFormation resource rpp_events subscription"""

import base64
import json

import boto3

# pylint: disable=unused-import
from botocore.exceptions import ClientError
from environs import Env
from requests import HTTPError
from rpp_lib.custom_resource_decorator import CustomResourceHandler
from rpp_lib.manheim_requests import Session
from aws_lambda_powertools import Tracer
from voluptuous import Any

from validation import validate_subscription_cfn

from util import LOGGER

ENV = Env()
LOG_LEVEL = ENV(
    "LOG_LEVEL", validate=Any("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG")
)
TRACER = Tracer()

# pylint: disable=invalid-name
handler = CustomResourceHandler()

# pylint: disable=broad-except
try:
    manheim_session = Session()
except Exception as ex:
    manheim_session = ex

ENV = Env()
TOPIC_ARN = ENV("EVENT_BUS_ARN", validate=Any(str))
STREAM_NAME = ENV("EVENT_FIREHOSE", validate=Any(str))
SUBSCRIPTION_URL = ENV("EVENTER_SUBSCRIPTION_URL", validate=Any(str))
SUBSCRIBER_URL = ENV("EVENTER_SUBSCRIBER_URL", validate=Any(str))
SUBSCRIBER_ID = ENV("EVENTER_SUBSCRIBER_ID", validate=Any(str))


class ManheimEventerException(Exception):
    """exception to be raised when eventer returns error"""

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

    subscriptions = manheim_session.get(subscriber_subs_url).json()
    for subscription in subscriptions["items"]:
        if event_name in subscription["criteria"]:
            return subscription["href"]

    raise ManheimEventerException("Can't find existing subscription")


# pylint: disable=unused-argument
@TRACER.capture_method
def create_eventer_subscription(event_name, expansions):
    data = {
        "subscriber": {"href": SUBSCRIBER_URL},
        "criteria": [{"type": {"pattern": event_name}}],
        "expansions": expansions,
    }

    try:
        response = manheim_session.post(SUBSCRIPTION_URL, json=data)
        subscription_id = response.headers["Location"]

    except HTTPError as httpe:
        if httpe.response.status_code != 409:
            raise httpe

        try:
            data = {"expansions": expansions}
            subscription_id = get_current_subscription(event_name)
            response = manheim_session.post(subscription_id, json=data)
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
        raise ManheimEventerException(response.headers)

    LOGGER.info({"Subscription_Data": data, "Subsciption_id": subscription_id})
    return subscription_id


@TRACER.capture_method
def delete_eventer_subscription(event_name, subscription_url, force=False):
    client = boto3.client("sns")
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
    if event_name not in event_list or force:
        try:
            response = manheim_session.delete(subscription_url)
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
                "Reason": str(event_name) + "has other services are using it",
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
def create_eventer_source(physical_resource_id, event_list, expand_dict):
    for event_name in event_list:
        expansions = expand_dict.get(event_name, [])
        subscription_id = create_eventer_subscription(event_name, expansions)
        physical_resource_id.update({event_name: subscription_id})


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
def update_eventer_source(
    event_list, expand_dict, delete_event_list, physical_resource_id
):
    for event_name in event_list:
        expansions = expand_dict.get(event_name, [])

        subscription_id = create_eventer_subscription(event_name, expansions)
        physical_resource_id.update({event_name: subscription_id})

    for event_name in delete_event_list:
        delete_eventer_subscription(event_name, physical_resource_id[event_name])


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
def delete_eventer_source(event_list, physical_resource_id):
    """delete eventer subscriptions"""
    LOGGER.debug(
        {"event_list": event_list, "physical_resource_id": physical_resource_id}
    )

    for event_name in event_list:
        LOGGER.debug({"event_name": event_name})
        delete_eventer_subscription(event_name, physical_resource_id[event_name])


@TRACER.capture_lambda_handler
@handler.create
def create_subscription(event, context):
    LOGGER.info({"event": event})
    # pylint: disable=raising-non-exception
    if isinstance(manheim_session, Exception):
        LOGGER.exception(manheim_session)
        raise manheim_session

    properties = validate_subscription_cfn(event["ResourceProperties"])

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
        create_eventer_source(physical_resource_id, event_list, expand_dict)
    except KeyError:
        pass

    try:
        event_list = properties["Source"]["Inspection"]["Events"]
        create_targets(
            properties=properties,
            event_list=event_list,
            data=data,
            physical_resource_id=physical_resource_id,
        )
    except KeyError:
        pass

    try:
        event_list = properties["Source"]["PE"]["Events"]
        create_targets(
            properties=properties,
            event_list=event_list,
            data=data,
            physical_resource_id=physical_resource_id,
        )
    except KeyError:
        pass

    try:
        event_list = properties["Source"]["RPP"]["Events"]
        create_targets(
            properties=properties,
            event_list=event_list,
            data=data,
            physical_resource_id=physical_resource_id,
        )
    except KeyError:
        pass

    data.update({"TopicArn": TOPIC_ARN})
    data.update({"StreamName": TOPIC_ARN})

    return (
        data,
        base64.urlsafe_b64encode(json.dumps(physical_resource_id).encode()).decode(),
    )


@TRACER.capture_lambda_handler
@handler.update
def update_subscription(event, context):
    LOGGER.info({"event": event})
    # pylint: disable=raising-non-exception, too-many-locals
    if isinstance(manheim_session, Exception):
        LOGGER.exception(manheim_session)
        raise manheim_session

    data = {}
    physical_resource_id = json.loads(
        base64.urlsafe_b64decode(event["PhysicalResourceId"].encode()).decode()
    )

    properties = validate_subscription_cfn(event["ResourceProperties"])
    old_properties = validate_subscription_cfn(event["OldResourceProperties"])

    try:
        event_list = properties["Source"]["Eventer"]["Events"]
        expand_dict = properties["Source"]["Eventer"]["Expansions"]
        old_event_list = old_properties["Source"]["Eventer"]["Events"]
        delete_event_list = set(old_event_list) - set(event_list)
        update_targets(
            properties=properties,
            event_list=event_list,
            data=data,
            physical_resource_id=physical_resource_id,
        )

        update_eventer_source(
            event_list=event_list,
            expand_dict=expand_dict,
            delete_event_list=delete_event_list,
            physical_resource_id=physical_resource_id,
        )

    except KeyError:
        pass

    try:
        event_list = properties["Source"]["Inspection"]["Events"]
        old_event_list = old_properties["Source"]["Inspection"]["Events"]
        delete_event_list = set(old_event_list) - set(event_list)
        update_targets(
            properties=properties,
            event_list=event_list,
            data=data,
            physical_resource_id=physical_resource_id,
        )

    except KeyError:
        pass

    try:
        event_list = properties["Source"]["PE"]["Events"]
        old_event_list = old_properties["Source"]["PE"]["Events"]
        delete_event_list = set(old_event_list) - set(event_list)
        update_targets(
            properties=properties,
            event_list=event_list,
            data=data,
            physical_resource_id=physical_resource_id,
        )

    except KeyError:
        pass

    try:
        event_list = properties["Source"]["RPP"]["Events"]
        old_event_list = old_properties["Source"]["RPP"]["Events"]
        delete_event_list = set(old_event_list) - set(event_list)
        update_targets(
            properties=properties,
            event_list=event_list,
            data=data,
            physical_resource_id=physical_resource_id,
        )

    except KeyError:
        pass

    data.update({"TopicArn": TOPIC_ARN})
    data.update({"StreamName": TOPIC_ARN})

    return (
        data,
        base64.urlsafe_b64encode(json.dumps(physical_resource_id).encode()).decode(),
    )


@TRACER.capture_lambda_handler
@handler.delete
def delete_subscription(event, context):
    LOGGER.info({"event": event})
    # pylint: disable=raising-non-exception
    if isinstance(manheim_session, Exception):
        LOGGER.exception(manheim_session)
        raise manheim_session

    data = {}
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

        delete_eventer_source(event_list, physical_resource_id)
    except KeyError:
        pass

    try:
        event_list = properties["Source"]["Inspection"]["Events"]
        delete_targets(physical_resource_id)
    except KeyError:
        pass

    try:
        event_list = properties["Source"]["PE"]["Events"]
        delete_targets(physical_resource_id)
    except KeyError:
        pass

    try:
        event_list = properties["Source"]["RPP"]["Events"]
        delete_targets(physical_resource_id)
    except KeyError:
        pass

    return data, json.dumps(physical_resource_id)
