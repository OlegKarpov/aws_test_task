import random

from troposphere import (
    GetAtt,
    s3,
)

from aws_lambda import lambda_processing

bucket = s3.Bucket(
    'UploadedResources',
    VersioningConfiguration=s3.VersioningConfiguration(
        Status='Enabled',
    ),
    DependsOn=['LambdaProcessing', ],
    NotificationConfiguration=s3.NotificationConfiguration(
        LambdaConfigurations=[
            s3.LambdaConfigurations(
                Event='s3:ObjectCreated:*',
                Function=GetAtt(lambda_processing, 'Arn')
            )
        ]
    )
)
