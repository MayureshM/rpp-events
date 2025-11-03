from util import LOGGER


# pylint: disable=unused-argument
def handler(event, context):
    LOGGER.info({"event": event})
