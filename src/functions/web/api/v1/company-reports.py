import boto3
import json
import logging
import os
from subprocess import call

import src.lib.helpers.helpers as helpers
import src.lib.sqlfunctions as sql_functions
from src.lib.report_generators.prelim_report import PrelimReport
from src.lib.report_generators.full_report import FullReport

logging.getLogger().setLevel(logging.INFO)


def generate_report(event, context):
    s3 = boto3.resource('s3')
    bucket = os.environ['S3_BUCKET_NAME']

    event_body = json.loads(event['body'])
    _id = event_body['id']
    report_type = event_body.get("type", "full")
    logging.info(f"Company UUID: {_id}")
    helpers.validate_user(event, _id)

    # Create pdf name
    connection = sql_functions.make_connection()
    name_query = ("SELECT ic.id, ic.name, ic.application_datetime "
                  "FROM public.company ic where ic.id = %s"
                  )
    query_fields = (_id,)
    name_data = sql_functions.retrieve_rows_safe(connection, name_query, query_fields)
    company_name = name_data[0][1]
    date = name_data[0][2].strftime("%d-%m-%Y")
    pdf_name = f"{company_name}_{date}.pdf"
    pdf_path = f"/tmp/{pdf_name}"

    logging.info("Generating PDF....")
    if report_type == "prelim":
        report = PrelimReport(_id, pdf_path)
    else:
        report = FullReport(_id, pdf_path)

    # Upload pdf to s3 bucket
    logging.info("Uploading PDF to S3....")
    s3.Bucket(bucket).upload_file(pdf_path, pdf_name)

    # Clear tmp storage in lambda
    call('rm -rf /tmp/*', shell=True)

    # Get download url for pdf
    logging.info("Retrieving URL to PDF....")
    s3_client = boto3.client('s3', region_name="ap-southeast-1",
                             config=boto3.session.Config(s3={'addressing_style': 'path'},
                                                         signature_version='s3v4', ))
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket,
                                                            'Key': pdf_name},
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
