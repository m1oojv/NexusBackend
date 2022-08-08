import json
import logging
from datetime import datetime, timezone
from decimal import Decimal

import src.lib.sqlfunctions as sql_functions
import src.lib.helpers.helpers as helpers

logging.getLogger().setLevel(logging.INFO)


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)

def index(event, context):
    """
    Retrieves controls assessment progress of a company by control family.
    /web/api/v1/companies/{company_id}/controls-assessments/{assessment_id}
    """
    logging.info(f"event: {event}")
    event_params = event["pathParameters"]
    company_id = event_params["company_id"]
    assessment_id = event_params["assessment_id"]
    
    helpers.validate_user(event, company_id)

    connection = sql_functions.make_connection()
    # Write string queries
    control_family_query = """
    select control_family, assessment_progress \
    from control_family_assessment_progress where control_assessment_id = %s order by control_family
    """
    control_family_query_fields = (assessment_id,)
    control_family_data = sql_functions.retrieve_rows_safe(connection, control_family_query, control_family_query_fields)

    control_family_key = ('controlFamily', 'assessmentProgress')
    control_family_result = []

    for row in control_family_data:
        control_family_result.append(dict(zip(control_family_key, row)))
    logging.debug(f"Control family result: {control_family_result}")

    company_details_query = """
    select ic.name, ca.company_id, ca.id from control_assessment ca \
    inner join company ic on ca.company_id = ic.id \
    where ca.id = %s
    """
    
    company_details_query_fields = (assessment_id,)
    company_details_data = sql_functions.retrieve_rows_safe(connection, company_details_query, company_details_query_fields)

    company_details_key = ('companyName', 'companyId', 'assessmentId')
    company_details_result = []

    for row in company_details_data:
        company_details_result.append(dict(zip(company_details_key, row)))
    company_details_result[0]['controlFamily'] = control_family_result
    
    logging.debug(f"Company details result: {company_details_result}")
    connection[1].close()
    connection[0].close()
    # print(assessment_scores_result)
    response = json.dumps(company_details_result, cls=Encoder)

    return {'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': response,
            }

def show(event, context):
    """
    Retrieves controls assessment scores of a company by control family.
    /web/api/v1/companies/{company_id}/controls-assessments/{assessment_id}/{family_id}
    """
    logging.info(f"event: {event}")
    event_params = event["pathParameters"]
    company_id = event_params["company_id"]
    assessment_id = event_params["assessment_id"]
    family_id = event_params["family_id"]

    helpers.validate_user(event, company_id)

    connection = sql_functions.make_connection()
    # Write string queries
    assessment_scores_query = """
    select ca.control_id, ca.nist_function, ca.org_control_family, ca.description, ca.maturity, \
    ca.effectiveness_relevance, ca.effectiveness_timeliness, ca.effectiveness_adaptability, ca.coverage, ca.source_framework, \
    ca.source_framework_code , svs.maturity, svs.effectiveness_adaptability, svs.effectiveness_timeliness, svs.effectiveness_relevance, svs.group_coverage \
    from score svs inner join control_attribute ca on svs.control_attribute_id = ca.id \
    where svs.control_assessment_id = %s and ca.org_control_family=%s order by ca.control_id
    """
    assessment_score_query_fields = (assessment_id, family_id)
    assessment_scores_data = sql_functions.retrieve_rows_safe(connection, assessment_scores_query, assessment_score_query_fields)

    assessment_scores_key = ('controlId', 'nistFunction', 'controlFamily', 'description', 'maturity', 'effectivenessAdaptability', 'effectivenessTimeliness', 'effectivenessRelevance', 'coverage', 'sourceFramework', 'sourceFrameworkCode', 'maturityScore', 'effectivenessAdaptabilityScore', 'effectivenessTimelinessScore', 'effectivenessRelevanceScore', 'coverageScore')
    assessment_scores_result = []
    for row in assessment_scores_data:
        assessment_scores_result.append(dict(zip(assessment_scores_key, row)))

    logging.debug(f"Assessment scores result: {assessment_scores_result}")
    connection[1].close()
    connection[0].close()
    # print(assessment_scores_result)
    response = json.dumps(assessment_scores_result, cls=Encoder)

    return {'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': response,
            }

def update(event, context):
    """
    Updates controls assessment scores of a company by control family.
    /web/api/v1/companies/{company_id}/controls-assessments/{assessment_id}/{family_id}
    request_body: 
    [{
        "uuid": "cf26758b-07eb-4783-92e1-522d5b77cd4b", 
        "controlId": "ORG.PR.VM-01",
        "maturityScore": 4,
        "effectivenessAdaptabilityScore": "Strong",
        "effectivenessTimelinessScore": "Strong",
        "effectivenessRelevanceScore": "Strong",
        "coverageScore": "0.8"
    }]
    """
    logging.info(f"event: {event}")
    event_params = event["pathParameters"]
    company_id = event_params["company_id"]
    assessment_id = event_params["assessment_id"]
    family_id = event_params["family_id"]

    helpers.validate_user(event, company_id)
    
    event_body = json.loads(event['body'])
    connection = sql_functions.make_connection()
    # Write string queries
    update_score_query = """
    update score set maturity = %(maturityScore)s, effectiveness_relevance = %(effectivenessRelevanceScore)s,
    effectiveness_timeliness = %(effectivenessTimelinessScore)s, effectiveness_adaptability = %(effectivenessAdaptabilityScore)s,
    group_coverage = %(coverageScore)s where control_attribute_id = %(controlId)s and control_assessment_id = %(uuid)s
    """

    update_score = sql_functions.update_rows_many(connection, update_score_query, event_body)

    update_control_family_query = """
    update control_family_assessment_progress set assessment_progress = 'COMPLETED', last_saved = %s\
    where control_assessment_id = %s and control_family = %s
    """
    
    update_control_family_fields = (datetime.now(timezone.utc), assessment_id, family_id)
    update_control_family = sql_functions.update_rows_safe(connection, update_control_family_query, update_control_family_fields)
    
    return {'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            }
