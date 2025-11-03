from typing import Optional, Union

from aws_lambda_powertools.utilities.parameters import (
    AppConfigProvider,
    GetParameterError,
    TransformParameterError,
)
from voluptuous import ALLOW_EXTRA, All
from voluptuous import Range, Required, Schema

from config.base_config import DEFAULT_CACHE_TTL, BaseConfig
from util import LOGGER


class AppConfig(AppConfigProvider, BaseConfig):
    """
    Required IAM Permissions:
        - appconfig:GetConfiguration
        - appconfig:StartConfigurationSession
        - appconfig:GetLatestConfiguration

    Environment variables:
        - APPCONFIG_APP
        - APPCONFIG_ENV
        - APPCONFIG_CONFIG
    """

    def __init__(self, params={}):
        """
        Instantiates AppConfig with the optional params. Falls back to the Configuration Variable if specific variable
        in the params dictionary not found.

        :param params['application']: str
            Points to the application name in the App Config. Defaults to the environment variable "APPCONFIG_APP"
        :param params['environment']: str
            Points to the environment name in the App Config. Defaults to the environment variable "APPCONFIG_ENV"

        Raises
        ------
        EnvError
            When unable to find the required environment variable

        """

        self.set_attributes_to_default_values()
        self.populate_input_params(params)
        self.validate_input_params()

        super().__init__(self.environment, application=self.application)

    def set_attributes_to_default_values(self):
        """
        Overrode function. Please see BaseConfig's corresponding function for description
        """
        BaseConfig.config_validator = Schema(
            {
                Required("application", default=""): All(str),
                Required("environment", default=""): All(str),
                Required("configuration", default=""): All(str),
                Required("transform", default=None): ["json", "base64", None],
                Required("max_age", default=DEFAULT_CACHE_TTL): All(
                    int, Range(min=DEFAULT_CACHE_TTL)
                ),
                Required("force_fetch", default=False): bool,
            },
            required=True,
            extra=ALLOW_EXTRA,
        )
        BaseConfig.property_to_env_mappings = {
            "application": "APPCONFIG_APP",
            "environment": "APPCONFIG_ENV",
            "configuration": "APPCONFIG_CONFIG",
        }

        validated_properties = BaseConfig.config_validator({"transform": []})
        for (
            instance_attribute,
            instance_attribute_value,
        ) in validated_properties.items():
            if instance_attribute == "transform":
                instance_attribute_value = None
            setattr(self, instance_attribute, instance_attribute_value)

    def get(self, **sdk_options) -> Optional[Union[str, dict, bytes]]:
        """
        Overrode function. Please see BaseConfig's corresponding function for description
        """
        try:
            config = super().get(
                self.configuration,
                max_age=self.max_age,
                transform=self.transform,
                force_fetch=self.force_fetch,
                **sdk_options,
            )
        except GetParameterError:
            error_obj = {
                "message": "Could not find the configurations from AWS App Config.",
                "input_parameters": self.get_instance_attribute_values(),
            }
            LOGGER.exception(error_obj)
            raise GetParameterError(
                error_obj["message"],
                {"input_parameters": error_obj["input_parameters"]},
            )
        except TransformParameterError:
            error_obj = {
                "message": "Could not transform the requested data from AWS App Config.",
                "input_parameters": self.get_instance_attribute_values(),
            }
            LOGGER.exception(error_obj)
            raise TransformParameterError(
                error_obj["message"],
                {"input_parameters": error_obj["input_parameters"]},
            )

        return config
