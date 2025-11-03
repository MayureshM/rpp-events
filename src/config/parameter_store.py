from typing import Dict, Optional, Union

from aws_lambda_powertools.utilities.parameters import (
    GetParameterError, SSMProvider, TransformParameterError)
from voluptuous import ALLOW_EXTRA, All
from voluptuous import Range, Required, Schema

from config.base_config import DEFAULT_CACHE_TTL, BaseConfig
from util import LOGGER


class ParameterStore(SSMProvider, BaseConfig):
    """
    Required IAM Permissions:
        - ssm:GetParameter
        - ssm:GetParametersByPath

    Environment variables:
        - SSM_PATH
    """

    def __init__(self):
        """
        Instantiates ParameterStore
        """

        self.set_attributes_to_default_values()

        super().__init__()

    def set_attributes_to_default_values(self):
        """
        Overrode function. Please see BaseConfig's corresponding function for description
        """
        BaseConfig.config_validator = Schema(
            {
                Required("ssm_path", default=""): All(str),
                Required("max_age", default=DEFAULT_CACHE_TTL): All(
                    int, Range(min=DEFAULT_CACHE_TTL)
                ),
                Required("transform", default=None): ["json", "base64", None],
                Required("raise_on_transform_error", default=False): bool,
                Required("decrypt", default=False): bool,
                Required("force_fetch", default=False): bool,
            },
            required=True,
            extra=ALLOW_EXTRA,
        )

        BaseConfig.property_to_env_mappings = {
            "ssm_path": "SSM_PATH",
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
                self.ssm_path,
                max_age=self.max_age,
                transform=self.transform,
                decrypt=self.decrypt,
                force_fetch=self.force_fetch,
                **sdk_options,
            )
        except GetParameterError:
            error_obj = {
                "message": "Could not find the path from AWS Parameter Store.",
                "input_parameters": self.get_instance_attribute_values(),
            }
            LOGGER.exception(error_obj)
            raise GetParameterError(
                error_obj["message"],
                {"input_parameters": error_obj["input_parameters"]},
            )
        except GetParameterError as e:
            LOGGER.exception(
                {
                    "message": "Could not find the path from AWS Parameter Store.",
                    "error": e,
                    "record": self.get_instance_attribute_values()
                }
            )
            raise e
        except TransformParameterError:
            error_obj = {
                "message": "Could not transform the data from AWS Parameter Store.",
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
                self.ssm_path,
                max_age=self.max_age,
                transform=self.transform,
                raise_on_transform_error=self.raise_on_transform_error,
                force_fetch=self.force_fetch,
                **sdk_options,
            )
        except GetParameterError:
            error_obj = {
                "message": "Could not find the path from AWS Parameter Store.",
                "input_parameters": self.get_instance_attribute_values(),
            }
            LOGGER.exception(error_obj)
            raise GetParameterError(
                error_obj["message"],
                {"input_parameters": error_obj["input_parameters"]},
            )
        except TransformParameterError:
            error_obj = {
                "message": "Could not transform the data from AWS Parameter Store.",
                "input_parameters": self.get_instance_attribute_values(),
            }
            LOGGER.exception(error_obj)
            raise TransformParameterError(
                error_obj["message"],
                {"input_parameters": error_obj["input_parameters"]},
            )

        return configs
