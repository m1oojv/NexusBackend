def listToString(s): 
    # initialize an empty string
    str1 = " " 
    # return string  
    return (str1.join(s))

def get_score(score, control_id, uuid):
    if score == 1:
        return {
            'control_id': control_id,
            'uuid': uuid,
            'maturity': 3,
            'effectiveness_adaptability': 'Moderate',
            'effectiveness_relevance': 'Moderate',
            'effectiveness_timeliness': 'Moderate',
            'coverage': 0.8,
        }
    elif score == 3:
        return {
            'control_id': control_id,
            'uuid': uuid,
            'maturity': 3,
            'effectiveness_adaptability': 'Moderate',
            'effectiveness_relevance': 'Moderate',
            'effectiveness_timeliness': 'Moderate',
            'coverage': 0.6,
        }
    elif score == 5:
        return {
            'control_id': control_id,
            'uuid': uuid,
            'maturity': 2,
            'effectiveness_adaptability': 'Weak',
            'effectiveness_relevance': 'Moderate',
            'effectiveness_timeliness': 'Weak',
            'coverage': 0.4,
        }
    
    return True

def get_controls_scores(controls, risk_score, uuid):
    results = []
    for row in controls:
        if row[1] == 'vuln': #check scan indicator for vuln
            results.append(get_score(risk_score['vuln_score'], row[0], uuid))
        elif row[1] == 'creds': #check scan indicator for vuln
            results.append(get_score(risk_score['creds_score'], row[0], uuid))
        elif row[1] == 'exposure': #check scan indicator for vuln
            results.append(get_score(risk_score['exposure_score'], row[0], uuid))
        elif row[1] == 'marketplace': #check scan indicator for markertplace
            results.append(get_score(risk_score['marketplace_score'], row[0], uuid))
        elif row[1] == 'self_assess': #check scan indicator for vuln
            results.append(get_score(risk_score['vuln_score'], row[0], uuid))
    return results
