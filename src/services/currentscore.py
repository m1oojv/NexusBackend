import json
import src.lib.sqlfunctions as sqlfunctions
import decimal
import collections

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal): return float(obj)

def handler(event, context):
    #body = {}
    #body["event"] = event
    print (event)
    event = json.loads(event['body'])
    print (event)
    business_unit = event['BusinessUnit']
    business_impact = event['BusinessImpact']
    connection = sqlfunctions.make_connection()
    #business_unit = 'Global Banking'
    #business_impact = 'Loss of funds'

    ## write string queries ##

    sql_stage = """select round(avg(tri_score_stage)::numeric,2) as score, nist_function, current_pi from group_scores_result_backup \
    where business_impact = '{bi}' \
    and business_unit ='{bu}' \
    group by nist_function, current_pi \
    order by  CASE nist_function \
    WHEN 'Identify' THEN 1 \
    WHEN 'Protect' THEN 2 \
    WHEN 'Detect' THEN 3 \
    WHEN 'Respond' THEN 4 \
    ELSE 5 END
    """.format(bu=business_unit, bi=business_impact)

    sql_current_score = """
    select round(sum(tri_stage)::numeric,2) from \
    (select avg(tri_score_stage) as tri_stage from group_scores_result_backup \
    where business_impact = '{bi}' \
    and business_unit = '{bu}' \
    and current_pi = 'current' \
    group by nist_function) as a
    """.format(bu=business_unit, bi=business_impact)

    sql_pi_score = """
    select round(sum(tri_stage)::numeric,2) from \
    (select avg(tri_score_stage) as tri_stage from group_scores_result_backup \
    where business_impact = '{bi}' \
    and business_unit = '{bu}' \
    and current_pi = 'pi' \
    group by nist_function) as a
    """.format(bu=business_unit, bi=business_impact)

    threatScenarioTitle = """
    select * from ts_id order by length(threat_scenario), threat_scenario
    """

    #select c.control_id, c.maturity, c.effectiveness_relevance, c.effectiveness_timeliness, c.effectiveness_adaptability, c.group_coverage from (select * from group_scores as b where b.control_id in (SELECT a.control_id FROM public.control_attributes as a WHERE a.org_control_family IN ('Asset Management')) and b.current_pi in ('current')) as c
    control_family = ["Asset Management", "Awareness & Training", "Change Management", "Cloud Security", "Communications", "Endpoint Security", "Identity Management", "Information Protection Processes and Procedures", "Improvements", "Mitigation", "Mobile Security", "Monitoring", "Network Security", "Personnel Security", "Physical & Environmental Security", "Privileged Access Management", "Recovery Planning", "Risk Assessment", "Risk Management Strategy", "Strategy & Policy", "System Security Engineering", "Threat Intelligence", "Third Party Risk Management", "Visibility", "Vulnerability Management"]
    ## two methods to make a connection and fetch the results ##

    ## this creates a pandas dataframe

    #df_stage = sqlfunctions.load_df(connection, sql_stage)

    ## this retrives rows from DB as a list
    response = [sqlfunctions.retrieve_rows(connection, sql_current_score), sqlfunctions.retrieve_rows(connection, sql_pi_score), sqlfunctions.retrieve_rows(connection, sql_stage), sqlfunctions.controlFamilyScore(connection, control_family), sqlfunctions.retrieve_rows(connection, threatScenarioTitle)]
    print(response[4])
    print(response)
    objects_list = []
    for row in response[4]:
        d = collections.OrderedDict()
        d['id'] = row[0]
        d['title'] = row[1]
        objects_list.append(d)
    response[4] = objects_list
    
    response = json.dumps(response, cls = Encoder)
    print (response)
    connection[1].close()
    connection[0].close()
    return {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': response,
    }

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration

def threatScenario(event, context):
    
    print (event)
    connection = sqlfunctions.make_connection()
    ## write string queries ##

    threatscenario = """
    select * from ts_id \
    order by threat_scenario    
    """
    ## this retrives rows from DB as a list
    response = sqlfunctions.retrieve_rows(connection, threatscenario)
    print (response)
    objects_list = []
    for row in response:
        d = collections.OrderedDict()
        d['id'] = row[0]
        d['threatScenario'] = row[1]
        objects_list.append(d)
    response = json.dumps(objects_list, cls = Encoder)
    print (response)
    connection[1].close()
    connection[0].close()
    return {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': response,
    }