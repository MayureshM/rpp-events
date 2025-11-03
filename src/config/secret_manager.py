from aws_lambda_powertools.utilities.parameters import SecretsProvider
from typing import Union, Optional
from voluptuous import (
    Schema,
    ALLOW_EXTRA,
    Required,
    Range,
    All,
)
from util import LOGGER
from aws_lambda_powertools.utilities.parameters import (
    GetParameterError,
    TransformParameterError,
)
from config.base_config import DEFAULT_CACHE_TTL, BaseConfig


class SecretManager(SecretsProvider, BaseConfig):
    """
    Required IAM Permissions:
        - secretsmanager:GetSecretValue

    Environment variables:
        - SM_PATH
    """

    def __init__(self):
        """
        Instantiates SecretManager

        """
        self.set_attributes_to_default_values()

        super().__init__()

    def set_attributes_to_default_values(self):
        """
        Overrode function. Please see BaseConfig's corresponding function for description
        """
        BaseConfig.config_validator = Schema(
            {
                Required("sm_path", default=""): All(str),
                Required("max_age", default=DEFAULT_CACHE_TTL): All(
                    int, Range(min=DEFAULT_CACHE_TTL)
                ),
                Required("transform", default=None): ["json", "base64", None],
                Required("raise_on_transform_error", default=False): bool,
                Required("force_fetch", default=False): bool,
            },
            required=True,
            extra=ALLOW_EXTRA,
        )
        BaseConfig.property_to_env_mappings = {
            "sm_path": "SM_PATH",
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
                self.sm_path,
                max_age=self.max_age,
                transform=self.transform,
                force_fetch=self.force_fetch,
                **sdk_options,
            )
        except GetParameterError as e:
            LOGGER.exception(
                {
                    "message": "Could not find the path from AWS Secret Manager.",
                    "error": e,
                    "record": self.get_instance_attribute_values(),
                }
            )
            raise e
        except TransformParameterError:
            error_obj = {
                "message": "Could not transform the data from AWS Secret Manager.",
                "input_parameters": self.get_instance_attribute_values(),
            }
            LOGGER.exception(error_obj)
            raise TransformParameterError(
                error_obj["message"],
                {"input_parameters": error_obj["input_parameters"]},
            )

        return config
