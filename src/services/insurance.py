import json 
import src.lib.sqlfunctions as sqlfunctions
import src.lib.flareapi as flareapi
import src.lib.helpers as helpers
import decimal
import uuid
import boto3
import os
from datetime import datetime, timezone, date

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal): return float(obj)

class User:
    def __init__(self, event):
        self.user_id = event['requestContext']['authorizer']['jwt']['claims']['sub']

def companydetails(event, context):   
    event = json.loads(event['body'])
    connection = sqlfunctions.make_connection()

    ## write string queries ##
    companydetails_query = """
    SELECT ic.uuid, ic.company_name, ic.revenue, ic.industry, ic.country, ic.description, ic.assessment_progress, \
    ic.last_assessed, ic.employees, domain, ic.threat_completed, ic.scan_completed, ic.control_completed, ic.scan_results,\
    ic.pii, ic.pci, ic.phi FROM public.insured_companies ic where ic.uuid = %s 
    """

    financials_query = """
    SELECT uuid, risk, risk_m1, risk_m2, premium, limits, loss_exceedence, threat_category, return_period FROM public.insured_financials where uuid=%s 
    """

    assessment_query = """
    select ca.assessment_uuid, cfap.control_family,cfap.assessment_progress from control_assessment ca inner join control_family_assessment_progress cfap on ca.assessment_uuid = cfap.assessment_uuid where company_uuid = %s
    """

    query_fields = (event['id'],)
    ## this retrives rows from DB as a list
    financials_data = sqlfunctions.retrieve_rows_safe(connection, financials_query, query_fields)
    companydetails_data = sqlfunctions.retrieve_rows_safe(connection, companydetails_query, query_fields)
    assessment_data = sqlfunctions.retrieve_rows_safe(connection, assessment_query, query_fields)

    # parse data into dict
    financials_key = ('uuid', 'risk', 'riskM1', 'riskM2', 'premium', 'limit', 'lossExceedence', 'threatCategory', 'returnPeriod')
    financials_result = []
    for row in financials_data:
        financials_result.append(dict(zip(financials_key, row)))

    assessment_key = ('assessmentUuid', 'controlFamily', 'progress')
    assessment_result = []
    for row in assessment_data:
        assessment_result.append(dict(zip(assessment_key, row)))
    
    companydetails_result = []
    companydetails_key = ('id', 'companyName', 'revenue', 'industry', 'country', 'description', 'assessmentProgress', 'lastAssessed', 'employees', 'domain','threatAssessment', 'exposureAssessment', 'controlsAssessment', 'scanResults', 'pii', 'pci', 'phi')
    for row in companydetails_data:
        d = dict(zip(companydetails_key, row))
        d['financials'] = financials_result[0]
        d['assessment'] = assessment_result
        companydetails_result.append(d)

    response = json.dumps(companydetails_result, cls = Encoder)
    print (response)
    connection[1].close()
    connection[0].close()
    return {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': response,
    }

def insuredcompanies(event, context):
    user = User(event)
    connection = sqlfunctions.make_connection()
    ## write string queries ##

    companylist_query = """SELECT ic.uuid, ic.company_name, if2.risk, ic.industry, ic.country, if2.premium, if2.claims, ic.assessment_progress \
        FROM public.insured_companies as ic inner join insured_financials if2 on ic.uuid =  if2.uuid \
            where ic.user_id = %s order by ic.company_name"""
    ## this retrives rows from DB as a list
    companylist_data = sqlfunctions.retrieve_rows_safe(connection, companylist_query, (user.user_id,))
    
    companylist_key = ('id', 'companyName', 'risk', 'industry', 'country', 'premium', 'claims', 'assessmentProgress')
    companylist_result = []

    for row in companylist_data:
        companylist_result.append(dict(zip(companylist_key, row)))

    response = json.dumps(companylist_result, cls = Encoder)
    
    print (response)
    connection[1].close()
    connection[0].close()
    return {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': response,
    }

def insurancedashboard(event, context):
    connection = sqlfunctions.make_connection()
    ## write string queries ##

    financials_query = """SELECT sum (risk) as risk, sum(premium) as premiums, sum(claims) as claims FROM public.insured_financials as ifs \
        inner join insured_companies ic ON ifs.uuid = ic.uuid where ic.assessment_progress = 'COMPLETED'"""
    
    industry_query = """SELECT ic.industry, sum (if2.risk) as risk, sum(if2.premium) as premiums, \
        sum(if2.claims) as claims, sum (if2.risk_m1) as riskM1, sum (if2.risk_m2) as riskM2\
             FROM public.insured_financials as if2 inner join insured_companies ic on ic.uuid =  if2.uuid \
                 where ic.assessment_progress = 'COMPLETED' and if2.premium is not null group by ic.industry"""
    ## this retrives rows from DB as a list
    industry_data = sqlfunctions.retrieve_rows_safe(connection, industry_query, [])
    financials_data = sqlfunctions.retrieve_rows_safe(connection, financials_query, [])

    industry_key = ('industry', 'risk', 'premiums', 'claims', 'riskM1', 'riskM2')
    industry_result = []
    for row in industry_data:
        industry_result.append(dict(zip(industry_key, row)))

    financials_key = ('risk', 'premiums', 'claims')
    financials_result = []
    for row in financials_data:
        d = dict(zip(financials_key, row))
        d['industry'] = industry_result
        financials_result.append(d)

    response = json.dumps(financials_result, cls = Encoder)
    
    print (response)
    connection[1].close()
    connection[0].close()
    return {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': response,
    }

def addnewcompany(event, context):
    user = User(event)
    sqs = boto3.client('sqs', endpoint_url='https://sqs.ap-southeast-1.amazonaws.com')
    event = json.loads(event['body'])
    id = str(uuid.uuid4())
    connection = sqlfunctions.make_connection()
    ## write string queries ##
    add_company_query = """with first_insert as (insert into public.insured_companies \
        (user_id, uuid, company_name, revenue, industry, country, employees, domain, assessment_progress, threat_completed, scan_completed, control_completed, pii, pci, phi, estimated_controls, application_datetime) \
            values (%s, %s, %s, %s, %s, %s, %s, %s, 'NOT STARTED', 'IN PROGRESS', 'IN PROGRESS', 'NOT STARTED', %s, %s, %s, %s, current_timestamp) returning uuid) \
            insert into public.insured_financials (uuid) select uuid from first_insert"""
    add_company_fields = (user.user_id, id, event['companyName'], event['revenue'], event['industry'], event['countries'], event['employees'], event['domain'], event['records'], 0, 0, 'Yes')
    add_company = sqlfunctions.update_rows_safe(connection, add_company_query, add_company_fields)
    connection[1].close()
    connection[0].close()
    
    sqs.send_message(
        QueueUrl=os.environ['QUEUE_URL'],
        DelaySeconds=1,
        MessageBody=(json.dumps(
            {
                "uuid": id,
                "companyName": event['companyName'],
                "domain": event['domain'],
                "estimatedControls": 'Yes'
            }
        ))
    )
    print("success")
    
    response = json.dumps({'uuid': id}, cls = Encoder)

    return {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': response,
    }

def deletecompany(event, context):   
    #event = json.loads(event['body'])
    #event = json.loads(event)
    print (event)
    id = event['body']
    query_fields = (id.strip('"'),)
    print(query_fields)
    connection = sqlfunctions.make_connection()
    assessment_uuid_query = """
    select assessment_uuid from control_assessment where company_uuid = %s
    """
    flare_id_query = """
    select scan_results from insured_companies ic where uuid = %s
    """
    assessment_uuid = sqlfunctions.retrieve_rows_safe(connection, assessment_uuid_query, query_fields)
    try: 
        flare_id = sqlfunctions.retrieve_rows_safe(connection, flare_id_query, query_fields)
        print(flare_id)
        delete_identifier = flareapi.delete_identifier(flare_id[0][0]['asset']['asset']['id'])
        print(delete_identifier)
    except:
        pass
    #print(flare_id[0]['asset']['id'], type(flare_id))
    ## write string queries ##
    delete_threat_scenario = """
    delete from sc_ts_vendors where vendor = %s
    """
    delete_vendor_scores = """
    delete from sc_vendor_scores where uuid = %s
    """
    delete_control_assessment = """
    delete from control_assessment where company_uuid = %s
    """
    delete_control_assessment_family = """
    delete from control_family_assessment_progress where assessment_uuid = %s
    """
    delete_insured_companies = """
    delete from insured_companies where uuid = %s
    """
    delete_insured_financials = """
    delete from insured_financials where uuid = %s
    """
    ## this retrives rows from DB as a list
    
    results = [sqlfunctions.retrieve_rows_safe(connection, delete_threat_scenario, query_fields),
    sqlfunctions.retrieve_rows_safe(connection, delete_vendor_scores, query_fields),
    sqlfunctions.retrieve_rows_safe(connection, delete_control_assessment, query_fields),
    sqlfunctions.retrieve_rows_safe(connection, delete_control_assessment_family, assessment_uuid[0]),
    sqlfunctions.retrieve_rows_safe(connection, delete_insured_companies, query_fields),
    sqlfunctions.retrieve_rows_safe(connection, delete_insured_financials, query_fields)]
    print(results)

    connection[1].close()
    connection[0].close()
    response = True
    response = json.dumps(response, cls = Encoder)

    return {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': response,
    }

def calculatecompanyscores(event, context):   
    #event = json.loads(event['body'])
    #event = json.loads(event)
    print (event)
    id = event['id']
    print (id)
    connection = sqlfunctions.make_connection()

    ## write string queries ##

    company_scores_query = """
    SELECT score.uuid, score.control_id, score.existence, score.maturity, score.effectiveness_adaptability, score.effectiveness_relevance,\
        score.effectiveness_timeliness, score.group_coverage, ca.nist_function, a.threat_scenario FROM public.sc_ts_vendors as a \
            inner join ts_killchain_control_mapping as c \
                on a.threat_scenario = c.threat_scenario \
                    inner join sc_vendor_scores as score \
                        on a.vendor = score.uuid and c.control_id = score.control_id \
                            inner join control_attributes as ca \
                                on score.control_id = ca.control_id \
                                    where score.uuid = %s
    """
    ## this retrives rows from DB as a list
    query_fields = (event['id'],)
    score_results = sqlfunctions.retrieve_rows_safe(connection, company_scores_query, query_fields)
    print(score_results)
    sqlfunctions.updateVendorScore(connection, id, sqlfunctions.assessVendorScore(score_results))

    connection[1].close()
    connection[0].close()
    response = True
    response = json.dumps(response, cls = Encoder)

    return {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': response,
    }

def worker(event, context):   
    sfn_client = boto3.client('stepfunctions')
    state_machine_arn = 'arn:aws:states:ap-southeast-1:431837896730:stateMachine:RiskModel' #to make it configurable - reference to the state machine to run.
    connection = sqlfunctions.make_connection()
    data = json.loads(event['Records'][0]['body'])
    print(data)

    assessment_id = str(uuid.uuid4())
    current_date = date.today()
    print(assessment_id)
    #create the blank control assessments
    try:
        insert_control_assesssment_query = """
        insert into public.control_assessment (assessment_uuid, company_uuid, start_date) \
            values (%s, %s, %s)"""
        insert_control_assesssment_fields = (assessment_id, data['uuid'], current_date)
        print(insert_control_assesssment_query)
        sqlfunctions.update_rows_safe(connection, insert_control_assesssment_query, insert_control_assesssment_fields)
    except (ValueError, TypeError):
        return {
        'statusCode': 500,
        'headers': {'Content-Type': 'application/json'},
        }
    #if the estimated controls field is selected, only selected number of controls will be used
    try:
        if data['estimatedControls'] == 'Yes':
            create_blank_assessment_sme = """insert into public.sc_vendor_scores (control_id, assessment_uuid, uuid, existence) \
                select ca.control_id, assess.assessment_uuid, assess.company_uuid, 'Exists' as existence from controls_sme_estimated cse inner join control_attributes as ca on cse.control_id = ca.control_id \
                    cross join public.control_assessment as assess where assessment_uuid = %s
            """
            sqlfunctions.update_rows_safe(connection, create_blank_assessment_sme, (assessment_id,))
            
            create_blank_assessment_progress_sme = """insert into public.control_family_assessment_progress (assessment_uuid, control_family, assessment_progress) \
                SELECT DISTINCT assess.assessment_uuid, ca.org_control_family, 'NOT STARTED' as assessment_progress FROM sc_vendor_scores svs inner join control_attributes ca on svs.control_id = ca.control_id \
                    cross join public.control_assessment as assess where assess.assessment_uuid = %s and svs.uuid = %s order by ca.org_control_family asc
            """
            sqlfunctions.update_rows_safe(connection, create_blank_assessment_progress_sme, (assessment_id, data['uuid'],))
        #else the full control library will be used
        else:
            create_blank_assessment = """insert into public.sc_vendor_scores (control_id, assessment_uuid, uuid, existence) \
                SELECT ca.control_id, assess.assessment_uuid, assess.company_uuid, 'Exists' as existence FROM control_attributes as ca \
                    cross join public.control_assessment as assess where assessment_uuid = %s
            """
            sqlfunctions.update_rows_safe(connection, create_blank_assessment, (assessment_id,))

            create_blank_assessment_progress = """insert into public.control_family_assessment_progress (assessment_uuid, control_family, assessment_progress) \
                SELECT DISTINCT assess.assessment_uuid, ca.org_control_family, 'NOT STARTED' as assessment_progress FROM control_attributes ca \
                    cross join public.control_assessment as assess where assessment_uuid = %s
            """
            sqlfunctions.update_rows_safe(connection, create_blank_assessment_progress, (assessment_id,))
    except (ValueError, TypeError):
        return {
        'statusCode': 500,
        'headers': {'Content-Type': 'application/json'},
        }
    #identify relevant threat scenarios
    #check for industry
    select_company_threat_scenarios = """insert into sc_ts_vendors (vendor, threat_scenario) select ic.uuid, ti.threat_scenario from insured_companies ic\
            inner join ts_industry ti on ic.industry = ti.industry where ic.uuid = %s
    """
    sqlfunctions.update_rows_safe(connection, select_company_threat_scenarios, (data['uuid'],))
    
    #check for threat scenarios that apply to all industries
    select_company_threat_scenarios_all = """insert into sc_ts_vendors (vendor, threat_scenario)\
        select %s as uuid, ti.threat_scenario from ts_industry ti where ti.industry = 'All'
    """
    sqlfunctions.update_rows_safe(connection, select_company_threat_scenarios_all, (data['uuid'],))

    #conduct dark web scans
    scan_results = flareapi.add_flare_identifier(data['companyName'], data['domain'])
        
    update_scan_results = """
    update insured_companies set scan_results = %s, scan_completed = 'COMPLETED', threat_completed = 'COMPLETED', assessment_progress = 'IN PROGRESS' where uuid = %s
    """
    sqlfunctions.update_rows_safe(connection, update_scan_results, (json.dumps(scan_results, cls = Encoder), data['uuid']))

    risk_results = flareapi.evaluate_risk(scan_results) #obtain the results of the assessments of the dark web scans
    print(risk_results)
    if data['estimatedControls'] == 'Yes':
        #retrieve the controls to be estimated from database
        get_controls_query = """select control_id, scan_indicator from controls_sme_estimated cse"""
        controls = sqlfunctions.retrieve_rows_safe(connection, get_controls_query, ()) 
        print("controls", controls)

        #generate the controls scores based on the dark web scans
        controls_score = helpers.get_controls_scores(controls, risk_results, assessment_id)
        print(controls_score)

        #update the control scores based on scan results
        update_score_query = """update sc_vendor_scores set maturity = %(maturity)s, effectiveness_relevance = %(effectiveness_relevance)s, \
            effectiveness_timeliness = %(effectiveness_timeliness)s, effectiveness_adaptability = %(effectiveness_adaptability)s, \
                group_coverage = %(coverage)s where control_id = %(control_id)s and assessment_uuid = %(uuid)s"""
        update_score = sqlfunctions.update_rows_many(connection, update_score_query, controls_score) 

        #add the scores to sc_vendor_scores which is used to calculate resiliency
        company_scores_query = """
        SELECT score.uuid, score.control_id, score.existence, score.maturity, score.effectiveness_adaptability, score.effectiveness_relevance,\
            score.effectiveness_timeliness, score.group_coverage, ca.nist_function, a.threat_scenario FROM public.sc_ts_vendors as a \
                inner join ts_killchain_control_mapping as c \
                    on a.threat_scenario = c.threat_scenario \
                        inner join sc_vendor_scores as score \
                            on a.vendor = score.uuid and c.control_id = score.control_id \
                                inner join control_attributes as ca \
                                    on score.control_id = ca.control_id \
                                        where score.uuid = %s
        """
        score_results = sqlfunctions.retrieve_rows_safe(connection, company_scores_query, (data['uuid'],))
        print(score_results)
        sqlfunctions.updateVendorScore(connection, id, sqlfunctions.assessVendorScore(score_results))

        #trigger step function to run monte carlo simulation
        response = sfn_client.start_execution(
            stateMachineArn=state_machine_arn,
            name=str(data['uuid']),
            input=json.dumps({ 'uuid': data['uuid'] })
        )

    connection[1].close()
    connection[0].close()
    return {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    }