import boto3
import json
import logging
import os
import uuid
from datetime import date
from decimal import Decimal

import src.lib.helpers.helpers as helpers
import src.lib.sqlfunctions as sql_functions
from src.lib.scanners.scan_domain import scan_domain
from src.lib.helpers.json_response import list_objects, success
from src.lib.errors.errors_handler import exception_response
import src.services.control_assessment_service as ControlAssessmentService
import src.services.control_family_assessment_progress_service as ControlFamilyAssessmentProgress
import src.services.company_service as CompanyService
import src.services.score_service as ScoreService
import src.services.score_result_service as ScoreResultService
import src.services.industry_service as IndustryService
import src.services.control_sme_service as ControlSmeEstimatedService
import src.services.company_threat_scenario_service as CompanyThreatScenarioService


logging.getLogger().setLevel(logging.INFO)

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)

def handler(event, context):
    """
    Used in a SQS which is called by the `add_new_company`. Runs the intel gathering on the
    company domain. Then calls the risk model step function to run the risk model on the gathered
    data.
    Event['Records'][0]['body']: { "company_id": "<company UUID>", "name": "<company name>",
                                   "domain": "<domain>", "estimated_controls": "<Yes|No>", "user_id": <user_id> }
    """
    try:
        #uncomment for production
        sfn_client = boto3.client('stepfunctions')
        state_machine_arn = os.environ["STATE_MACHINE_ARN"]
        logging.info(f"State machine ARN: {state_machine_arn}")
        params = json.loads(event['Records'][0]['body'])

        #uncomment for dev
        #params = json.loads(event['body'])

        company_id = params['company_id']
        user_id = params['user_id']

        company = CompanyService.find(**params, id=company_id, joinedload=False)

        logging.info("Creating new control assessment")
        control_assessment = ControlAssessmentService.create(create_control_assessment_params(params))

        #Identify controls for estimated controls and create new blank score and control family assessment progress
        if params['estimated_controls'] == 'Yes':
            logging.info("Creating new score and control family assessment progress")
            params['control_assessment'] = control_assessment
            score = ScoreService.create_sme_control(**params)
            control_family_assessment_progress = ControlFamilyAssessmentProgress.create_sme_control(**params)
        
        #Identify threat scenario and create entries into company threat scenario
        logging.info("Identifying relevant threat scenarios for company")
        industry = IndustryService.find(industry=company.industry, select_all=True)
        threat_scenario_dict = [{'threat_scenario_id':str(row.__dict__['threat_scenario_id'])} for row in industry]
        CompanyThreatScenarioService.create_sme(company_id=company_id, threat_scenarios=threat_scenario_dict)
    
        logging.info("Scanning domain....")
        #uncomment for dev
        #f = open(os.path.join('db', 'envipure.json'))
        #scan_results = json.load(f)
        scan_results = scan_domain(params['name'], params['domain'])
        logging.debug(f"Scan results:\n{scan_results}")
        logging.info("Scanning domain done.")

        #updating company table with the latest scan results
        CompanyService.update_record(id=company_id, user_id=user_id, body=update_params(scan_results=scan_results))

        #evaluate the risk levels based on the scan results
        risk_results = scan_results["risk_results"]
        logging.debug(f"Evaluated Risk: {risk_results}")

        #create control scores based on scan results and update the score and score_result tables with values
        if params['estimated_controls'] == 'Yes':
            controls = ControlSmeEstimatedService.all()
            controls_dict = [{"control_attribute_id":row.control_attribute_id, "scan_indicator": row.scan_indicator} for row in controls]
            controls_score = helpers.get_controls_scores(controls_dict, risk_results, str(control_assessment.id))
            logging.debug(f"Control score:\n{controls_score}")

            ScoreService.update_many_record(company_id=company_id, control_assessment_id=str(control_assessment.id), body=controls_score)
            score_result = ScoreService.get_score_result_params(company_id=company_id, control_assessment_id=str(control_assessment.id))
            ScoreResultService.create_record(
                company_id=company_id,
                control_assessment_id=str(control_assessment.id), 
                body=ScoreResultService.assess_company_score(score_result))
            
        # Trigger step function to run monte carlo simulation
        logging.info("Triggering step function to run risk model....")
        #uncomment for production
        sfn_client.start_execution(stateMachineArn=state_machine_arn,
                                name=str(company_id),
                                input=json.dumps({'uuid': company_id})
                                )

        return success()
    except Exception as e:
        logging.info("Deleting company due to exception")
        CompanyService.delete_record(id=company.id, user_id=user_id)
        logging.info("Deleted company")
        return exception_response(e)

def update_params(*args, **kwargs):
    return({
        "scan_results": kwargs['scan_results'],
        "threat_assessment_status": 'COMPLETED',
        "assessment_progress": 'IN PROGRESS',
        "scan_status": 'COMPLETED'
    })

def create_control_assessment_params(params):
    return {
    "company_id": params['company_id']
    }

def create_score_sme_control_params(control_assessment, sme_control):
    for control in sme_control:
        params = {
            "company_id": params['company_id']
        }
    return params

def old_handler(event, context):
    """
    Used in a SQS which is called by the `add_new_company` above. Runs the intel gathering on the
    company domain. Then calls the risk model step function to run the risk model on the gathered
    data.
    Event['Records'][0]['body']: { "company_id": "<company UUID>", "name": "<company name>",
                                   "domain": "<domain>", "estimated_controls": "<Yes|No>" }
    """
    sfn_client = boto3.client('stepfunctions')
    state_machine_arn = os.environ["STATE_MACHINE_ARN"]
    logging.info(f"State machine ARN: {state_machine_arn}")
    connection = sql_functions.make_connection()
    data = json.loads(event['Records'][0]['body'])
    logging.debug(f"Data:\n{data}")

    assessment_id = str(uuid.uuid4())
    current_date = date.today()
    logging.info(f"Assessment ID: {assessment_id}")

    # Create the blank control assessments
    try:
        insert_control_assessment_query = """
        insert into control_assessment (id, company_id, start_date) \
        values (%s, %s, %s)"""
        insert_control_assessment_fields = (assessment_id, data['company_id'], current_date)
        sql_functions.update_rows_safe(connection, insert_control_assessment_query, insert_control_assessment_fields)
    except (ValueError, TypeError) as e:
        logging.error(e)
        return {'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                }
    # If the estimated controls field is selected, only selected number of controls will be used
    try:
        if data['estimated_controls'] == 'Yes':
            create_blank_assessment_sme_query = """insert into score (id, control_attribute_id, control_assessment_id, company_id, existence) \
            select gen_random_uuid() as id, ca.id as control_attribute_id, assess.id as control_assessment_id, assess.company_id, 'Exists' as existence from \
            control_sme_estimated cse inner join control_attribute as ca on cse.control_attribute_id = ca.id \
            cross join control_assessment as assess where assess.id =%s
            """
            sql_functions.update_rows_safe(connection, create_blank_assessment_sme_query, (assessment_id,))
            
            create_blank_assessment_progress_sme_query = """insert into public.control_family_assessment_progress (id, control_assessment_id, control_family, assessment_progress) \
            select gen_random_uuid() as id, * from (select distinct assess.id, ca.org_control_family, 'COMPLETED' as assessment_progress FROM score svs inner join control_attribute ca on svs.control_attribute_id = ca.id \
            cross join control_assessment as assess where assess.id = %s and svs.company_id = %s order by ca.org_control_family asc) as family
            """
            sql_functions.update_rows_safe(connection, create_blank_assessment_progress_sme_query, (assessment_id, data['company_id'],))
        # Else the full control library will be used
        else:
            create_blank_assessment_query = """insert into public.sc_vendor_scores (control_id, assessment_uuid, uuid, existence) \
                SELECT ca.control_id, assess.assessment_uuid, assess.company_uuid, 'Exists' as existence FROM control_attributes as ca \
                    cross join public.control_assessment as assess where assessment_uuid = %s
            """
            sql_functions.update_rows_safe(connection, create_blank_assessment_query, (assessment_id,))

            create_blank_assessment_progress_query = """insert into public.control_family_assessment_progress (assessment_uuid, control_family, assessment_progress) \
                SELECT DISTINCT assess.assessment_uuid, ca.org_control_family, 'NOT STARTED' as assessment_progress FROM control_attributes ca \
                    cross join public.control_assessment as assess where assessment_uuid = %s
            """
            sql_functions.update_rows_safe(connection, create_blank_assessment_progress_query, (assessment_id,))
    except (ValueError, TypeError) as e:
        logging.error(e)
        return {'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                }
    # Identify relevant threat scenarios
    # Check for industry
    select_company_threat_scenarios_query = """insert into company_threat_scenario  (id, company_id, threat_scenario_id) \
    select gen_random_uuid() as id, ic.id, ti.threat_scenario_id from company ic \
    inner join industry ti on ic.industry = ti.name where ic.id = %s
    """
    sql_functions.update_rows_safe(connection, select_company_threat_scenarios_query, (data['company_id'],))
    
    # Check for threat scenarios that apply to all industries
    select_company_threat_scenarios_all_query = """insert into company_threat_scenario  (id, company_id, threat_scenario_id) \
    select gen_random_uuid() as id, %s as company_id, ti.threat_scenario_id from industry ti where ti.name = 'All'
    """
    sql_functions.update_rows_safe(connection, select_company_threat_scenarios_all_query, (data['company_id'],))

    # Conduct dark web scans
    logging.info("Scanning domain....")
    scan_results = scan_domain(data['name'], data['domain'])
    logging.debug(f"Scan results:\n{scan_results}")
    logging.info("Scanning domain done.")
        
    update_scan_results_query = """
    update company set scan_results = %s, scan_status = 'COMPLETED', threat_assessment_status = 'COMPLETED', \
    assessment_progress = 'IN PROGRESS' where id = %s
    """
    sql_functions.update_rows_safe(connection, update_scan_results_query, (json.dumps(scan_results, cls=Encoder), data['company_id']))

    risk_results = scan_results["risk_results"]
    logging.debug(f"Evaluated Risk: {risk_results}")

    #if estimated controls functionality is used, the control scores will be updated based on the scan results
    if data['estimated_controls'] == 'Yes':
        # Retrieve the controls to be estimated from database
        get_controls_query = """select control_attribute_id, scan_indicator from control_sme_estimated cse"""
        controls = sql_functions.retrieve_rows_safe(connection, get_controls_query, ())
        logging.debug(f"Controls:\n{controls}")

        # Generate the controls scores based on the dark web scans
        controls_score = helpers.get_controls_scores(controls, risk_results, assessment_id)
        logging.debug(f"Control score:\n{controls_score}")

        # Update the control scores based on scan results
        update_score_query = """update score set maturity = %(maturity)s, effectiveness_relevance = %(effectiveness_relevance)s, \
        effectiveness_timeliness = %(effectiveness_timeliness)s, effectiveness_adaptability = %(effectiveness_adaptability)s, \
        group_coverage = %(coverage)s where control_attribute_id = %(control_id)s and control_assessment_id = %(uuid)s"""
        update_score = sql_functions.update_rows_many(connection, update_score_query, controls_score)

        # Add the scores to sc_vendor_scores which is used to calculate resiliency
        company_scores_query = """
        select score.company_id, score.control_attribute_id, score.existence, score.maturity, score.effectiveness_adaptability, score.effectiveness_relevance, \
        score.effectiveness_timeliness, score.group_coverage, ca.nist_function, a.threat_scenario_id FROM company_threat_scenario as a \
        inner join threat_scenario_control_attribute as c on a.threat_scenario_id = c.threat_scenario_id \
        inner join score as score on a.company_id = score.company_id and c.control_attribute_id = score.control_attribute_id \
        inner join control_attribute as ca on score.control_attribute_id = ca.id where score.company_id  = %s
        """
        score_results = sql_functions.retrieve_rows_safe(connection, company_scores_query, (data['company_id'],))
        logging.debug(f"Score results:\n{score_results}")

        sql_functions.update_company_score(connection, str(data['company_id']), sql_functions.assess_company_score(score_results))

        # Trigger step function to run monte carlo simulation
        logging.info("Triggering step function to run risk model....")
        sfn_client.start_execution(stateMachineArn=state_machine_arn,
                                   name=str(data['company_id']),
                                   input=json.dumps({'uuid': data['company_id']})
                                   )

    connection[1].close()
    connection[0].close()

    return {'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            }
