import simplejson as s_json
from simplejson import JSONDecodeError
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools.utilities.feature_flags import AppConfigStore, FeatureFlags
from environs import Env
from voluptuous import Any

ENV = Env()
APP = ENV("APPCONFIG_APP", validate=Any(str))
ENVIRONMENT = ENV("APPCONFIG_ENV", validate=Any(str))
APP_CONFIG = ENV("APPCONFIG_CONFIG", validate=Any(str))

TRACER = Tracer()
LOGGER = Logger()


config_store = AppConfigStore(
    environment=ENVIRONMENT, application=APP, name=APP_CONFIG, envelope="feature_flags"
)

FEATURE_FLAGS = FeatureFlags(store=config_store)


def load_app_config():
    config = {}
    try:
        config = s_json.loads(
            parameters.AppConfigProvider(application=APP, environment=ENVIRONMENT).get(
                APP_CONFIG
            )
        )

    except JSONDecodeError as json_decode_error:
        message = "We could not decode the message into JSON object that was pulled from AppConfig"
        record = None
        reason = str(json_decode_error)
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

    return config
