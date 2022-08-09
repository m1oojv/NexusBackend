import boto3
import json
import os
import uuid
import datetime

def defaultconverter(o):
  if isinstance(o, datetime.datetime):
      return o.__str__()

class User:
    def __init__(self, event):
        self.tenant_id = event['requestContext']['authorizer']['jwt']['claims']['custom:tenant_id']
        self.user_id = event['requestContext']['authorizer']['jwt']['claims']['sub']

def handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    if (event['request']['userAttributes']['cognito:user_status'] == "FORCE_CHANGE_PASSWORD"):
        table.put_item(
            Item={
                    'tenantId': event['request']['userAttributes']['custom:tenant_id'],
                    'userId': event['request']['userAttributes']['sub'],
                    'email': event['request']['userAttributes']['email'],
                    'phone': event['request']['userAttributes']['phone_number'],
                }
            )
    response = table.get_item(
        Key={
            'tenantId': 'Protoslabs',
            'userId': 'Demo'
        }
    )
    item = response['Item']
    print(item)

    return event

def userprofile(event, context):
    user = User(event)
    dynamodb = boto3.resource('dynamodb')
    print(event)
    table = dynamodb.Table('userData')
    response = table.get_item(
        Key={
            'tenantId': user.tenant_id,
            'userId': user.user_id
        }
    )
    print(response)

    return {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': json.dumps(response['Item']),
    }

def createnewuser(event, context):
    print(event)
    data = json.loads(event['body'])
    if (event['requestContext']['authorizer']['jwt']['claims']['custom:role'] != "admin"):
        return {
        'statusCode': 401,
        'headers': {'Content-Type': 'application/json'},
        }

    cognito = boto3.client('cognito-idp', 
        region_name = os.environ['REGION']
    )

    dynamodb = boto3.resource('dynamodb')
    print(cognito)
    table = dynamodb.Table('userData')

    try:
        response = cognito.admin_create_user(
            UserPoolId=os.environ['POOL_ID'],
            Username=data['email'],
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': data['email']
                },
                {
                    'Name': 'phone_number',
                    'Value': data['phoneNumber']
                },
                {
                    'Name': 'custom:tenant_id',
                    'Value': event['requestContext']['authorizer']['jwt']['claims']['custom:tenant_id']
                },
                {
                    'Name': 'custom:role',
                    'Value': 'user'
                },
                {
                    'Name': 'email_verified',
                    'Value': 'true'
                },
                {
                    'Name': 'phone_number_verified',
                    'Value': 'true'
                },
            ],
            ForceAliasCreation=False,
            DesiredDeliveryMediums=['EMAIL'],
        )
        print(response)
    except (ValueError, TypeError):
        print(ValueError, TypeError)
        return {
        'statusCode': 500,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(ValueError)
        }
    
    try:
        table.put_item(
            Item=
            {
                'tenantId': event['requestContext']['authorizer']['jwt']['claims']['custom:tenant_id'],
                'userId': response['User']['Username'],
                'email': data['email'],
                'phone': data['phoneNumber'],
                'role': 'User',
                'userCreateDate': str(response['User']['UserCreateDate'])
            }
        )
    except (ValueError, TypeError):
        print(ValueError, TypeError)
        return {
        'statusCode': 500,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(ValueError)
        }

    return {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': json.dumps(response, default = defaultconverter),
    }
