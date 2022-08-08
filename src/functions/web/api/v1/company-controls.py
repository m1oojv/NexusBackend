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

def show(event, context):
    """
    Retrieves details of a single control for a company.
    /web/api/v1/companies/{company_id}/controls/{control_id}
    """
    logging.info(f"event: {event}")
    event_params = event["pathParameters"]
    company_id = event_params["company_id"]
    control_id = event_params["control_id"]
    helpers.validate_user(event, company_id)
    
    connection = sql_functions.make_connection()

    # Write string queries
    company_control_details_query = """
    select a.control_id, a.nist_function, a.org_control_family, a.description, a.org_statement_type, a.enterprise_bu, a.org_control_domain, a.source_framework_code,\
    a.source_framework, a.maturity, a.effectiveness_relevance, a.effectiveness_timeliness, a.effectiveness_adaptability, a.coverage, b.maturity, b.effectiveness_adaptability,\
    b.effectiveness_timeliness, b.effectiveness_relevance, b.group_coverage, b.company_id from control_attribute as a inner join score as b on a.id = b.control_attribute_id\
    where a.control_id = '{control_id}' and b.company_id = '{company_id}'
    """.format(control_id=control_id, company_id=company_id)

    # This retrieves rows from DB as a list
    response = sql_functions.retrieve_rows(connection, company_control_details_query)
    logging.debug(f"Response:\n{response}")
    objects_list = []
    for row in response:
        d = OrderedDict()
        d['controlID'] = row[0]
        d['nistFunction'] = row[1]
        d['controlFamily'] = row[2]
        d['description'] = row[3]
        d['orgStatementType'] = row[4]
        d['enterpriseBU'] = row[5]
        d['controlDomain'] = row[6]
        d['sourceFrameworkCode'] = row[7]
        d['sourceFramework'] = row[8]
        d['maturity'] = row[9]
        d['effectivenessRelevance'] = row[10]
        d['effectivenessTimeliness'] = row[11]
        d['effectivenessAdaptability'] = row[12]
        d['coverage'] = row[13]
        d['maturityScore'] = row[14]
        d['effectivenessAdaptabilityScore'] = row[15]
        d['effectivenessTimelinessScore'] = row[16]
        d['effectivenessRelevanceScore'] = row[17]
        d['coverageScore'] = row[18]
        d['vendoruuid'] = row[19]
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
