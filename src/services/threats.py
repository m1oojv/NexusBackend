import json
import src.lib.sqlfunctions as sqlfunctions
import src.lib.threatshelper as threatshelper
import decimal
import collections

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal): return float(obj)

def threatscenariodetails(event, context):   
    event = json.loads(event['body'])
    print(event)
    vendor = event['vendor']
    id = event['id']
    connection = sqlfunctions.make_connection()

    ## write string queries ##

    threatScenarioTitle = """
    select threat_scenario, threat_scenario_title, description from ts_id where threat_scenario='{id}'    
    """.format(id=id)

    threatScenarioKillChain = """
    select * from ts_killchain_event where threat_scenario='{id}'   
    """.format(id=id)

    threatScenarioControls = """
    select a.killchain_stage, a.control_id, b.nist_function, b.org_control_family, b.description from public.ts_killchain_control_mapping as a inner join control_attributes as b on b.control_id = a.control_id where a.threat_scenario = '{id}'
    """.format(id=id)

    threatScenarioBUBI = """
    select * from public.ts_bi_bu_mapping where threat_scenario = '{id}'
    """.format(id=id)

    threatVector = """
    select * from public.ts_vector_mapping where threat_scenario = '{id}'
    """.format(id=id)

    threatActor = """
    select * from public.ts_actor_mapping where threat_scenario = '{id}'
    """.format(id=id)

    threatAssets = """
    select * from public.ts_assets_systems_mapping where threat_scenario = '{id}'
    """.format(id=id)

    mitreAttack = """
    select tactics, id, name, description from public.mitre_attack_techniques
    """

    techniques = """
    select a.threat_scenario, a.killchain_stage, a.technique, a.technique_id from ts_killchain_techniques as a where a.threat_scenario = '{id}'
    """.format(id=id)

    techniqueControlMapping = """
    select a.technique_id, a.control_id, b.nist_function, b.org_control_family, b.description from public.ts_technique_control as a inner join control_attributes as b on b.control_id = a.control_id
    """

    companyScore = """
    select round(sum(tri_stage)::numeric,2) from (select avg(tri_score_stage) as tri_stage from sc_scores_result \
        where threat_scenario = '{id}' and uuid = '{vendor}' and existence = 'Exists' group by nist_function) as a
    """.format(id=id, vendor=vendor)

    companyDetails = """
    SELECT company_name FROM insured_companies where uuid = '{vendor}'
    """.format(vendor=vendor)

    nistScore = """
    select round(avg(tri_score_stage)::numeric,2) as score, nist_function from sc_scores_result \
        where threat_scenario = '{id}' and uuid = '{vendor}' and existence = 'Exists' \
            group by nist_function order by CASE nist_function \
                WHEN 'Identify' THEN 1 WHEN 'Protect' THEN 2 WHEN 'Detect' THEN 3 WHEN 'Respond' THEN 4 ELSE 5 END
    """.format(id=id, vendor=vendor)

    controlFamilies = """
    select b.org_control_family from ts_killchain_control_mapping as a inner join public.control_attributes as b on b.control_id = a.control_id where a.threat_scenario = '{id}'
    """.format(id=id)

    industry = """
    select industry from public.ts_industry where threat_scenario = '{id}'
    """.format(id=id)
    
    families = sqlfunctions.retrieve_rows(connection, controlFamilies)
    print(families)
    families = set(families)
    families = list(families)
    print(families)

    ## this retrives rows from DB as a list
    response = [sqlfunctions.retrieve_rows(connection, threatScenarioTitle), \
        sqlfunctions.retrieve_rows(connection, threatScenarioKillChain), \
        sqlfunctions.retrieve_rows(connection, threatScenarioControls), \
        sqlfunctions.retrieve_rows(connection, threatScenarioBUBI),\
        sqlfunctions.retrieve_rows(connection, threatVector),\
        sqlfunctions.retrieve_rows(connection, threatActor),\
        sqlfunctions.retrieve_rows(connection, threatAssets),\
        sqlfunctions.retrieve_rows(connection, mitreAttack),
        sqlfunctions.retrieve_rows(connection, techniques),
        sqlfunctions.retrieve_rows(connection, techniqueControlMapping),
        sqlfunctions.retrieve_rows(connection, companyScore),
        sqlfunctions.retrieve_rows(connection, companyDetails),
        sqlfunctions.retrieve_rows(connection, nistScore),
        [],
        sqlfunctions.retrieve_rows(connection, industry)]

    objects_list = []
    for row in response[0]:
        d = collections.OrderedDict()
        d['id'] = row[0]
        d['title'] = row[1]
        d['description'] = row[2]
        objects_list.append(d)
    response[0] = objects_list

    objects_list = []
    for row in response[1]:
        d = collections.OrderedDict()
        d['threatScenario'] = row[0]
        d['killChainStage'] = row[1]
        d['threatEventDescription'] = row[2]
        objects_list.append(d)
    response[1] = objects_list

    objects_list = []
    for row in response[2]:
        d = collections.OrderedDict()
        d['killChainStage'] = row[0]
        d['controlID'] = row[1]
        d['nistFunction'] = row[2]
        d['controlFamily'] = row[3]
        d['description'] = row[4]
        objects_list.append(d)
    response[2] = objects_list

    objects_list = []
    for row in response[3]:
        d = collections.OrderedDict()
        d['threatScenario'] = row[0]
        d['businessImpact'] = row[1]
        d['businessUnit'] = row[2]
        objects_list.append(d)
    response[3] = objects_list

    objects_list = []
    for row in response[4]:
        d = collections.OrderedDict()
        d['threatScenario'] = row[0]
        d['threatVector'] = row[1]
        objects_list.append(d)
    response[4] = objects_list

    objects_list = []
    for row in response[5]:
        d = collections.OrderedDict()
        d['threatScenario'] = row[0]
        d['threatActor'] = row[1]
        objects_list.append(d)
    response[5] = objects_list

    objects_list = []
    for row in response[6]:
        d = collections.OrderedDict()
        d['threatScenario'] = row[0]
        d['informationAsset'] = row[1]
        d['informationSystem'] = row[2]
        d['confidentiality'] = row[3]
        d['integrity'] = row[4]
        d['availability'] = row[5]
        objects_list.append(d)
    response[6] = objects_list

    objects_list = []
    for row in response[7]:
        d = collections.OrderedDict()
        d['tactic'] = row[0]
        d['id'] = row[1]
        d['name'] = row[2]
        d['description'] = row[3]
        objects_list.append(d)
    response[7] = objects_list

    objects_list = []
    for row in response[8]:
        d = collections.OrderedDict()
        d['threatScenario'] = row[0]
        d['killChainStage'] = row[1]
        d['technique'] = row[2]
        d['id'] = row[3]
        objects_list.append(d)
    response[8] = objects_list

    objects_list = []
    for row in response[9]:
        d = collections.OrderedDict()
        d['techniqueID'] = row[0]
        d['controlID'] = row[1]
        d['nistFunction'] = row[2]
        d['controlFamily'] = row[3]
        d['description'] = row[4]
        objects_list.append(d)
    response[9] = objects_list

    objects_list = []
    for row in response[11]:
        d = collections.OrderedDict()
        d['vendorName'] = row[0]
        objects_list.append(d)
    response[11] = objects_list

    objects_list = []
    for row in response[14]:
        d = collections.OrderedDict()
        d['industry'] = row[0]
        objects_list.append(d)
    response[14] = objects_list

    response = json.dumps(response, cls = Encoder)
    connection[1].close()
    connection[0].close()

    return {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': response,
    }

def threatscenario(event, context):
    event = json.loads(event['body'])
    print (event)
    vendor = event['vendor']
    connection = sqlfunctions.make_connection()
    ## write string queries ##

    threatscenario = """
    select ts.threat_scenario, ts.threat_scenario_title, ts.description from sc_ts_vendors as vendor \
        inner join ts_id as ts on vendor.threat_scenario = ts.threat_scenario \
            where vendor.vendor = '{vendor}' \
                order by threat_scenario
    """.format(vendor=vendor)

    def companyScore(threat_scenario):
        return (
            """
            select round(sum(tri_stage)::numeric,2) from (select avg(tri_score_stage) as tri_stage from sc_scores_result \
                where threat_scenario = '{threat_scenario}' and uuid = '{vendor}' and existence = 'Exists' group by nist_function) as a
            """.format(threat_scenario=threat_scenario, vendor=vendor)
        )

    ## this retrives rows from DB as a list
    response = sqlfunctions.retrieve_rows(connection, threatscenario)
    print (response)
    objects_list = []
    for row in response:
        d = collections.OrderedDict()
        d['id'] = row[0]
        d['threatScenario'] = row[1]
        d['score'] = sqlfunctions.retrieve_rows(connection, companyScore(row[0]))
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

def updatethreatscenario(event, context):   
    event = json.loads(event['body'])
    id = event[0][0]['id']

    print (event)
    connection = sqlfunctions.make_connection()
    threatshelper.update_title(connection, id, event[0])
    threatshelper.update_business_details(connection, id, event[3])
    threatshelper.update_threat_vector(connection, id, event[4])
    threatshelper.update_threat_actor(connection, id, event[5])
    threatshelper.update_techniques(connection, id, event[8])
    threatshelper.update_controls(connection, id, event[2])
    threatshelper.update_industry(connection, id, event[14])

    score = """
    select c.uuid, a.control_id, c.existence, c.maturity, c.effectiveness_adaptability, c.effectiveness_relevance, \
    c.effectiveness_timeliness, c.group_coverage, b.nist_function, a.threat_scenario from ts_killchain_control_mapping as a \
    inner join public.control_attributes as b on b.control_id = a.control_id \
    inner join public.sc_vendor_scores as c on c.control_id = a.control_id \
    inner join insured_companies as ic on c.uuid = ic.uuid \
    where a.threat_scenario = '{id}' and ic.assessment_progress = 'COMPLETED' \
    and ic.uuid in (select vendor from sc_ts_vendors stv where stv.threat_scenario = '{id}')
    """.format(id=id)
    
    score_results = sqlfunctions.retrieve_rows(connection, score)
    threatshelper.update_company_score(connection, id, threatshelper.assess_company_score(score_results))

    connection[1].close()
    connection[0].close()
    response = event
    response = json.dumps(response, cls = Encoder)

    return {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': response,
    }