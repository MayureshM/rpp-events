import json
from typing import Dict, Optional, Union

from aws_lambda_powertools.utilities.parameters.base import DEFAULT_MAX_AGE_SECS
from environs import Env, EnvError
from voluptuous import ALLOW_EXTRA
from voluptuous import MultipleInvalid, Schema

from util import LOGGER

DEFAULT_CACHE_TTL = DEFAULT_MAX_AGE_SECS


class BaseConfig:
    config_validator = Schema(
        {},
        required=True,
        extra=ALLOW_EXTRA,
    )
    property_to_env_mappings = {}

    def populate_input_params(self, params={}) -> None:
        """
        Overrode function.

        Takes what's coming in the params dict. Sets it to the instance variables
        If not provided in the params, defaults to environment variables if applicable

        Variable in params has the highest precedence.
        If variable in params not present, then see if the class member variable is already set to non-default value?
        If yes, we are good.
        If class member variable is not set to non-default value, then try to lookup env variable if applicable

        Applicable params for DynamoDB:
            :param params['table_name']: str
                Points to the table name in the DynamoDB.
                Defaults to the environment variable "DYNAMO_DB_TABLE_NAME" if not provided.
                Should be provided as part of the object instantiation
            :param params['key_attr']: str
                Points to the key attribute of the table.
                Defaults to the environment variable "DYNAMO_DB_KEY_ATTR" if not provided
                Should be provided as part of the object instantiation
            :param params['sort_attr']: str
                Points to the sort attribute of the table.
                Defaults to the environment variable "DYNAMO_DB_SORT_ATTR" if not provided
                Should be provided as part of the object instantiation
            :param params['value_attr']: str, optional
                Points to the value attribute of the table.
                Defaults to the environment variable "DYNAMO_DB_VALUE_ATTR" if not provided
                Should be provided as part of the object instantiation

            :param params['key_attr_val']: str
                Points to the value of the key_attr of the table
            :param params['max_age']: int
                Sets the time in seconds after which Cache is invalidated
            :param params['transform']: str, optional
                Transforms the content from a JSON object ('json') or base64 binary string ('binary').
                By Default, it pulls as is without any transformation
            :param params['force_fetch']: bool
                If true, the cache will be bypassed and the configuration value will be directly fetched from
                ÅWS Parameter Store service. Use it with caution as this might bring latency

        Applicable params for ParameterStore:
            :param params['ssm_path']: str
                Points to the SSM Path where the configuration is stored.
                Defaults to the environment variable "SSM_PATH" if not provided
            :param params['max_age']: int
                Sets the time in seconds after which Cache is invalidated
            :param params['transform']: str, optional
                Transforms the content from a JSON object ('json') or base64 binary string ('binary').
                By Default, it pulls as is without any transformation
            :param params['decrypt']: bool
                If true, the configuration value will be decrypted
            :param params['force_fetch']: bool
                If true, the cache will be bypassed and the configuration value will be directly fetched from
                ÅWS Parameter Store service. Use it with caution as this might bring latency

        Applicable params for SecretManager:
            :param params['sm_path']: str
                Points to the SSM Path where the configuration is stored.
                Defaults to the environment variable "SM_PATH" if not provided
            :param params['max_age']: int
                Sets the time in seconds after which Cache is invalidated
            :param params['transform']: str, optional
                Transforms the content from a JSON object ('json') or base64 binary string ('binary').
                By Default, it pulls as is without any transformation
            :param params['force_fetch']: bool
                If true, the cache will be bypassed and the configuration value will be directly fetched from
                ÅWS Parameter Store service. Use it with caution as this might bring latency

        Applicable params for AppConfig:
            :param params['application']: str
                Points to the application name in the App Config. Defaults to the environment variable "APPCONFIG_APP"
                Should be provided as part of the object instantiation
            :param params['environment']: str
                Points to the environment name in the App Config. Defaults to the environment variable "APPCONFIG_ENV"
                Should be provided as part of the object instantiation

            :param params['configuration']: str
                Points to the configuration name in the App Config. Defaults to the environment variable "APPCONFIG_CONFIG"
            :param params['max_age']: int
                Sets the time in seconds after which Cache is invalidated
            :param params['transform']: str, optional
                Transforms the content from a JSON object ('json') or base64 binary string ('binary').
                By Default, it pulls as is without any transformation
            :param params['force_fetch']: bool
                If true, the cache will be bypassed and the configuration value will be directly fetched from
                AWS App Config service. Use it with caution as this might bring latency

        """
        env = Env()

        for class_property, property_value in params.items():
            setattr(self, class_property, property_value)

        instance_attributes = self.get_attributes()
        # Variable in params has the highest precedence.
        # If variable in params not present, then see if the class member variable is already set to non-default value?
        # If yes, we are good.
        # If class member variable is not set to non-default value, then try to lookup env variable if applicable
        try:
            for instance_attribute in instance_attributes:
                if instance_attribute not in params:
                    if not hasattr(self, instance_attribute) or getattr(
                        self, instance_attribute
                    ) in ["", None]:
                        if instance_attribute in BaseConfig.property_to_env_mappings:
                            setattr(
                                self,
                                instance_attribute,
                                env(
                                    BaseConfig.property_to_env_mappings[
                                        instance_attribute
                                    ]
                                ),
                            )
        except EnvError:
            error_obj = {
                "message": f"{instance_attribute} was neither explicitly provided as argument nor set as environment "
                f"variable.",
                "input_parameters": self.get_instance_attribute_values(),
            }
            LOGGER.exception(error_obj)
            raise EnvError(
                error_obj["message"],
                {"input_parameters": error_obj["input_parameters"]},
            )

        return None

    def validate_input_params(self) -> dict:
        """
        Overrode function. Please see BaseConfig's corresponding function for description
        """
        properties = self.get_instance_attribute_values()
        try:
            validated_input_params = BaseConfig.config_validator(properties)
        except MultipleInvalid:
            error_obj = {
                "message": "One of the input parameters was not valid. The supported schema is: "
                + str(BaseConfig.config_validator),
                "input_parameters": properties,
            }
            LOGGER.exception(error_obj)
            raise MultipleInvalid(json.dumps(error_obj))
        validated_input_params["transform"] = validated_input_params["transform"][0]
        validated_input_params = list(validated_input_params.values())

        return validated_input_params

    def get_attributes(self):
        validated_properties = BaseConfig.config_validator({"transform": []})
        instance_attributes = [
            instance_attribute
            for instance_attribute, instance_attribute_value in validated_properties.items()
        ]

        return instance_attributes

    def get_instance_attribute_values(self):
        instance_attributes = self.get_attributes()
        properties = {}
        for instance_attribute in instance_attributes:
            if instance_attribute == "transform":
                properties[instance_attribute] = [getattr(self, instance_attribute)]
            else:
                properties[instance_attribute] = getattr(self, instance_attribute)

        return properties

    def get(self, **sdk_options) -> Optional[Union[str, dict, bytes]]:
        """
        # This method should be overridden by the subclass.

        Pulls the configurations from the configured data source

        # At the source, it could be stored in one of the following formats:
        # [str, list, dict, bytes]

        Raises
        ------
        GetParameterError
            When unable to find the configuration at the configured data source
        TransformParameterError
            When unable to decode the data into the requested format

        """
        pass

    def get_multiple(
        self, **sdk_options
    ) -> Union[Dict[str, str], Dict[str, dict], Dict[str, bytes]]:
        """
        # This method should be overridden by the subclass.

        Pulls the configurations from the configured data source

        # At the source, it could be stored in one of the following formats:
        # [str, list, dict, bytes]

        :param sdk_options:

        Raises
        ------
        GetParameterError
            When unable to find the path at the configured data source
        TransformParameterError
            When unable to decode the data into the requested format

        """
        pass

    def set_attributes_to_default_values(self):
        """
        This method should be overridden by the subclass.

        Sets the class member variables to its default values as per the Configured Schema validation object.
        """

        pass
