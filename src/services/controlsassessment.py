import json 
import src.lib.sqlfunctions as sqlfunctions
import decimal
from datetime import datetime, timezone

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal): return float(obj)

def controlassessment(event, context):
    event = json.loads(event['body'])
    print(event)
    connection = sqlfunctions.make_connection()
    ## write string queries ##
    assessment_scores_query = """select ca.control_id, ca.nist_function, ca.org_control_family, ca.description, ca.maturity, \
        ca.effectiveness_relevance, ca.effectiveness_timeliness, ca.effectiveness_adaptability, ca.coverage, ca.source_framework, \
            ca.source_framework_code , svs.maturity, svs.effectiveness_adaptability, svs.effectiveness_timeliness, svs.effectiveness_relevance, svs.group_coverage \
                from sc_vendor_scores svs inner join control_attributes ca on svs.control_id = ca.control_id \
                    where svs.assessment_uuid = %s and ca.org_control_family=%s order by svs.control_id"""
    assessment_score_query_fields = (event['uuid'], event['controlFamily'])
    assessment_scores_data = sqlfunctions.retrieve_rows_safe(connection, assessment_scores_query, assessment_score_query_fields)

    assessment_scores_key = ('controlId', 'nistFunction', 'controlFamily', 'description', 'maturity', 'effectivenessAdaptability', 'effectivenessTimeliness', 'effectivenessRelevance', 'coverage', 'sourceFramework', 'sourceFrameworkCode', 'maturityScore', 'effectivenessAdaptabilityScore', 'effectivenessTimelinessScore', 'effectivenessRelevanceScore', 'coverageScore')
    assessment_scores_result = []
    for row in assessment_scores_data:
        assessment_scores_result.append(dict(zip(assessment_scores_key, row)))

    print(assessment_scores_result)
    connection[1].close()
    connection[0].close()
    #print(assessment_scores_result)
    response = json.dumps(assessment_scores_result, cls = Encoder)

    return {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': response,
    }

def controlassessmentfamily(event, context):
    event = json.loads(event['body'])
    #event = event['body']
    connection = sqlfunctions.make_connection()
    ## write string queries ##
    control_family_query = """select control_family, assessment_progress \
        from control_family_assessment_progress where assessment_uuid = %s order by control_family"""
    control_family_query_fields = (event['uuid'],)
    control_family_data = sqlfunctions.retrieve_rows_safe(connection, control_family_query, control_family_query_fields)

    control_family_key = ('controlFamily', 'assessmentProgress')
    control_family_result = []

    for row in control_family_data:
        control_family_result.append(dict(zip(control_family_key, row)))
    print(control_family_result)

    company_details_query = """
    select ic.company_name, ca.company_uuid, ca.assessment_uuid from control_assessment ca\
            inner join insured_companies ic on ca.company_uuid = ic.uuid \
                where ca.assessment_uuid = %s"""
    company_details_query_fields = (event['uuid'],)
    company_details_data = sqlfunctions.retrieve_rows_safe(connection, company_details_query, company_details_query_fields)

    company_details_key = ('companyName', 'companyId', 'assessmentId')
    company_details_result = []

    for row in company_details_data:
        company_details_result.append(dict(zip(company_details_key, row)))
    company_details_result[0]['controlFamily'] = control_family_result
    
    print(company_details_result)
    connection[1].close()
    connection[0].close()
    #print(assessment_scores_result)
    response = json.dumps(company_details_result, cls = Encoder)

    return {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': response,
    }

def updatecontrolscore(event, context):
    event = json.loads(event['body'])
    print(event)
    connection = sqlfunctions.make_connection()
    ## write string queries ##
    update_score_query = """update sc_vendor_scores set maturity = %(maturityScore)s, effectiveness_relevance = %(effectivenessRelevanceScore)s, \
        effectiveness_timeliness = %(effectivenessTimelinessScore)s, effectiveness_adaptability = %(effectivenessAdaptabilityScore)s, \
            group_coverage = %(coverageScore)s where control_id = %(controlId)s and assessment_uuid = %(uuid)s"""
    update_score = sqlfunctions.update_rows_many(connection, update_score_query, event)

    update_control_family_query = """update control_family_assessment_progress set assessment_progress = 'COMPLETED', last_saved = %s\
        where assessment_uuid = %s and control_family = %s"""
    
    update_control_family_fields = (datetime.now(timezone.utc), event[0]['uuid'], event[0]['controlFamily'])
    update_control_family = sqlfunctions.update_rows_safe(connection, update_control_family_query, update_control_family_fields)
    
    return {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    }