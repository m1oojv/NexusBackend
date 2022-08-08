import boto3
import json
import logging
import os
import uuid
from datetime import datetime

import src.lib.helpers.helpers as helpers

logging.getLogger().setLevel(logging.INFO)

def default_converter(obj):
    if isinstance(obj, datetime):
        return obj.__str__()

def show(event, context):
    user = helpers.User(event)
    dynamodb = boto3.resource('dynamodb')
    logging.debug(f"Event:\n{event}")
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    response = table.get_item(Key={'tenantId': user.tenant_id,
                                   'userId': user.user_id
                                   }
                              )
    logging.debug(f"Response:\n{response}")

    return {'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response['Item']),
            }


def create(event, context):
    logging.debug(f"Event:\n{event}")
    tenant_uuid = str(uuid.uuid4())
    print(tenant_uuid)

    cognito = boto3.client('cognito-idp',
                           region_name=os.environ['REGION']
                           )
    logging.debug(f"Cognito:\n{cognito}")
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])

    try:
        response = cognito.admin_create_user(
            UserPoolId=os.environ['POOL_ID'],
            Username=event['email'],
            UserAttributes=[{'Name': 'email',
                             'Value': event['email']
                             },
                            {'Name': 'phone_number',
                             'Value': event['phoneNumber']
                             },
                            {'Name': 'custom:tenant_id',
                             'Value': tenant_uuid
                             },
                            {'Name': 'custom:user_type',
                             'Value': event['userType']
                             },
                            {'Name': 'custom:access_type',
                             'Value': event['accessType']
                             },
                            {'Name': 'email_verified',
                             'Value': 'true'
                             },
                            {'Name': 'phone_number_verified',
                             'Value': 'true'
                             },
                            ],
            ForceAliasCreation=False,
            DesiredDeliveryMediums=['EMAIL'],
        )
        logging.debug(response)
    except (ValueError, TypeError) as e:
        logging.exception(e)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(str(e))
        }

    try:
        table.put_item(
            Item={'tenantId': tenant_uuid,
                  'userId': response['User']['Username'],
                  'firstName': event['firstName'],
                  'lastName': event['lastName'],
                  'organization': event['organization'],
                  'jobTitle': event['jobTitle'],
                  'email': event['email'],
                  'phone': event['phoneNumber'],
                  'user_type': event['userType'],
                  'access_type': event['accessType'],
                  'userCreateDate': str(response['User']['UserCreateDate']),
                  'userLastModifiedDate': str(response['User']['UserLastModifiedDate']),
                  }
        )
    except (ValueError, TypeError) as e:
        logging.exception(e)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(str(e))
        }
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(response, default=lambda x: str(x)),
    }

""" 
data for create new user function
{
    "firstName": "Simeon",
    "lastName": "Tan",
    "organization": "Protos Labs",
    "jobTitle": "CTO",
    "email": "simeon_tan@protoslabs.sg",
    "phoneNumber": "+6581298114",
    "userType": "user" || "admin",
    "accessType": "broker" || "sme" || "superadmin"
} """