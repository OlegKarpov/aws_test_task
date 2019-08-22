import re

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_s3

from cloud_formation.constants import DYNAMO_DB_TABLE
from cloud_formation.test.conftest import do_test_setup


def s3_object_created_event(bucket_name, key):
    # NOTE: truncated event object shown here
    return {
      "Records": [
        {
          "s3": {
            "object": {
              "key": key,
            },
            "bucket": {
              "name": bucket_name,
            },
          },
        }
      ]
    }


# def test_function():
#     with mock_s3():
#         # Create the bucket
#         conn = boto3.resource('s3', region_name='us-east-1')
#         conn.create_bucket(Bucket="some-bucket")
#         # Add a file
#         boto3.client('s3', region_name='us-east-1').put_object(Bucket="some-bucket",
#                                                                Key="incoming/transaction-0001.txt",
#                                                                Body="Lambda S3 Test!")
#
#
#         # Run call with an event describing the file:
#         call(s3_object_created_event("some-bucket", "incoming/transaction-0001.txt"), None)
#
#         with pytest.raises(ClientError) as e_info:
#             conn.Object("some-bucket", "incoming/transaction-0001.txt").get()
#             assert e_info.response['Error']['Code'] == 'NoSuchKey'
#
#         # Check that it exists in `processed/`
#         obj = conn.Object("some-bucket", "processed/transaction-0001.txt").get()
#         assert obj['Body'].read() == b'Lambda S3 Test!'


def move_object_to_processed(s3_client, original_bucket, original_key):
    new_key = re.sub("incoming\/", "processed/", original_key)
    s3_client.copy_object(
        Bucket=original_bucket,
        Key=new_key,
        CopySource={'Bucket': original_bucket, 'Key': original_key}
    )
    s3_client.delete_object(Bucket=original_bucket, Key=original_key)


def call(event, context):

    s3_client = boto3.client('s3')
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    table = boto3.resource('dynamodb', region_name='us-east-1').Table(DYNAMO_DB_TABLE)
    txn_id = re.search("incoming\/transaction-(\d*).txt", key).group(1)
    table.put_item(
        Item={
            'transaction_id': txn_id,
            'body': s3_client.get_object(
                Bucket=bucket,
                Key=key
             )['Body'].read().decode('utf-8')
        }
    )
    # move_object_to_processed(s3_client, bucket, key)


def test_handler_adds_record_in_dynamo_db_about_object():
    BUCKET = "some-bucket"
    KEY = "incoming/transaction-0001.txt"

    with do_test_setup():
        call(s3_object_created_event(BUCKET, KEY), None)

        table = boto3.resource('dynamodb', region_name='us-east-1').Table(DYNAMO_DB_TABLE)
        item = table.get_item(Key={'transaction_id': '0001'})['Item']
        assert item['body'] == 'Hello World!'