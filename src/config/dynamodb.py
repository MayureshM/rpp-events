from typing import Dict, Optional, Union

from aws_lambda_powertools.utilities.parameters import (
    DynamoDBProvider,
    GetParameterError,
    TransformParameterError,
)
from voluptuous import ALLOW_EXTRA, All
from voluptuous import Range, Required, Schema

from config.base_config import DEFAULT_CACHE_TTL, BaseConfig
from util import LOGGER


class DynamoDB(DynamoDBProvider, BaseConfig):
    """
    Required IAM Permissions:
        - dynamodb:GetItem
        - dynamodb:Query

    Environment variables:
        - DYNAMO_DB_TABLE_NAME
        - DYNAMO_DB_KEY_ATTR
        - DYNAMO_DB_SORT_ATTR
        - DYNAMO_DB_VALUE_ATTR
    """

    def __init__(self, params={}):
        """
        Instantiates DynamoDB with the optional params. Falls back to the Configuration Variable if specific variable
        in the params dictionary not found.

        :param params['table_name']: str
            Points to the table name in the DynamoDB.
            Defaults to the environment variable "DYNAMO_DB_TABLE_NAME" if not provided
        :param params['key_attr']: str
            Points to the key attribute of the table.
            Defaults to the environment variable "DYNAMO_DB_KEY_ATTR" if not provided
        :param params['sort_attr']: str
            Points to the sort attribute of the table.
            Defaults to the environment variable "DYNAMO_DB_SORT_ATTR" if not provided
        :param params['value_attr']: str, optional
            Points to the value attribute of the table.
            Defaults to the environment variable "DYNAMO_DB_VALUE_ATTR" if not provided

        Raises
        ------
        EnvError
            When unable to find the required environment variable

        """
        self.set_attributes_to_default_values()

        self.populate_input_params(params)
        self.validate_input_params()

        super().__init__(
            self.table_name,
            key_attr=self.key_attr,
            sort_attr=self.sort_attr,
            value_attr=self.value_attr,
        )

    def set_attributes_to_default_values(self):
        """
        Overrode function. Please see BaseConfig's corresponding function for description
        """
        BaseConfig.config_validator = Schema(
            {
                Required("table_name", default=""): All(str),
                Required("key_attr", default=""): All(str),
                Required("key_attr_val", default=""): All(str),
                Required("sort_attr", default=""): All(str),
                Required("value_attr", default=""): All(str),
                Required("transform", default=None): ["json", "base64", None],
                Required("raise_on_transform_error", default=False): bool,
                Required("max_age", default=DEFAULT_CACHE_TTL): All(
                    int, Range(min=DEFAULT_CACHE_TTL)
                ),
                Required("force_fetch", default=False): bool,
            },
            required=True,
            extra=ALLOW_EXTRA,
        )
        BaseConfig.property_to_env_mappings = {
            "table_name": "DYNAMO_DB_TABLE_NAME",
            "key_attr": "DYNAMO_DB_KEY_ATTR",
            "sort_attr": "DYNAMO_DB_SORT_ATTR",
            "value_attr": "DYNAMO_DB_VALUE_ATTR",
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
                self.key_attr_val,
                max_age=self.max_age,
                transform=self.transform,
                force_fetch=self.force_fetch,
                **sdk_options,
            )
        except GetParameterError as e:
            LOGGER.exception(
                {
                    "message": "Could not find the configurations from AWS DynamoDB.",
                    "error": e,
                    "record": self.get_instance_attribute_values(),
                }
            )
            raise e
        except TransformParameterError:
            error_obj = {
                "message": "Could not transform the requested data from AWS DynamoDB.",
                "input_parameters": self.get_instance_attribute_values(),
            }
            LOGGER.exception(error_obj)
            raise TransformParameterError(
                error_obj["message"],
                {"input_parameters": error_obj["input_parameters"]},
            )

        return config

    def get_multiple(
        self, **sdk_options
    ) -> Union[Dict[str, str], Dict[str, dict], Dict[str, bytes]]:
        """
        Overrode function. Please see BaseConfig's corresponding function for description
        """
        try:
            configs = super().get_multiple(
                self.key_attr_val,
                max_age=self.max_age,
                transform=self.transform,
                raise_on_transform_error=self.raise_on_transform_error,
                force_fetch=self.force_fetch,
                **sdk_options,
            )
        except GetParameterError as e:
            LOGGER.exception(
                {
                    "message": "Could not find the configurations from AWS DynamoDB.",
                    "error": e,
                    "record": self.get_instance_attribute_values(),
                }
            )
            raise e
        except TransformParameterError:
            error_obj = {
                "message": "Could not transform the requested data from AWS DynamoDB.",
                "input_parameters": self.get_instance_attribute_values(),
            }
            LOGGER.exception(error_obj)
            raise TransformParameterError(
                error_obj["message"],
                {"input_parameters": error_obj["input_parameters"]},
            )

        return configs
