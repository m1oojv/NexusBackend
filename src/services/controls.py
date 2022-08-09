import json
import src.lib.sqlfunctions as sqlfunctions
import src.lib.helpers as helpers
import decimal
import collections

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal): return float(obj)

#to create the tables based on the vendor control scores
def companycontrolfamilies(event, context):
    event = json.loads(event['body'])
    print (event)
    uuid = event['uuid']
    print (uuid)
    connection = sqlfunctions.make_connection()
    ## write string queries ##
    control_family_query = """
    select distinct ca.org_control_family from sc_vendor_scores svs inner join control_attributes ca on svs.control_id = ca.control_id where svs.uuid = %s order by ca.org_control_family asc
    """
    #control_family = ["Asset Management", "Awareness & Training", "Change Management", "Cloud Security", "Communications", "Endpoint Security", "Identity Management", "Information Protection Processes and Procedures", "Improvements", "Mitigation", "Mobile Security", "Monitoring", "Network Security", "Personnel Security", "Physical & Environmental Security", "Privileged Access Management", "Recovery Planning", "Risk Assessment", "Risk Management Strategy", "Strategy & Policy", "System Security Engineering", "Threat Intelligence", "Third Party Risk Management", "Visibility", "Vulnerability Management"]
    control_family = list(map(lambda x: helpers.listToString(x) , sqlfunctions.retrieve_rows_safe(connection, control_family_query, (uuid,))))
    print(control_family)
    ## this retrives rows from DB as a list
    response = sqlfunctions.ControlFamilyScore(connection, control_family, uuid)
    print (response)

    objects_list = []
    for row in response:
        d = collections.OrderedDict()
        d['controlFamily'] = row[0]
        d['maturity'] = row[1]
        d['effectiveness'] = row[2]
        d['coverage'] = row[3]
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

def companycontrolfamilydetails(event, context):   
    event = json.loads(event['body'])
    print (event)
    id = event['id']
    vendor = event['vendor']
    print (id)
    connection = sqlfunctions.make_connection()

    ## write string queries ##

    companyControlFamilyDetails = """
    select a.control_id, a.description, a.org_control_family, b.maturity, b.effectiveness_adaptability, b.effectiveness_timeliness, b.effectiveness_relevance, b.group_coverage from \
    control_attributes as a inner join sc_vendor_scores as b on a.control_id = b.control_id where a.org_control_family = '{id}' and b.uuid = '{vendor}' order by a.control_id
    """.format(id=id, vendor=vendor)

    ## this retrives rows from DB as a list
    response = sqlfunctions.retrieve_rows(connection, companyControlFamilyDetails)
    print(response)
    objects_list = []
    for row in response:
        d = collections.OrderedDict()
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

    response = json.dumps(response, cls = Encoder)
    print(response)
    connection[1].close()
    connection[0].close()

    return {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': response,
    }

def companycontroldetails(event, context):   
    event = json.loads(event['body'])
    print (event)
    id = event['id']
    vendor = event['vendor']
    print (id)
    connection = sqlfunctions.make_connection()

    ## write string queries ##

    companyControlDetails = """
    select a.control_id, a.nist_function, a.org_control_family, a.description, a.org_statement_type, a.enterprise_bu, a.org_control_domains, a.source_framework_code,\
    a.source_framework, a.maturity, a.effectiveness_relevance, a.effectiveness_timeliness, a.effectiveness_adaptability, a.coverage, b.maturity, b.effectiveness_adaptability, \
    b.effectiveness_timeliness, b.effectiveness_relevance, b.group_coverage, b.uuid from control_attributes as a inner join sc_vendor_scores as b on a.control_id = b.control_id \
    where a.control_id = '{controlid}' and b.uuid = '{vendor}'
    """.format(controlid=id, vendor=vendor)

    ## this retrives rows from DB as a list
    response = sqlfunctions.retrieve_rows(connection, companyControlDetails)
    print(response)
    objects_list = []
    for row in response:
        d = collections.OrderedDict()
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

    response = json.dumps(response, cls = Encoder)
    print(response)
    connection[1].close()
    connection[0].close()

    return {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': response,
    }