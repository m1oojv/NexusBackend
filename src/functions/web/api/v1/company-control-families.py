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
    Retrieves controls family scores of a company.
    /web/api/v1/companies/{id}/control-families
    id is the company id that can be found in event["pathParameters"]
    """
    logging.info(f"event: {event}")
    event_params = event["pathParameters"]
    company_id = event_params["id"]

    helpers.validate_user(event, company_id)

    connection = sql_functions.make_connection()
    # Write string queries
    control_family_query = """
    select distinct ca.org_control_family from score svs inner join control_attribute ca \
    on svs.control_attribute_id = ca.id where svs.company_id = %s order by ca.org_control_family asc
    """
    # control_family = ["Asset Management", "Awareness & Training", "Change Management", "Cloud Security", "Communications", "Endpoint Security", "Identity Management", "Information Protection Processes and Procedures", "Improvements", "Mitigation", "Mobile Security", "Monitoring", "Network Security", "Personnel Security", "Physical & Environmental Security", "Privileged Access Management", "Recovery Planning", "Risk Assessment", "Risk Management Strategy", "Strategy & Policy", "System Security Engineering", "Threat Intelligence", "Third Party Risk Management", "Visibility", "Vulnerability Management"]
    control_family = list(map(lambda x: helpers.list_to_string(x), sql_functions.retrieve_rows_safe(connection, control_family_query, (company_id,))))
    logging.debug(f"Control family: {control_family}")
    # This retrieves rows from DB as a list
    response = sql_functions.control_family_score(connection, control_family, company_id)
    logging.debug(f"Response:\n{response}")

    objects_list = []
    for row in response:
        d = OrderedDict()
        d['controlFamily'] = row[0]
        d['maturity'] = row[1]
        d['effectiveness'] = row[2]
        d['coverage'] = row[3]
        objects_list.append(d)
        
    response = json.dumps(objects_list, cls=Encoder)
    logging.debug(f"Response:\n{response}")
    connection[1].close()
    connection[0].close()
    return {'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': response,
            }


def show(event, context):
    """
    Retrieves control scores of one control family for a company.
    /web/api/v1/companies/{company_id}/control-families/{family_id}
    """
    logging.info(f"event: {event}")
    event_params = event["pathParameters"]
    company_id = event_params["company_id"]
    family_id = event_params["family_id"]

    connection = sql_functions.make_connection()

    # Write string queries
    company_control_family_details_query = """
    select a.control_id, a.description, a.org_control_family, b.maturity, b.effectiveness_adaptability, b.effectiveness_timeliness, \
    b.effectiveness_relevance, b.group_coverage from control_attribute as a inner join score as b on a.id = b.control_attribute_id \
    where a.org_control_family = '{family_id}' and b.company_id = '{company_id}' order by a.control_id
    """.format(family_id=family_id, company_id=company_id)

    # This retrieves rows from DB as a list
    response = sql_functions.retrieve_rows(connection, company_control_family_details_query)
    logging.debug(f"Response:\n{response}")
    objects_list = []
    for row in response:
        d = OrderedDict()
        d['controlID'] = row[0]
        d['description'] = row[1]
        d['controlFamily'] = row[2]
        d['maturity'] = row[3]
        d['effectivenessAdapt'] = row[4]
        d['effectivenessTimeliness'] = row[5]
        d['effectivenessRelevance'] = row[6]
        d['coverage'] = row[7]
        objects_list.append(d)
    response = objects_list

    response = json.dumps(response, cls=Encoder)
    logging.debug(f"Response:\n{response}")
    connection[1].close()
    connection[0].close()

    return {'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': response,
            }