import json
import logging
from collections import OrderedDict
from decimal import Decimal

import src.lib.helpers.helpers as helpers
import src.lib.sqlfunctions as sql_functions

logging.getLogger().setLevel(logging.INFO)

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)

def index(event, context):
    """
    Retrieves threat scenarios related to a company.
    /web/api/v1/companies/{id}/threat-scenarios
    id is the company id that can be found in event["pathParameters"]
    """
    logging.info(f"event: {event}")
    event_params = event["pathParameters"]
    company_id = event_params["id"]

    helpers.validate_user(event, company_id)

    connection = sql_functions.make_connection()

    # Write string queries
    threat_scenario_query = """
    select ts.id, ts.title, ts.description from company_threat_scenario as cts\
    inner join threat_scenario as ts on cts.threat_scenario_id = ts.id\
    where cts.company_id = %s order by cts.threat_scenario_id
    """

    company_score_query = """
    select round(sum(tri_stage)::numeric,2) from (select avg(tri_score_stage) as tri_stage from score_result\
    where threat_scenario_id = %s and company_id = %s and existence = 'Exists' group by nist_function) as a
    """

    # This retrieves rows from DB as a list
    threat_scenario_query_fields = (company_id,)
    response = sql_functions.retrieve_rows_safe(connection, threat_scenario_query, threat_scenario_query_fields)

    logging.debug(f"Response: {response}")
    objects_list = []
    for row in response:
        d = OrderedDict()
        d['id'] = row[0]
        d['threatScenario'] = row[1]
        d['score'] = sql_functions.retrieve_rows_safe(connection, company_score_query, (row[0], company_id,))
        objects_list.append(d)
    response = json.dumps(objects_list, cls=Encoder)
    logging.debug(f"Response: {response}")
    connection[1].close()
    connection[0].close()

    return {'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': response,
            }

def show(event, context):
    """
    Retrieves one threat scenario with details related to a company.
    /web/api/v1/companies/{company_id}/threat-scenarios/{threat_scenario_id}
    id is the company id that can be found in event["pathParameters"]
    """
    logging.info(f"event: {event}")
    event_params = event["pathParameters"]
    company_id = event_params["company_id"]
    threat_scenario_id = event_params["threat_scenario_id"]

    helpers.validate_user(event, company_id)
    
    connection = sql_functions.make_connection()

    # Write string queries
    threat_scenario_title_query = """
    select id, title, description from threat_scenario where id='{threat_scenario_id}'
    """.format(threat_scenario_id=threat_scenario_id)

    threat_scenario_controls_query = """
    select b.control_id, b.nist_function, b.org_control_family, b.description from threat_scenario_control_attribute as a\
    inner join control_attribute as b on b.id = a.control_attribute_id where a.threat_scenario_id = '{threat_scenario_id}'
    """.format(threat_scenario_id=threat_scenario_id)

    threat_scenario_BUBI_query = """
    select distinct bi.threat_scenario_id, bi.name from business_impact bi where bi.threat_scenario_id = '{threat_scenario_id}'
    """.format(threat_scenario_id=threat_scenario_id)

    threat_vector_query = """
    select threat_scenario_id, name from vector where threat_scenario_id = '{threat_scenario_id}'
    """.format(threat_scenario_id=threat_scenario_id)

    threat_actor_query = """
    select threat_scenario_id, name from actor where threat_scenario_id = '{threat_scenario_id}'
    """.format(threat_scenario_id=threat_scenario_id)

    mitre_attack_query = """
    select tactics, id, name, description from mitre_attack_technique
    """

    techniques_query = """
    select a.threat_scenario_id, a.killchain_stage, mat.name, mat.technique_id from threat_scenario_mitre_attack_technique as a \
    inner join mitre_attack_technique mat on a.mitre_attack_technique_id = mat.id where a.threat_scenario_id = '{threat_scenario_id}'
    """.format(threat_scenario_id=threat_scenario_id)

    technique_control_mapping_query = """
    select mat.technique_id, a.control_attribute_id, b.nist_function, b.org_control_family, b.description from mitre_attack_technique_control_attribute as a\
    inner join mitre_attack_technique mat on a.mitre_attack_technique_id = mat.id\
    inner join control_attribute as b on b.id = a.control_attribute_id
    """

    company_score_query = """
    select round(sum(tri_stage)::numeric,2) from (select avg(tri_score_stage) as tri_stage from score_result\
    where threat_scenario_id = '{threat_scenario_id}' and company_id = '{company_id}' and existence = 'Exists' group by nist_function) as a
    """.format(threat_scenario_id=threat_scenario_id, company_id=company_id)

    company_details_query = """
    SELECT name FROM company where id = '{company_id}'
    """.format(company_id=company_id)

    nist_score_query = """
    select round(avg(tri_score_stage)::numeric,2) as score, nist_function from score_result \
    where company_id = '{company_id}' and threat_scenario_id = '{threat_scenario_id}' and existence = 'Exists' \
    group by nist_function order by CASE nist_function \
    WHEN 'Identify' THEN 1 WHEN 'Protect' THEN 2 WHEN 'Detect' THEN 3 WHEN 'Respond' THEN 4 ELSE 5 END
    """.format(threat_scenario_id=threat_scenario_id, company_id=company_id)

    control_families_query = """
    select b.org_control_family from threat_scenario_control_attribute as a \
    inner join control_attribute as b on b.id = a.control_attribute_id where a.threat_scenario_id = '{threat_scenario_id}'
    """.format(threat_scenario_id=threat_scenario_id)

    industry_query = """
    select name from industry where threat_scenario_id = '{threat_scenario_id}'
    """.format(threat_scenario_id=threat_scenario_id)

    families = sql_functions.retrieve_rows(connection, control_families_query)
    families = list(set(families))
    logging.debug(f"Families:\n{families}")

    # This retrieves rows from DB as a list
    response = [sql_functions.retrieve_rows(connection, threat_scenario_title_query),
                [],
                sql_functions.retrieve_rows(connection, threat_scenario_controls_query),
                sql_functions.retrieve_rows(connection, threat_scenario_BUBI_query),
                sql_functions.retrieve_rows(connection, threat_vector_query),
                sql_functions.retrieve_rows(connection, threat_actor_query),
                [],
                sql_functions.retrieve_rows(connection, mitre_attack_query),
                sql_functions.retrieve_rows(connection, techniques_query),
                sql_functions.retrieve_rows(connection, technique_control_mapping_query),
                sql_functions.retrieve_rows(connection, company_score_query),
                sql_functions.retrieve_rows(connection, company_details_query),
                sql_functions.retrieve_rows(connection, nist_score_query),
                [],
                sql_functions.retrieve_rows(connection, industry_query)]

    objects_list = []
    for row in response[0]:
        d = OrderedDict()
        d['id'] = row[0]
        d['title'] = row[1]
        d['description'] = row[2]
        objects_list.append(d)
    response[0] = objects_list

    objects_list = []
    for row in response[2]:
        d = OrderedDict()
        d['controlID'] = row[0]
        d['nistFunction'] = row[1]
        d['controlFamily'] = row[2]
        d['description'] = row[3]
        objects_list.append(d)
    response[2] = objects_list

    objects_list = []
    for row in response[3]:
        d = OrderedDict()
        d['threatScenario'] = row[0]
        d['businessImpact'] = row[1]
        objects_list.append(d)
    response[3] = objects_list

    objects_list = []
    for row in response[4]:
        d = OrderedDict()
        d['threatScenario'] = row[0]
        d['threatVector'] = row[1]
        objects_list.append(d)
    response[4] = objects_list

    objects_list = []
    for row in response[5]:
        d = OrderedDict()
        d['threatScenario'] = row[0]
        d['threatActor'] = row[1]
        objects_list.append(d)
    response[5] = objects_list

    objects_list = []
    for row in response[7]:
        d = OrderedDict()
        d['tactic'] = row[0]
        d['id'] = row[1]
        d['name'] = row[2]
        d['description'] = row[3]
        objects_list.append(d)
    response[7] = objects_list

    objects_list = []
    for row in response[8]:
        d = OrderedDict()
        d['threatScenario'] = row[0]
        d['killChainStage'] = row[1]
        d['technique'] = row[2]
        d['id'] = row[3]
        objects_list.append(d)
    response[8] = objects_list

    objects_list = []
    for row in response[9]:
        d = OrderedDict()
        d['techniqueID'] = row[0]
        d['controlID'] = row[1]
        d['nistFunction'] = row[2]
        d['controlFamily'] = row[3]
        d['description'] = row[4]
        objects_list.append(d)
    response[9] = objects_list

    objects_list = []
    for row in response[11]:
        d = OrderedDict()
        d['vendorName'] = row[0]
        objects_list.append(d)
    response[11] = objects_list

    objects_list = []
    for row in response[14]:
        d = OrderedDict()
        d['industry'] = row[0]
        objects_list.append(d)
    response[14] = objects_list

    response = json.dumps(response, cls=Encoder)
    connection[1].close()
    connection[0].close()

    return {'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': response,
            }

# def update(event, context):
#     event = json.loads(event['body'])
#     _id = event[0][0]['id']

#     logging.debug(f"Event:\n{event}")

#     connection = sql_functions.make_connection()
#     threats_helper.update_title(connection, _id, event[0])
#     threats_helper.update_business_details(connection, _id, event[3])
#     threats_helper.update_threat_vector(connection, _id, event[4])
#     threats_helper.update_threat_actor(connection, _id, event[5])
#     threats_helper.update_techniques(connection, _id, event[8])
#     threats_helper.update_controls(connection, _id, event[2])
#     threats_helper.update_industry(connection, _id, event[14])

#     score_query = """
#     select c.uuid, a.control_id, c.existence, c.maturity, c.effectiveness_adaptability, c.effectiveness_relevance, \
#     c.effectiveness_timeliness, c.group_coverage, b.nist_function, a.threat_scenario from ts_killchain_control_mapping as a \
#     inner join public.control_attributes as b on b.control_id = a.control_id \
#     inner join public.sc_vendor_scores as c on c.control_id = a.control_id \
#     inner join insured_companies as ic on c.uuid = ic.uuid \
#     where a.threat_scenario = '{id}' and ic.assessment_progress = 'COMPLETED' \
#     and ic.uuid in (select vendor from sc_ts_vendors stv where stv.threat_scenario = '{id}')
#     """.format(id=_id)

#     score_results = sql_functions.retrieve_rows(connection, score_query)
#     threats_helper.update_company_score(connection, _id, threats_helper.assess_company_score(score_results))

#     connection[1].close()
#     connection[0].close()
#     response = event
#     response = json.dumps(response, cls=Encoder)

#     return {'statusCode': 200,
#             'headers': {'Content-Type': 'application/json'},
#             'body': response,
#             }
