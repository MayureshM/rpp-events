from urllib.parse import urlparse

from environs import Env
from rpp_lib.custom_resource_decorator import CustomResourceHandler

# from rpp_lib.manheim_requests import Session
from rpp_lib.cip_requests import CIPSession
from aws_lambda_powertools import Tracer
from voluptuous import Any

from validation import validate_subscriber_cfn

from util import LOGGER
import const as c

ENV = Env()
LOG_LEVEL = ENV(
    "LOG_LEVEL", validate=Any("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG")
)
TRACER = Tracer()

handler = CustomResourceHandler()

try:
    CIP_session = CIPSession(c.SUBSCRIBER_SCOPE)
except Exception as ex:
    CIP_session = ex


class ManheimEventerException(Exception):
    pass


@TRACER.capture_lambda_handler
@handler.create
def create_subscriber(event, context):
    if isinstance(CIP_session, Exception):
        LOGGER.exception(CIP_session)
        raise CIP_session

    properties = validate_subscriber_cfn(event["ResourceProperties"])
    subscriber_url = ENV("EVENTER_URL", validate=Any(str))
    physical_resource_id = None

    try:
        eventer_props = properties["Source"]["Eventer"]
    except KeyError as ex:
        LOGGER.exception(ex)
        raise NotImplementedError("Event source type not implemented")

    subscriber_data = {}
    try:
        subscriber_data.update(
            {"headers": eventer_props["Headers"], "inactive": eventer_props["Inactive"]}
        )
    except KeyError:
        pass
    subscriber_data.update(
        {"callback": eventer_props["CallbackUrl"], "emails": eventer_props["Emails"]}
    )
    response = CIP_session.post(subscriber_url, json=subscriber_data)

    try:
        physical_resource_id = response.headers["Location"]
    except KeyError as ex:
        LOGGER.exception(ex)
        LOGGER.error(response.headers)
        raise ManheimEventerException(response.headers)

    data = {
        "SubscriberUrl": physical_resource_id,
        "SubscriberId": physical_resource_id.split("/")[-1],
    }

    LOGGER.info('{ "Subscriber_Created": %s }', str(data))

    return data, physical_resource_id


@TRACER.capture_lambda_handler
@handler.update
def update_subscriber(event, context):
    if isinstance(CIP_session, Exception):
        LOGGER.exception(CIP_session)
        raise CIP_session

    properties = validate_subscriber_cfn(event["ResourceProperties"])
    physical_resource_id = event["PhysicalResourceId"]

    try:
        eventer_props = properties["Source"]["Eventer"]
    except KeyError as ex:
        LOGGER.exception(ex)
        raise NotImplementedError("Event source type not implemented")

    subscriber_data = {}
    try:
        subscriber_data.update(
            {"headers": eventer_props["Headers"], "inactive": eventer_props["Inactive"]}
        )
    except KeyError:
        pass

    subscriber_data.update(
        {"callback": eventer_props["CallbackUrl"], "emails": eventer_props["Emails"]}
    )
    response = CIP_session.post(physical_resource_id, json=subscriber_data)

    try:
        physical_resource_id = response.headers["Location"]
    except KeyError:
        LOGGER.warning(
            {
                "message": "no Location header in update response",
                "headers": response.headers,
                "action": "ignoring, reusing previous physical_resource_id",
            }
        )

    data = {
        "SubscriberUrl": physical_resource_id,
        "SubscriberId": physical_resource_id.split("/")[-1],
    }

    LOGGER.info('{ "Subscriber_Updated": %s }', str(data))
    return data, physical_resource_id


@TRACER.capture_lambda_handler
@handler.delete
def delete_subscriber(event, context):
    if isinstance(CIP_session, Exception):
        LOGGER.exception(CIP_session)
        raise CIP_session

    data = {"SubscriberUrl": event["PhysicalResourceId"], "SubscriberId": ""}

    physical_resource_id = urlparse(event["PhysicalResourceId"])
    if physical_resource_id.scheme is not None:
        params = {"force": "true"}
        CIP_session.delete(physical_resource_id.geturl(), params=params)
        data.update({"SubscriberUrl": physical_resource_id})
        data.update({"SubscriberId": physical_resource_id.geturl().split("/")[-1]})

    LOGGER.info('{ "Subscriber_Deleted": %s }', str(data))
    return data, event["PhysicalResourceId"]
