```json
[
    {
        "path": "ai-generated-tests/test_event_subscription.py",
        "content": "import pytest\nfrom unittest.mock import patch, MagicMock\nfrom your_project.event_subscription import EventSubscriptionManager\n\n\n@pytest.fixture\ndef event_subscription_manager():\n    return EventSubscriptionManager()\n\n\ndef test_create_subscription(event_subscription_manager):\n    # Arrange\n    subscription_data = {'event_type': 'task_event', 'target_endpoint': 'http://example.com'}\n    \n    # Act\n    with patch('your_project.dynamodb_client.put_item') as mock_put:\n        event_subscription_manager.create_subscription(subscription_data)\n        \n    # Assert\n    mock_put.assert_called_once_with(\n        TableName='Subscriptions',\n        Item={\n            'event_type': {'S': 'task_event'},\n            'target_endpoint': {'S': 'http://example.com'}\n        }\n    )\n\n\ndef test_update_subscription(event_subscription_manager):\n    # Arrange\n    subscription_id = '123'\n    updated_data = {'event_type': 'task_event', 'target_endpoint': 'http://new-example.com'}\n    \n    # Act\n    with patch('your_project.dynamodb_client.update_item') as mock_update:\n        event_subscription_manager.update_subscription(subscription_id, updated_data)\n        \n    # Assert\n    mock_update.assert_called_once()\n\n\ndef test_delete_subscription(event_subscription_manager):\n    # Arrange\n    subscription_id = '123'\n    \n    # Act\n    with patch('your_project.dynamodb_client.delete_item') as mock_delete:\n        event_subscription_manager.delete_subscription(subscription_id)\n        \n    # Assert\n    mock_delete.assert_called_once()\n"
    },
    {
        "path": "ai-generated-tests/test_event_processing.py",
        "content": "import pytest\nfrom unittest.mock import patch\nfrom your_project.event_processing import EventProcessor\n\n\n@pytest.fixture\ndef event_processor():\n    return EventProcessor()\n\n\ndef test_process_event(event_processor):\n    # Arrange\n    event_data = {'type': 'task_event', 'data': {'task_id': '1'}}\n    \n    # Act\n    with patch('your_project.sns_client.publish') as mock_publish:\n        event_processor.process_event(event_data)\n        \n    # Assert\n    mock_publish.assert_called_once()\n\n\ndef test_invalid_event(event_processor):\n    # Arrange\n    invalid_event_data = {'type': 'invalid_event'}\n    \n    # Act & Assert\n    with pytest.raises(ValueError):\n        event_processor.process_event(invalid_event_data)\n"
    },
    {
        "path": "ai-generated-tests/test_dynamodb_integration.py",
        "content": "import pytest\nfrom unittest.mock import patch\nfrom your_project.dynamodb_integration import DynamoDBManager\n\n\n@pytest.fixture\ndef dynamodb_manager():\n    return DynamoDBManager()\n\n\ndef test_create_item(dynamodb_manager):\n    # Arrange\n    item_data = {'id': '1', 'value': 'test'}\n    \n    # Act\n    with patch('your_project.dynamodb_client.put_item') as mock_put:\n        dynamodb_manager.create_item(item_data)\n        \n    # Assert\n    mock_put.assert_called_once()\n\n\ndef test_get_item(dynamodb_manager):\n    # Arrange\n    item_id = '1'\n    \n    # Act\n    with patch('your_project.dynamodb_client.get_item') as mock_get:\n        dynamodb_manager.get_item(item_id)\n        \n    # Assert\n    mock_get.assert_called_once()\n"
    },
    {
        "path": "ai-generated-tests/test_config_manager.py",
        "content": "import pytest\nfrom unittest.mock import patch\nfrom your_project.config_manager import ConfigManager\n\n\n@pytest.fixture\ndef config_manager():\n    return ConfigManager()\n\n\ndef test_load_config(config_manager):\n    # Arrange\n    expected_config = {'key': 'value'}\n    \n    # Act\n    with patch('your_project.aws_client.get_parameter') as mock_get:\n        mock_get.return_value = expected_config\n        config = config_manager.load_config('test_config')\n        \n    # Assert\n    assert config == expected_config\n\n\ndef test_invalid_config(config_manager):\n    # Arrange\n    with patch('your_project.aws_client.get_parameter', side_effect=Exception('Not Found')):\n        \n        # Act & Assert\n        with pytest.raises(Exception):\n            config_manager.load_config('invalid_config')\n"
    },
    {
        "path": "ai-generated-tests/test_integration.py",
        "content": "import pytest\nfrom fastapi.testclient import TestClient\nfrom your_project.main import app\n\n\n@pytest.fixture\ndef client():\n    return TestClient(app)\n\n\ndef test_create_subscription(client):\n    # Arrange\n    subscription_data = {'event_type': 'task_event', 'target_endpoint': 'http://example.com'}\n    \n    # Act\n    response = client.post('/subscriptions', json=subscription_data)\n    \n    # Assert\n    assert response.status_code == 201\n    assert response.json() == {'message': 'Subscription created'}\n\n\ndef test_process_event(client):\n    # Arrange\n    event_data = {'type': 'task_event', 'data': {'task_id': '1'}}\n    \n    # Act\n    response = client.post('/events', json=event_data)\n    \n    # Assert\n    assert response.status_code == 200\n    assert response.json() == {'message': 'Event processed'}\n"
    },
    {
        "path": "ai-generated-tests/pytest.ini",
        "content": "[pytest]\naddopts = -v\n"
    },
    {
        "path": "ai-generated-tests/conftest.py",
        "content": "import pytest\n\n\n@pytest.fixture(autouse=True)\ndef setup_environment():\n    import os\n    os.environ['AWS_REGION'] = 'us-east-1'\n    os.environ['DYNAMODB_TABLE'] = 'Subscriptions'\n"
    },
    {
        "path": "ai-generated-tests/README.md",
        "content": "# RPP Events and Configuration Management Tests\n\nThis directory contains tests for the RPP Events and Configuration Management project.\n\n## Running Tests\n\nTo run the tests, use the following command:\n\n```bash\npytest ai-generated-tests/\n```\n"
    }
]
```