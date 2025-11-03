from typing import Dict, Optional, Union

from config.app_config import AppConfig
from config.dynamodb import DynamoDB
from config.parameter_store import ParameterStore
from config.secret_manager import SecretManager
from util import LOGGER


class ConfigManager:
    """
    ConfigManager supporting multi data sources (i.e. AppConfig, ParameterStore, SecretManager, DynamoDB)

    AppConfig Data Source:

    Example
    -------
    **Retrieves the latest configuration value from App Config**

        >>> from config.config_manager import ConfigManager
        >>>
        >>> params = {"application": "test-app", "environment": "production",}
        >>> config_manager = ConfigManager(data_provider="AppConfig", params=params)
        >>> input_params = {
            "configuration": "config-profile",
            "max_age": 5,
            "transform": "json",
            "force_fetch": False,
        }
        >>> config = config_manager.get(input_params)
        >>> print(config)
        My configuration value


    ParameterStore Data Source:

    Example 1
    -------
    **Retrieves a parameter value from Systems Manager Parameter Store**

    **Retrieves a configuration value from App Config in another AWS region**

        >>> from config.config_manager import ConfigManager
        >>>
        >>> config_manager = ConfigManager(data_provider="ParameterStore")
        >>> input_params = {
            "ssm_path": "single-value-param",
            "max_age": 5,
            "transform": "json",
            "raise_on_transform_error": False,
            "decrypt": False,
            "force_fetch": False,
        }
        >>> config = config_manager.get(input_params)
        >>> print(config)
        My configuration value

    Example 2
    -------
    **Retrieves multiple parameter values from Systems Manager Parameter Store using a path prefix**

    >>> from config.config_manager import ConfigManager
        >>>
        >>> config_manager = ConfigManager(data_provider="ParameterStore")
        >>> input_params = {
            "ssm_path": "/prefix-path/",
            "max_age": 5,
            "transform": "json",
            "raise_on_transform_error": False,
            "decrypt": False,
            "force_fetch": False,
        }
        >>> config = config_manager.get_multiple(input_params)
        >>> print(config)
        My configuration value

    SecretManager Data Source:

    Example
    -------
    **Retrieves a parameter value from Secrets Manager**

    >>> from config.config_manager import ConfigManager
    >>>
    >>> config_manager = ConfigManager(data_provider="SecretManager")
    >>> input_params = {
            "sm_path": "single-secret-manager",
            "max_age": 5,
            "transform": "json",
            "raise_on_transform_error": False,
            "force_fetch": False,
        }
    >>> config = config_manager.get(input_params)
    >>> print(config)
        My configuration value

    DynamoDB Data Source:

    Example 1
    -------
    **Retrieves a parameter value from a DynamoDB table**
    In this example, the DynamoDB table uses `id` as hash key and stores the value in the `value`
    attribute. The parameter item looks like this:

    { "id": "my-parameter", "value": "Parameter value a" }

    >>> from config.config_manager import ConfigManager
    >>>
    >>> params = {
            "table_name": "my-table-without-sort-key",
            "key_attr": "id",
            "sort_attr": "sk",
            "value_attr": "value",
        }
    >>> config_manager = ConfigManager(data_provider="DynamoDB", params=params)
    >>> input_params = {
            "key_attr_val": "my-parameter",
            "max_age": 5,
            # "transform": "json",
            "force_fetch": False,
        }
    >>> config = config_manager.get(input_params)
    >>> print(config)
        My configuration value


    Example 2
    -------
    **Retrieves multiple values from a DynamoDB table**
    In this case, the provider will use a sort key to retrieve multiple values using a query under
    the hood. This expects that the sort key is named `sk`. The DynamoDB table contains three items
    looking like this:

        { "id": "my-hash-key", "sk": "a", "value": "Parameter value a" }
        { "id": "my-hash-key", "sk": "b", "value": "Parameter value b" }
        { "id": "my-hash-key", "sk": "c", "value": "Parameter value c" }

    >>> from config.config_manager import ConfigManager
    >>>
    >>> params = {
            "table_name": "my-table",
            "key_attr": "id",
            "sort_attr": "sk",
            "value_attr": 'value',
        }
    >>> config_manager = ConfigManager(data_provider="DynamoDB", params=params)
    >>> input_params = {
            "key_attr_val": "my-hash-key",
            "max_age": 5,
            # "transform": "json",
            "force_fetch": False,
        }
    >>> config = config_manager.get_multiple(input_params)
    >>> print(config)
        My configuration value



    """

    def __init__(self, data_provider="ParameterStore", params={}):
        """
        Instantiates ConfigManager that behaves as a Proxy class for AppConfig, SecretManager, DynamoDB and
        ParameterStore providing simple interface to the callee

        :param data_provider:
            Binds to specific data source. Valid values are [AppConfig, SecretManager, DynamoDB, ParameterStore]
        :param params:
            params are Forwarded to the respective data provider constructor for initialization

        Raises
        ------
        KeyError
            When called for an unsupported data provider
        """
        class_map = {
            "AppConfig": AppConfig,
            "SecretManager": SecretManager,
            "DynamoDB": DynamoDB,
            "ParameterStore": ParameterStore,
        }
        try:
            if params and data_provider in ["AppConfig", "DynamoDB"]:
                self.data_provider = class_map[data_provider](params)
            else:
                self.data_provider = class_map[data_provider]()
        except KeyError:
            error_obj = {
                "message": "The provided data provider not supported. Supported data provider types are: "
                + ", ".join(class_map.keys()),
                "input_parameters": {"data_provider": data_provider},
            }

            LOGGER.exception(error_obj)
            raise KeyError(
                error_obj["message"],
                {"input_parameters": error_obj["input_parameters"]},
            )

    def get(self, params={}, **sdk_options) -> Optional[Union[str, dict, bytes]]:
        """
        Pulls the configuration value from the configured data source

        # At the source, it could be stored in one of the following formats:
        # [str, list, dict, bytes]

        Raises
        ------
        GetParameterError
            When unable to find the configuration at the configured data source
        TransformParameterError
            When unable to decode the data into the requested format

        """
        if isinstance(self.data_provider, ParameterStore):
            self.data_provider.populate_input_params(params)
            self.data_provider.validate_input_params()
            return self.data_provider.get(**sdk_options)

        if isinstance(self.data_provider, SecretManager):
            self.data_provider.populate_input_params(params)
            self.data_provider.validate_input_params()
            return self.data_provider.get(**sdk_options)

        if isinstance(self.data_provider, AppConfig):
            self.data_provider.populate_input_params(params)
            self.data_provider.validate_input_params()
            return self.data_provider.get(**sdk_options)

        if isinstance(self.data_provider, DynamoDB):
            self.data_provider.populate_input_params(params)
            self.data_provider.validate_input_params()
            return self.data_provider.get(**sdk_options)
        return None

    def get_multiple(
        self, params={}, **sdk_options
    ) -> Union[Dict[str, str], Dict[str, dict], Dict[str, bytes]]:
        """
        Pulls the configuration value(s) from the configured data source

        # At the source, it could be stored in one of the following formats:
        # [str, list, dict, bytes]

        Raises
        ------
        GetParameterError
            When unable to find the path at the configured data source
        TransformParameterError
            When unable to decode the data into the requested format

        """
        if isinstance(self.data_provider, ParameterStore):
            self.data_provider.populate_input_params(params)
            self.data_provider.validate_input_params()
            return self.data_provider.get_multiple(**sdk_options)
        elif isinstance(self.data_provider, SecretManager):
            raise NotImplementedError()
        elif isinstance(self.data_provider, AppConfig):
            raise NotImplementedError()
        elif isinstance(self.data_provider, SecretManager):
            raise NotImplementedError()
        elif isinstance(self.data_provider, DynamoDB):
            self.data_provider.populate_input_params(params)
            self.data_provider.validate_input_params()
            return self.data_provider.get_multiple(**sdk_options)
        return None
