''' module for testing custom resource '''
import json
import os
import pytest
import mock
import boto3
from requests.models import Response
from pytest_voluptuous import S
from voluptuous import Optional
from moto import mock_sns
from moto import mock_sqs
from moto import mock_kinesis
from rpp_events.cfn.rpp_events_subscription import handler


with open('tests/custom_resource_tests.json') as f:
    TESTS = json.load(f)


TESTS = [(key, TESTS[key]) for key in TESTS.keys()]

STATUS = "SUCCESS"


def pytest_generate_tests(metafunc):
    ''' function to generate tests functions from test json '''
    idlist = []
    argvalues = []
    for test in TESTS:
        idlist.append(test[0])
        items = test[1].items()
        argnames = [x[0] for x in items]
        argvalues.append(([x[1] for x in items]))
    metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")


# pylint: disable=missing-docstring

@pytest.fixture(scope='module')
def create_topic():
    with mock_sns():
        client = boto3.client('sns')
        topic_arn = client.create_topic(Name='test_topic')['TopicArn']
        yield topic_arn


@pytest.fixture(scope='module')
def create_queue():
    with mock_sqs():
        client = boto3.client('sqs')
        queue_url = client.create_queue(QueueName='test_queue')['QueueUrl']
        yield queue_url


@pytest.fixture(scope='module')
def create_stream():
    with mock_kinesis():
        client = boto3.client('kinesis')
        stream_name = 'test_stream'
        client.create_stream(
            StreamName=stream_name,
            ShardCount=3
        )
        yield stream_name


def request_put(url, data, **kwargs):
    response = {'url': url, 'data': json.loads(data), 'optional': kwargs}
    if STATUS == "SUCCESS":
        assert S(
            {
                'url': url,
                'data': {
                    'Status': STATUS,
                    'StackId': str,
                    'RequestId': str,
                    'LogicalResourceId': str,
                    'PhysicalResourceId': str,
                    'Data': {
                        Optional('SQSSubscriptionArn'): str,
                        Optional('LambdaSubscriptionArn'): str,
                        'TopicArn': str,
                        'StreamName': str
                    }
                },
                'optional': {
                    'headers': {
                        'Content-Type': "",
                        'Content-Length': str
                    }
                },
            }
        ) == response

    if STATUS == "FAILURE":
        assert S(
            {
                'url': url,
                'data': {
                    'Status': STATUS,
                    'StackId': str,
                    'RequestId': str,
                    'LogicalResourceId': str,
                    'Reasons': str,
                },
                'optional': {
                    'headers': {
                        'Content-Type': "",
                        'Content-Length': str
                    }
                },
            }
        ) == response

    fake_r = Response()
    fake_r.status_code = 300

    return fake_r


# pylint: disable=unused-argument, redefined-outer-name
@mock.patch('requests.put', side_effect=request_put)
def handle_event(event, mock=None):
    handler(event, None)


# pylint: disable=invalid-name, unused-variable, global-statement
def test_custom_resource(event, status, create_topic, create_stream):
    os.environ["EVENT_BUS_ARN"] = create_topic
    os.environ["EVENT_FIREHOSE"] = create_stream
    global STATUS
    STATUS = status
    handle_event(event)
