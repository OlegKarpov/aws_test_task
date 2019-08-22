import os

import boto3
import moto
import pytest
from moto import mock_s3, mock_dynamodb2

from cloud_formation.constants import DYNAMO_DB_TABLE

TEST_BUCKET_NAME = 'test-bucket'
TEST_DYNAMO_TABLE_NAME = 'test-dynamodb-table'


@pytest.fixture
def s3_bucket():
    with moto.mock_s3():
        boto3.client('s3').create_bucket(Bucket=TEST_BUCKET_NAME)
        yield boto3.resource('s3').Bucket(TEST_BUCKET_NAME)


@pytest.fixture
def dynamodb_table():
    with moto.mock_dynamodb2():
        boto3.client('dynamodb').create_table(
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'}
            ],
            TableName=TEST_DYNAMO_TABLE_NAME,
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            ProvisionedThroughput={
                'ReadCapacityUnits': 123,
                'WriteCapacityUnits': 123,
            },
        )
        yield boto3.resource('dynamodb').Table(TEST_DYNAMO_TABLE_NAME)


@pytest.fixture
def file_mock():
    with open("test_file.txt", "w") as file:
        file.write("Your text goes here")

        return file


EVENT_FILE = os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    'events',
    'test_file.txt'
)


@pytest.fixture()
def event():
    event = {
        "Records": [
            {
                "eventVersion": "2.0",
                "eventSource": "aws:s3",
                "awsRegion": "us-east-1",
                "eventTime": "2016-09-25T05:15:44.261Z",
                "eventName": "ObjectCreated:Put",
                "userIdentity": {
                    "principalId": "AWS:AROAW5CA2KAGZPAWYRL7K:cli"
                },
                "requestParameters": {
                    "sourceIPAddress": "222.24.107.21"
                },
                "responseElements": {
                    "x-amz-request-id": "00093EEAA5C7G7F2",
                    "x-amz-id-2": "9tTklyI/OEj4mco12PgsNksgxAV3KePn7WlNSq2rs+LXD3xFG0tlzgvtH8hClZzI963KYJgVnXw="
                },
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "configurationId": "151dfa64-d57a-4383-85ac-620bce65f269",
                    "bucket": {
                        "name": "service-1474780369352-1",
                        "ownerIdentity": {
                            "principalId": "A3QLJ3P3P5QY05"
                        },
                        "arn": "arn:aws:s3:::service-1474780369352-1"
                    },
                    "object": {
                        "key": "object",
                        "size": 11,
                        "eTag": "5eb63bbbe01eetd093cb22bb8f5acdc3",
                        "sequencer": "0057E75D80IA35C3E0"
                    }
                }
            }
        ]
    }
    return event


BUCKET = "some-bucket"
KEY = "incoming/transaction-0001.txt"
BODY = "Hello World!"

## Test Setup Functions
from contextlib import contextmanager


@contextmanager
def do_test_setup():
    with mock_s3():
        with mock_dynamodb2():
            set_up_s3()
        set_up_dynamodb()
        yield


def set_up_s3():
    conn = boto3.resource('s3', region_name='us-east-1')
    conn.create_bucket(Bucket=BUCKET)
    boto3.client('s3', region_name='us-east-1').put_object(Bucket=BUCKET, Key=KEY, Body=BODY)


TXNS_TABLE = "my-transactions-table"


def set_up_dynamodb():
    client = boto3.client('dynamodb', region_name='us-east-1')
    client.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'transaction_id',
                'AttributeType': 'N'
            },
        ],
        KeySchema=[
            {
                'AttributeName': 'transaction_id',
                'KeyType': 'HASH'
            }
        ],
        TableName=DYNAMO_DB_TABLE,
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
