import boto3
import json
import logging
import os
from subprocess import call

import src.lib.helpers.helpers as helpers
from src.lib.reportfunctions import PDFPSReport


logging.getLogger().setLevel(logging.INFO)


def create(event, context):
    """
    Creates a new pdf report of the company.
    Event['body']: { "id": "<company_id>"}
    """
    event_body = json.loads(event['body'])
    company_id = event_body['id']
    logging.info(f"Company UUID: {company_id}")
    helpers.validate_user(event, company_id)

    s3 = boto3.resource('s3')
    bucket = os.environ['S3_BUCKET_NAME']  
    report_name = str(company_id) + ".pdf"
    temp_pdf_path = "/tmp/report.pdf"

    logging.info("Generating PDF....")
    report = PDFPSReport(company_id, temp_pdf_path)

    # Upload pdf to s3 bucket
    logging.info("Uploading PDF to S3....")
    s3.Bucket(bucket).upload_file(temp_pdf_path, report_name)

    # Clear tmp storage in lambda
    call('rm -rf /tmp/*', shell=True)

    # Get download url for pdf
    logging.info("Retrieving URL to PDF....")
    s3_client = boto3.client('s3', region_name="ap-southeast-1",
                             config=boto3.session.Config(s3={'addressing_style': 'path'}, signature_version='s3v4', ))
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket,
                                                            'Key': report_name},
                                                    ExpiresIn=3600)
        logging.debug(response)
    except Exception as e:
        logging.exception(e)
        return {'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                }

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': response,
    }
