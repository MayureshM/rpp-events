```json
[
    {
        "path": "ai-generated-tests/test_config_manager.py",
        "content": "import pytest\nfrom my_project.config_manager import ConfigManager\n\ndef test_config_manager_select_data_source():\n    config_manager = ConfigManager()\n    data_source = config_manager.select_data_source('AppConfig')\n    assert data_source == 'AppConfig'\n"
    },
    {
        "path": "ai-generated-tests/test_app_config.py",
        "content": "import pytest\nfrom my_project.app_config import AppConfig\n\ndef test_app_config_get_value():\n    app_config = AppConfig()\n    value = app_config.get_value('key')\n    assert value == 'mocked_value'\n"
    },
    {
        "path": "ai-generated-tests/test_parameter_store.py",
        "content": "import pytest\nfrom my_project.parameter_store import ParameterStore\n\ndef test_parameter_store_get_parameter():\n    parameter_store = ParameterStore()\n    parameter = parameter_store.get_parameter('param_name')\n    assert parameter == 'mocked_parameter'\n"
    },
    {
        "path": "ai-generated-tests/test_secret_manager.py",
        "content": "import pytest\nfrom my_project.secret_manager import SecretManager\n\ndef test_secret_manager_get_secret():\n    secret_manager = SecretManager()\n    secret = secret_manager.get_secret('secret_name')\n    assert secret == 'mocked_secret'\n"
    },
    {
        "path": "ai-generated-tests/test_dynamodb.py",
        "content": "import pytest\nfrom my_project.dynamodb import DynamoDB\n\ndef test_dynamodb_get_item():\n    dynamodb = DynamoDB()\n    item = dynamodb.get_item('table_name', 'key')\n    assert item == {'key': 'value'}\n"
    }
]
```