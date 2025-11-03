import boto3
import json
from rpp_lib.logs import LOGGER
from environs import Env
from voluptuous import Any

ENV = Env()
EVENT_BRIDGE = boto3.client("events")
EVENT_BUS = name = ENV("EVENT_BUS", validate=Any(str))


def send_to_event_bus(event, event_type):
    """ Send event to EventBridge Event Bus. """

    LOGGER.debug({"event_type": event_type, "event_object": event})
    EVENT_BRIDGE.put_events(
        Entries=[
            {
                "Source": "rpp-events",
                "Resources": [],
                "DetailType": event_type,
                "Detail": json.dumps(event),
                "EventBusName": EVENT_BUS,
            }
        ]
    )
