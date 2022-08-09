from src.lib.propertieshelper import load_sql_properties, load_property_by
import src.lib.sqlfunctions as sqlfunctions

def update_title(connection, id, data):

    update_query = """
    update ts_id set threat_scenario_title = %s, description = %s where threat_scenario = %s
    """
    updateTitle = sqlfunctions.update_rows_safe(connection, update_query, (data[0]["title"], data[0]["description"], id,))
    return True

def update_controls(connection, id, data):

    clear_controls_query = """
    delete from ts_killchain_control_mapping where threat_scenario = %s;
    """
    delete_controls = sqlfunctions.update_rows_safe(connection, clear_controls_query, (id,))
    
    update_controls_query = """
    insert into ts_killchain_control_mapping(threat_scenario, killchain_stage, control_id) \
    select %s as threat_scenario, coalesce(b.killchain_stage, 'Reconnaissance') as killchain_stage, a.control_id \
    from public.ts_technique_control as a left join ts_killchain_techniques as b on a.technique_id = b.technique_id \
    where a.technique_id = 'NIL' or (a.technique_id in (select tkt.technique_id from ts_killchain_techniques tkt \
    where tkt.threat_scenario = %s) and b.threat_scenario = %s)
    """
    sqlfunctions.update_rows_safe(connection, update_controls_query, (id, id, id,))
    #for row in data:
    #    update = """
    #    insert into ts_killchain_control_mapping(threat_scenario, killchain_stage, control_id) values (%s, %s, %s)
    #    """

    #    sqlfunctions.update_rows_safe(connection, update, (id, row["killChainStage"], row["controlID"]))
    return True

def update_business_details(connection, id, data):

    clear_details_query = """
    delete from ts_bi_bu_mapping where threat_scenario = %s
    """
    delete = sqlfunctions.update_rows_safe(connection, clear_details_query, (id,))

    for row in data:
        update = """
        insert into ts_bi_bu_mapping(threat_scenario, business_unit, business_impact) values (%s, %s, %s)
        """
        sqlfunctions.update_rows_safe(connection, update, (id, row['businessUnit'], row['businessImpact'],))

    return True

def update_threat_vector(connection, id, data):

    clear_threat_vector = """
    delete from ts_vector_mapping where threat_scenario = %s
    """
    delete = sqlfunctions.update_rows_safe(connection, clear_threat_vector, (id,))
    for row in data:
        update = """
        insert into ts_vector_mapping(threat_scenario, vector) values (%s, %s)
        """
        sqlfunctions.update_rows_safe(connection, update, (id, row['threatVector'],))

    return True

def update_threat_actor(connection, id, data):

    clear_threat_actor = """
    delete from ts_actor_mapping where threat_scenario = %s
    """
    delete = sqlfunctions.update_rows_safe(connection, clear_threat_actor, (id,))

    for row in data:
        update = """
        insert into ts_actor_mapping(threat_scenario, actor) values (%s, %s)
        """
        sqlfunctions.update_rows_safe(connection, update, (id, row['threatActor'],))

    return True

def update_techniques(connection, id, data):

    clear_techniques = """
    delete from ts_killchain_techniques where threat_scenario = %s
    """
    delete = sqlfunctions.update_rows_safe(connection, clear_techniques, (id,))

    for row in data:
        print(row)
        update = """
        insert into ts_killchain_techniques(threat_scenario, killchain_stage, technique, technique_id) values (%s, %s, %s, %s)
        """
        sqlfunctions.update_rows_safe(connection, update, (id, row['killChainStage'], row['technique'], row['id'],))

    return True

def update_industry(connection, id, data):

    clear_industry = """
    delete from ts_industry where threat_scenario = %s
    """
    delete = sqlfunctions.update_rows_safe(connection, clear_industry, (id,))
    
    for row in data:
        update = """
        insert into ts_industry(threat_scenario, industry) values (%s, %s)
        """
        sqlfunctions.update_rows_safe(connection, update, (id, row['industry'],))

    return True

def update_industry(connection, id, data):

    clear_industry = """
    delete from ts_industry where threat_scenario = %s
    """
    delete = sqlfunctions.update_rows_safe(connection, clear_industry, (id,))
    
    for row in data:
        update = """
        insert into ts_industry(threat_scenario, industry) values (%s, %s)
        """
        sqlfunctions.update_rows_safe(connection, update, (id, row['industry'],))

    #update threat scenario to company mapping
    clear_mapping = """
    delete from sc_ts_vendors where threat_scenario = %s
    """
    
    delete = sqlfunctions.update_rows_safe(connection, clear_mapping, (id,))

    update_company_ts = """
    insert into sc_ts_vendors (vendor, threat_scenario) select ic.uuid, ti.threat_scenario from insured_companies ic \
        inner join ts_industry ti on ic.industry = ti.industry where ti.threat_scenario = %s
    """
    sqlfunctions.update_rows_safe(connection, update_company_ts, (id,))

    return True

def convert_score(score, metric):
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

def tri_stage(score, nist_stage):
    value = 0
    if nist_stage == "Identify":
        value = score * 0.2
    elif nist_stage == "Protect":
        value = score *0.2
    elif nist_stage == "Detect":
        value = score * 0.20
    elif nist_stage == "Respond":
        value = score * 0.2
    elif nist_stage == "Recover":
        value = score * 0.2

    return value

def assess_company_score(score):
    object_list =[]
    for row in score:
        effectiveness_score = 0
        maturity_score = float(row[3])
        if (row[7] == "N/A"):
            coverage = float(0)
        else:
            coverage = float(row[7])
        nist_stage = row[8]

        adaptability = convert_score(row[4], "adaptability")
        relevance = convert_score(row[5], "relevance")
        timeliness = convert_score(row[6], "timeliness")
        
        effectiveness_score = (relevance[0] + timeliness[0] + adaptability[0])/(relevance[1] + timeliness[1] + adaptability[1])
        
        tri_score = (maturity_score + (effectiveness_score * 2)) / 3 * coverage
        tri_score_stage = tri_stage(tri_score, nist_stage)
        row_list = list(row)
        row_list.append(effectiveness_score)
        row_list.append(tri_score)
        row_list.append(tri_score_stage)
        object_list.append(row_list)

    print (object_list)

    return object_list

def update_company_score(connection, id, data):

    clear_score = """
    delete from sc_scores_result where threat_scenario = '{id}'
    """.format(id=id)

    delete_row = sqlfunctions.update_rows(connection, clear_score)
    
    for row in data:
        update_company_scores = """
        insert into sc_scores_result \
        (uuid, control_id, existence, maturity, effectiveness_adaptability, effectiveness_relevance, effectiveness_timeliness, \
        group_coverage, nist_function, threat_scenario, effectiveness_score, tri_score, tri_score_stage) \
        values ('{uuid}', '{control_id}', '{existence}', '{maturity}', '{effectiveness_adaptability}', '{effectiveness_relevance}', \
        '{effectiveness_timeliness}', '{group_coverage}', '{nist_function}', '{threat_scenario}', '{effectiveness_score}', '{tri_score}', '{tri_score_stage}')
        """.format(uuid=row[0], control_id=row[1], existence=row[2], maturity=row[3], effectiveness_adaptability=row[4], effectiveness_relevance=row[5], effectiveness_timeliness=row[6], group_coverage=row[7], nist_function=row[8], threat_scenario=row[9], effectiveness_score=row[10], tri_score=row[11], tri_score_stage=row[12])

        sqlfunctions.update_rows(connection, update_company_scores)
    return True