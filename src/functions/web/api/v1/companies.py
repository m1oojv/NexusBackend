import boto3
import json
import logging
import os

import src.lib.helpers.helpers as helpers
from src.lib.scanners.scan_domain import delete_identifier
from src.lib.helpers.json_response import list_objects, success, with_object, with_dict
from src.lib.validators.user_validators import valid_user
from src.lib.errors.errors_handler import exception_response
import src.services.company_service as CompanyService

logging.getLogger().setLevel(logging.INFO)

def index(event, context):
  """
  Retrieves all companies associated to a user.
  /web/api/v1/companies
  """
  try:    
    valid_user(event)
    params = {
      #uncomment for production
      "user_id": user_id(event)
      #uncomment for dev
      # "user_id": 'e75d9c98-d162-439f-a641-3f376c8729a1'
    }    

    logging.info("Retrieving companies info")
    companies = CompanyService.all(**params)

    return list_objects(companies)
  except Exception as e:
    return exception_response(e)    

def show(event, context):
  """
  Retrieves details related to a company.
  /web/api/v1/insured-companies/{id}
  id can be found in event["pathParameters"]
  """
  try:
    valid_user(event)

    logging.info("Retrieving company info")
    params = {
      #uncomment for production
      "user_id": user_id(event),
      "id": event["pathParameters"]["id"],
      #uncomment for dev
      # "user_id": 'e75d9c98-d162-439f-a641-3f376c8729a1'
    }
    company = CompanyService.find(**params, joinedload=True)

    return with_dict(company)
  except Exception as e:
    return exception_response(e)

def create(event, context):
  """
  Called when users create a new client report to create a new company entry in the database.
  Is the first to be called and will trigger the client report calculation and generation process.
  Then passes on data to a SQS that runs the worker function below.
  /web/api/v1/companies
  Event['body']: { "pii": "<pii>", "domain": "<domain>", "employees": "<employees>",
                    "countries": "<countries>", "industry": "<industry>", "revenue": "<revenue>",
                    "company_name": "<company name>" }
  """
  try:    
    valid_user(event)
    #uncomment for production
    sqs = boto3.client('sqs', endpoint_url='https://sqs.ap-southeast-1.amazonaws.com')
    body = json.loads(event['body'])    
    body['user_id'] = user_id(event)
  
    logging.info("Creating company")
    company = CompanyService.create(**company_params(body))    

    # uncomment for production
    message_body = {
      "user_id": user_id(event),
      "company_id": str(company.id),
      "name": company.name,
      "domain": company.domain,
      "estimated_controls": 'Yes'
    }

    sqs.send_message(
      QueueUrl=os.environ['QUEUE_URL'],
      DelaySeconds=1,
      MessageBody=(json.dumps(message_body))                                            
    )

    logging.info("Data successfully sent to queue....")

    return with_object(company)
  except Exception as e:
    try:
      logging.info("Deleting company due to exception")
      CompanyService.delete_record(company.id)
      logging.info("Deleted company")
    except:
      pass
    return exception_response(e)

def update(event, context):
  """
  Called when users update details of a company.
  Event['body']: { "pii": "<pii>", "domain": "<domain>", "employees": "<employees>",
                    "countries": "<countries>", "industry": "<industry>", "revenue": "<revenue>",
                    "company_name": "<company name>" }
  """
  try:
    valid_user(event)
    
    id = event["pathParameters"]["id"]
    body = json.loads(event['body'])
    params = {
      "id": id,
      "body": company_params(body) 
    }
    
    logging.info("Update company info")
    company = CompanyService.update_record(params)

    return with_object(company)
  except Exception as e:
    return exception_response(e)

def delete(event, context):
  """
  Called when a company report is deleted from the dashboard.
  /web/api/v1/companies
  Event["body"]: "\"<company UUID>\""
  """
  try:
    valid_user(event)

    params = {
      "id": event["pathParameters"]["id"],
      #uncomment for production
      "user_id": user_id(event),      
      #uncomment for dev
      # "user_id": 'e75d9c98-d162-439f-a641-3f376c8729a1'
    }

    logging.info("Delete company")
    CompanyService.delete_record(**params)      
    return success()      
  except Exception as e:
    return exception_response(e)

def user_id(event):
  return event['requestContext']['authorizer']['jwt']['claims']['sub']

def company_params(params):
  return {
    "name": params['name'],
    "revenue": params['revenue'],
    "industry": params['industry'],
    "country": params['country'],
    "employees": params['employees'],
    "domain": params['domain'],
    "pii": params['pii'],
    "pci": 0,
    "phi": 0,
    "estimated_controls": 'Yes'    
  }