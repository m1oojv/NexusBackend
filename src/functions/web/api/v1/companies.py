import boto3
import json
import logging
import os

import src.lib.helpers.helpers as helpers
from src.lib.scanners.scan_domain import delete_identifier
from src.lib.helpers.json_response import list_objects, success, with_object, with_dict, unprocessable_entity
from src.lib.validators.user_validators import valid_user
from src.lib.errors.errors_handler import exception_response
import src.services.company_service as CompanyService

logging.getLogger().setLevel(logging.INFO)

# class Encoder(json.JSONEncoder):
#   def default(self, obj):
#     if isinstance(obj, Decimal):
#       return float(obj)

def index(event, context):
  """
  Retrieves all companies associated to a user.
  /web/api/v1/companies
  """
  try:
    valid_user(event)
    
    params = {
      #uncomment for production
      #"user_id": event['requestContext']['authorizer']['jwt']['claims']['sub']
      #uncomment for dev
      "user_id": 'e75d9c98-d162-439f-a641-3f376c8729a1'
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
    logging.info("Retrieving company info")
    params = {
      #uncomment for production
      #"user_id": event['requestContext']['authorizer']['jwt']['claims']['sub']
      "id": event["pathParameters"]["id"],
      #uncomment for dev
      "user_id": 'e75d9c98-d162-439f-a641-3f376c8729a1'
    }
    company = CompanyService.find_all(**params)

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
    user = helpers.User(event)
    #uncomment for production
    #sqs = boto3.client('sqs', endpoint_url='https://sqs.ap-southeast-1.amazonaws.com')
    body = json.loads(event['body'])
    body['user_id'] = user.user_id
  
    logging.info("Creating company")
    company = CompanyService.create(**create_company_params(body))    

    #uncomment for production
    # sqs.send_message(QueueUrl=os.environ['QUEUE_URL'],
    #                 DelaySeconds=1,
    #                 MessageBody=(json.dumps({
    #                                           "user_id": body['user_id'],
    #                                           "company_id": str(company.id),
    #                                           "company_name": company.name,
    #                                           "domain": company.domain,
    #                                           "estimated_controls": 'Yes'
    #                                           }
    #                                         )
    #                               )
    #                 )

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
    id = event["pathParameters"]["id"]
    body = json.loads(event['body'])
    params = {
      "id": id,
      "body": update_company_params(body) 
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
    params = {
      #uncomment for production
      #"user_id": event['requestContext']['authorizer']['jwt']['claims']['sub']
      "id": event["pathParameters"]["id"],
      #uncomment for dev
      "user_id": 'e75d9c98-d162-439f-a641-3f376c8729a1'
    }

    logging.info("Delete company")
    CompanyService.delete_record(**params)      
    return success()      
  except Exception as e:
    return exception_response(e)

def create_company_params(params):
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
    "estimated_controls": 'Yes',
    "user_id": params['user_id']
  }

def update_company_params(params):
  return {
    "name": params['name']
    # "revenue": params['revenue'],
    # "industry": params['industry'],
    # "country": params['country'],
    # "employees": params['employees'],
    # "domain": params['domain'],
    # "pii": params['pii'],
    # "pci": params['pci'],
    # "phi": params['phi']
  }

# def company_params(params):
#   return {
#     "name": params['name'],
#     "revenue": params['revenue'],
#     "industry": params['industry'],
#     "country": params['country'],
#     "description": params['description'],
#     "assessment_progress": params['assessment_progress'],
#     "last_assessed_at": params['last_assessed_at'],
#     "employees": params['employees'],
#     "domain": params['domain'],
#     "threat_assessment_status": params['threat_assessment_status'],
#     "scan_status": params['scan_status'],
#     "pii": params['pii'],
#     "pci": params['pci'],
#     "phi": params['phi'],
#     "control_status": params['control_status'],
#     "scan_results": params['scan_results'],
#     "estimated_controls": params['estimated_controls'],
#     "application_datetime": params['application_datetime'],
#     "tenant_id": params['tenant_id'],
#     "user_id": params['user_id']
#   }