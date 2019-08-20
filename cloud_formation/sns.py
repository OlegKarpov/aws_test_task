from troposphere import (
    Ref,
    sns,
)

sns_topic = sns.Topic("SNSTopic", )
subscription = sns.SubscriptionResource(
    'SNSTopicSubscription',
    Protocol='email',
    Endpoint='karpovhub@gmail.com',
    TopicArn=Ref(sns_topic)
)
