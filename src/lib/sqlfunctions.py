from src.lib.propertieshelper import load_sql_properties, load_property_by
from src.lib.sqlhelper import SQLHandler
import os

def retrieve_rows(connection, sql_statement):
    conn = connection[0]
    cursor = connection[1]
    try:
        cursor.execute(sql_statement)
        rows = cursor.fetchall()
        for row in cursor.fetchall():
            rows.append(row)
        return rows
    except Exception as ex:
        print("Error occurred while retrieving data. Error Message : {}".format(ex))
        return False

def retrieve_rows_safe(connection, sql_statement, data):
    conn = connection[0]
    cursor = connection[1]
    try:
        cursor.execute(sql_statement, data)
        rows = []
        for row in cursor.fetchall():
            rows.append(row)
        return rows
    except Exception as ex:
        print("Error occurred while retrieving data. Error Message : {}".format(ex))
        return False

def update_rows(connection, sql_statement):
    conn = connection[0]
    cursor = connection[1]
    try:
        cursor.execute(sql_statement)
        conn.commit()
        updated_rows = cursor.rowcount
        return updated_rows
    except Exception as ex:
        print("Error occurred while retrieving data. Error Message : {}".format(ex))
        return False

def update_rows_safe(connection, sql_statement, data):
    conn = connection[0]
    cursor = connection[1]
    try:
        cursor.execute(sql_statement, data)
        conn.commit()
        updated_rows = cursor.rowcount
        return updated_rows
    except Exception as ex:
        print("Error occurred while retrieving data. Error Message : {}".format(ex))
        return False

def update_rows_many(connection, sql_statement, data):
    conn = connection[0]
    cursor = connection[1]
    try:
        cursor.executemany(sql_statement, data)
        conn.commit()
        updated_rows = cursor.rowcount
        return updated_rows
    except Exception as ex:
        print("Error occurred while retrieving data. Error Message : {}".format(ex))
        return False

def make_connection():
    script_dir = os.path.dirname(__file__)
    # print(script_dir)
    conf = script_dir+'/../resource/config.ini'

    credentials = load_sql_properties(conf)
    executor = SQLHandler()
    try:
        conn = executor.sql_connect(credentials)
        cursor = conn.cursor()
    except Exception as ex:
        print("Error occurred while initializing connection to sql. Error Message : {}".format(ex))
        exit(2)
    else:
        print("Running the script from {}\n".format(script_dir))
    return conn, cursor

def updateScore(connection, id, data):

    clearScore = """
    delete from group_scores_result_backup where threat_scenario = '{id}';
    """.format(id=id)

    deletedRow = update_rows(connection, clearScore)
    
    for row in data:
        update = """
        insert into group_scores_result_backup \
        (threat_scenario, control_id, existence, maturity, effectiveness_adaptability, effectiveness_relevance, effectiveness_timeliness, \
        group_coverage, current_pi, business_impact, business_unit, nist_function, effectiveness_score, tri_score, tri_score_stage) \
        values ('{threat_scenario}', '{control_id}', '{existence}', '{maturity}', '{effectiveness_adaptability}', '{effectiveness_relevance}', \
        '{effectiveness_timeliness}', '{group_coverage}', '{current_pi}', '{business_impact}', '{business_unit}', '{nist_function}', '{effectiveness_score}', '{tri_score}', '{tri_score_stage}')
        """.format(threat_scenario=row[0], control_id=row[1], existence=row[2], maturity=row[3], effectiveness_adaptability=row[4], effectiveness_relevance=row[5], effectiveness_timeliness=row[6], group_coverage=row[7], current_pi=row[8], business_impact=row[9], business_unit=row[10], nist_function=row[11], effectiveness_score=row[12], tri_score=row[13], tri_score_stage=row[14])

        update_rows(connection, update)
    return True

def assessScore(score):
    object_list =[]
    for row in score:
        effectivenessScore = 0
        maturityScore = float(row[3])
        coverage = float(row[7])
        nistStage = row[11]

        adaptability = convertScore(row[4], "adaptability")
        relevance = convertScore(row[5], "relevance")
        timeliness = convertScore(row[6], "timeliness")

        NA = [row[4], row[5], row[6]].count("N/A")
        strong = [row[4], row[5], row[6]].count("Strong")
        moderate = [row[4], row[5], row[6]].count("Moderate")
        weak = [row[4], row[5], row[6]].count("Weak")
        
        effectivenessScore = (relevance[0] + timeliness[0] + adaptability[0])/(relevance[1] + timeliness[1] + adaptability[1])
        
        triScore = (maturityScore + (effectivenessScore * 2)) / 3 * coverage
        triScoreStage = triStage(triScore, nistStage)
        rowList = list(row)
        rowList.append(effectivenessScore)
        rowList.append(triScore)
        rowList.append(triScoreStage)
        object_list.append(rowList)

    print (object_list)

    return object_list

def convertScore(score, metric):
    value = 0
    weight = 0

    if metric == "relevance":
        weight = 1
    elif metric == "timeliness":
        weight = 2
    elif metric == "adaptability":
        weight = 2

    if score == "N/A":
        value = 0
        weight = 0
    elif score == "Strong":
        value = 5 * weight
    elif score == "Moderate":
        value = 3 * weight
    elif score == "Weak":
        value = 1 * weight

    return value, weight

def triStage(score, nistStage):
    value = 0
    if nistStage == "Identify":
        value = score * 0.2
    elif nistStage == "Protect":
        value = score *0.2
    elif nistStage == "Detect":
        value = score * 0.20
    elif nistStage == "Respond":
        value = score * 0.2
    elif nistStage == "Recover":
        value = score * 0.2

    return value

def controlFamilyScore(connection, control_family):
    family_scores =[]

    for family in control_family:
        maturity_total = 0
        effectiveness_total = 0
        coverage_total = 0
        NA = 0

        sql_control_family = """
        select c.control_id, c.maturity, c.effectiveness_relevance, c.effectiveness_timeliness, c.effectiveness_adaptability, \
        c.group_coverage from (select * from group_scores as b where b.control_id in (SELECT a.control_id FROM public.control_attributes as a \
        WHERE a.org_control_family IN ('{controlfamily}')) and b.current_pi in ('current')) as c
        """.format(controlfamily=family)

        family_data = retrieve_rows(connection, sql_control_family)
        for data in family_data:
            adaptability = convertScore(data[4], "adaptability")
            relevance = convertScore(data[2], "relevance")
            timeliness = convertScore(data[3], "timeliness")
            effectiveness_score = (relevance[0] + timeliness[0] + adaptability[0])/(relevance[1] + timeliness[1] + adaptability[1])

            maturity_total += float(data[1])
            effectiveness_total += effectiveness_score
            if (data[5] != "N/A"):
                coverage_total += float(data[5])
            else: 
                NA += 1
        family_list = [family]
        print (family, maturity_total, effectiveness_total, coverage_total, NA)
        if (len(family_data) == 0 or len(family_data) - NA == 0):
            family_list.append(0)
            family_list.append(0)
            family_list.append(0)
            family_list.append(0)
        else:
            family_list.append(round(maturity_total/len(family_data), 1))
            family_list.append(round(effectiveness_total/len(family_data), 1))
            family_list.append(round(coverage_total/(len(family_data) - NA), 1))
            family_list.append(len(family_data))          

        family_scores.append(family_list)

    print (family_scores)

    return family_scores

def tsControlFamilyScore(connection, control_family, id):
    family_scores =[]

    for family in control_family:
        maturity_total = 0
        effectiveness_total = 0
        coverage_total = 0
        NA = 0
        print (family[0])

        sql_control_family = """
        select c.control_id, c.maturity, c.effectiveness_relevance, c.effectiveness_timeliness, c.effectiveness_adaptability, c.group_coverage from \
        (select * from group_scores as b where b.control_id in (SELECT a.control_id FROM public.control_attributes as a inner join ts_killchain_control_mapping as cm \
        on a.control_id = cm.control_id WHERE a.org_control_family IN ('{controlfamily}') and cm.threat_scenario = '{id}') and b.current_pi in ('current')) as c
        """.format(controlfamily=family[0], id=id)

        family_data = retrieve_rows(connection, sql_control_family)
        for data in family_data:
            adaptability = convertScore(data[4], "adaptability")
            relevance = convertScore(data[2], "relevance")
            timeliness = convertScore(data[3], "timeliness")
            effectiveness_score = (relevance[0] + timeliness[0] + adaptability[0])/(relevance[1] + timeliness[1] + adaptability[1])

            maturity_total += float(data[1])
            effectiveness_total += effectiveness_score
            if (data[5] != "N/A"):
                coverage_total += float(data[5])
            else: 
                NA += 1
        family_list = [family[0]]
        print (family[0], maturity_total, effectiveness_total, coverage_total, NA)
        if (len(family_data) == 0 or len(family_data) - NA == 0):
            family_list.append(0)
            family_list.append(0)
            family_list.append(0)
            family_list.append(0)
        else:
            family_list.append(round(maturity_total/len(family_data), 1))
            family_list.append(round(effectiveness_total/len(family_data), 1))
            family_list.append(round(coverage_total/(len(family_data) - NA), 1))
            family_list.append(len(family_data))          

        family_scores.append(family_list)

    print (family_scores)

    return family_scores

def assessVendorScore(score):
    object_list =[]
    for row in score:
        effectivenessScore = 0
        maturityScore = float(row[3])
        if (row[7] == "N/A"):
            coverage = float(0)
        else:
            coverage = float(row[7])
        nistStage = row[8]

        adaptability = convertScore(row[4], "adaptability")
        relevance = convertScore(row[5], "relevance")
        timeliness = convertScore(row[6], "timeliness")
        
        effectivenessScore = (relevance[0] + timeliness[0] + adaptability[0])/(relevance[1] + timeliness[1] + adaptability[1])
        
        triScore = (maturityScore + (effectivenessScore * 2)) / 3 * coverage
        triScoreStage = triStage(triScore, nistStage)
        rowList = list(row)
        rowList.append(effectivenessScore)
        rowList.append(triScore)
        rowList.append(triScoreStage)
        object_list.append(rowList)

    print (object_list)

    return object_list

def updateVendorScore(connection, id, data):

    clearScore = """
    delete from sc_scores_result where uuid = '{id}'
    """.format(id=id)

    deletedRow = update_rows(connection, clearScore)
    
    for row in data:
        updateVendor = """
        insert into sc_scores_result \
        (uuid, control_id, existence, maturity, effectiveness_adaptability, effectiveness_relevance, effectiveness_timeliness, \
        group_coverage, nist_function, threat_scenario, effectiveness_score, tri_score, tri_score_stage) \
        values ('{uuid}', '{control_id}', '{existence}', '{maturity}', '{effectiveness_adaptability}', '{effectiveness_relevance}', \
        '{effectiveness_timeliness}', '{group_coverage}', '{nist_function}', '{threat_scenario}', '{effectiveness_score}', '{tri_score}', '{tri_score_stage}')
        """.format(uuid=row[0], control_id=row[1], existence=row[2], maturity=row[3], effectiveness_adaptability=row[4], effectiveness_relevance=row[5], effectiveness_timeliness=row[6], group_coverage=row[7], nist_function=row[8], threat_scenario=row[9], effectiveness_score=row[10], tri_score=row[11], tri_score_stage=row[12])

        update_rows(connection, updateVendor)
    return True

def ControlFamilyScore(connection, control_family, uuid):
    family_scores =[]

    for family in control_family:
        maturity_total = 0
        effectiveness_total = 0
        coverage_total = 0
        NA = 0

        sql_control_family = """
        select c.control_id, c.maturity, c.effectiveness_relevance, c.effectiveness_timeliness, c.effectiveness_adaptability, c.group_coverage from \
        (select * from sc_vendor_scores as b where b.control_id in (SELECT a.control_id FROM public.control_attributes as a WHERE a.org_control_family IN ('{controlfamily}')) \
        and b.uuid in ('{uuid}') and b.existence in ('Exists')) as c
        """.format(controlfamily=family, uuid=uuid)

        family_data = retrieve_rows(connection, sql_control_family)
        for data in family_data:
            adaptability = convertScore(data[4], "adaptability")
            relevance = convertScore(data[2], "relevance")
            timeliness = convertScore(data[3], "timeliness")
            effectiveness_score = (relevance[0] + timeliness[0] + adaptability[0])/(relevance[1] + timeliness[1] + adaptability[1])

            maturity_total += float(data[1])
            effectiveness_total += effectiveness_score
            if (data[5] != "N/A"):
                coverage_total += float(data[5])
            else: 
                NA += 1
        family_list = [family]
        print (family, maturity_total, effectiveness_total, coverage_total, NA)
        if (len(family_data) == 0 or len(family_data) - NA == 0):
            family_list.append(0)
            family_list.append(0)
            family_list.append(0)
            family_list.append(0)
        else:
            family_list.append(round(maturity_total/len(family_data), 1))
            family_list.append(round(effectiveness_total/len(family_data), 1))
            family_list.append(round(coverage_total/(len(family_data) - NA), 1))
            family_list.append(len(family_data))          

        family_scores.append(family_list)

    print (family_scores)

    return family_scores

def vendorTSControlFamilyScore(connection, control_family, id, vendor):
    family_scores =[]

    for family in control_family:
        maturity_total = 0
        effectiveness_total = 0
        coverage_total = 0
        NA = 0
        print (family[0])

        sql_control_family = """
        select c.control_id, c.maturity, c.effectiveness_relevance, c.effectiveness_timeliness, c.effectiveness_adaptability, c.group_coverage from
        (select * from sc_scores_result as b where b.control_id in (SELECT a.control_id FROM public.control_attributes as a inner join ts_killchain_control_mapping as cm
        on a.control_id = cm.control_id WHERE a.org_control_family IN ('{controlfamily}') and cm.threat_scenario = '{id}') and b.uuid in ('{vendor}') and b.existence in ('Exists')) as c
        """.format(controlfamily=family[0], id=id, vendor=vendor)

        family_data = retrieve_rows(connection, sql_control_family)
        for data in family_data:
            adaptability = convertScore(data[4], "adaptability")
            relevance = convertScore(data[2], "relevance")
            timeliness = convertScore(data[3], "timeliness")
            effectiveness_score = (relevance[0] + timeliness[0] + adaptability[0])/(relevance[1] + timeliness[1] + adaptability[1])

            maturity_total += float(data[1])
            effectiveness_total += effectiveness_score
            if (data[5] != "N/A"):
                coverage_total += float(data[5])
            else: 
                NA += 1
        family_list = [family[0]]
        print (family[0], maturity_total, effectiveness_total, coverage_total, NA)
        if (len(family_data) == 0 or len(family_data) - NA == 0):
            family_list.append(0)
            family_list.append(0)
            family_list.append(0)
            family_list.append(0)
        else:
            family_list.append(round(maturity_total/len(family_data), 1))
            family_list.append(round(effectiveness_total/len(family_data), 1))
            family_list.append(round(coverage_total/(len(family_data) - NA), 1))
            family_list.append(len(family_data))          

        family_scores.append(family_list)

    print (family_scores)

    return family_scores