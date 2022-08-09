import requests
import time
import src.lib.sqlfunctions as sqlfunctions

def filter_dict_keys(dictionary, keys):
    """Filters a dict by only including certain keys."""
    key_set = set(keys) & set(dictionary.keys())
    return {key: dictionary[key] for key in key_set}

def generate_asset_payload(name, domain):
    return(
        {
            "name":name,
            "data":{
                "fqdn":domain,
                "is_scanning_enabled": False,
                "is_shadow_asset_relations_discovery_needed": True
            },
            "fetching_progress": 0,
            "id": 0,
            "risks": [],
            "search_types":[
                "bucket",
                "bucket_object",
                "chat_message",
                "domain",
                "driller_host",
                "driller_profile",
                "forum_post",
                "forum_profile",
                "forum_topic",
                "google",
                "leak",
                "listing",
                "paste",
                "ransomleak",
                "seller",
                "source_code"
            ],
            "tenant_id": 2377,
            "type": "domain"
        }
    )


def get_port_riskiness(port_numbers): #list of port numbers
    connection = sqlfunctions.make_connection()
    query = """
    SELECT SUM("risk_level"), COUNT(*) FROM ports_riskiness WHERE port IN %s
    """
    length = len(port_numbers)
    total = 0
    ports_score = sqlfunctions.retrieve_rows_safe(connection, query, (tuple(port_numbers),))
    print(ports_score)
    if ports_score[0] == None:
        ports_score[0] = 0
    resultLength = ports_score[1]
    total = ports_score[0] + ((length - resultLength) * 4)
    print(total)
    connection[1].close()
    connection[0].close()
    
    return total/length

class FlareAPI:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        self.token = self.initialize()
    
    def initialize(self):
        url = self.base_url + '/tokens/generate'
        req = requests.post(url, auth=('', self.api_key))
        data = req.json()
        return data['token']
    
    def get(self, path):
        url = self.base_url + path
        try:
            response  = requests.get(url, headers={'Authorization': 'Bearer ' + self.token})
            #if not response .status_code // 100 == 2:
            #    return "Error: Unexpected response {}".format(response)
            json_obj = response.json()
            return json_obj
        except requests.RequestException as e:
            raise SystemExit(e)
    
    def post(self, path, data):
        url = self.base_url + path
        #print(url, data)
        try:
            response  = requests.post(url, headers={'Authorization': 'Bearer ' + self.token}, json=data)
            if not response .status_code // 100 == 2:
                return "Error: Unexpected response {}".format(response)

            json_obj = response.json()
            return json_obj
        except requests.RequestException as e:
            raise SystemExit(e)

    def put(self, path, data):
        url = self.base_url + path
        try:
            response = requests.put(url, headers={'Authorization': 'Bearer ' + self.token}, json=data)
            if not response .status_code // 100 == 2:
                return "Error: Unexpected response {}".format(response)

            json_obj = response.json()
            return json_obj
        except requests.RequestException as e:
            raise SystemExit(e)

    def delete(self, path, data):
        url = self.base_url + path
        try:
            response = requests.delete(url, headers={'Authorization': 'Bearer ' + self.token}, json=data)
            if not response .status_code // 100 == 2:
                return "Error: Unexpected response {}".format(response)
            json_obj = response.json()
            return json_obj
        except requests.RequestException as e:
            raise SystemExit(e)

    def add_new_domain(self, payload):
        response = self.post('/firework/v2/assets/', payload)
        return response

    def delete_domain(self, id):
        response = self.delete('/firework/v2/assets/{id}'.format(id=id),id)
        return response

    def check_leaked_creds(self, domain):
        query_count = """/firework/v2/activities/leak/leaksdb/{domain}/count""".format(domain=domain)
        count_data = self.get(query_count)
        
        query_creds = """/firework/v2/activities/leak/leaksdb/{domain}""".format(domain=domain)
        creds_data = self.get(query_creds)
        return {"total_creds_exposed": count_data["count"], "leaked_data": creds_data['activity']['data']['identities']}

    def check_driller_hosts(self, id):
        query = """/firework/v2/assets/{id}/feed?size=100&types%5B%5D=driller_host&order=desc&sort_by=created""".format(id=id)
        data = self.get(query)
        #print(data)
        exposure = []
        ports = []
        exposure_exists = {
            "vulns_exist": False, 
            "ssl_expiry_exists": False,
            "ssl_self_signed_exists": False,
        }

        for finding in data['items']:
            #check for ssl cert expiry
            try: 
                ssl_expiry = finding['data']['ssl']['cert']['expired']
            except:
                ssl_expiry = None
            #check for ssl cert expiry
            try: 
                if (finding['data']['tags'].count('self-signed') > 0):
                    ssl_self_signed = True
                else:
                    ssl_self_signed = False
            except:
                ssl_self_signed = None
            #check for vulns
            try: 
                vulns = finding['data']['opts']['vulns']
            except:
                vulns = None
            port = finding['port']
            ports.append(port)
            service = {
                "service": finding['data']['_shodan']['module'],
                "port": port,
                "vulns": vulns,
                "ssl_expiry": ssl_expiry,
                "ssl_self_signed": ssl_self_signed
            }
            #print(finding['data']['opts'])
            exposure.append(service)
        for item in exposure:
            if (bool(item['vulns'])):
                exposure_exists['vulns_exists'] = True
            if (ssl_expiry == True):
                exposure_exists['ssl_expiry_exists'] = True
            if (ssl_self_signed == True):
                exposure_exists['ssl_self_signed_exists'] = True
        ports = list(set(ports))
        #ports_risk = get_port_riskiness(ports)
        return {"exposureExists": exposure_exists, "exposureData": exposure, "open_ports": ports}
    
    def subdomains(self, id):
        query = """/firework/v2/assets/{id}/subdomains""".format(id=id)
        data = self.get(query)
        #print(data)
        return data

    def subdomain_scan_results(self, id, subdomain):
        query = """/firework/v2/assets/{id}/subdomains/{subdomain}/feed?size=100&order=desc&sort_by=created&use_global_policies=true""".format(id=id, subdomain=subdomain)
        data = self.get(query)
        high_risk = []
        exposure = []
        vulns = []
        ssl = False
        vuln_number = 0

        for row in data['items']:
            if row['risk']['score'] > 2:
                high_risk.append(row)

        for row in high_risk:
            ip_address = row['ip_address']
            if 'SERVER_VULNERABILITIES' in row['risk']['reasons']:
                vul_list = []
                for vul in row['vulnerabilities']:
                    vul_list.append(vul['name'])
                vuln_number += len(vul_list)
                vulns.append(
                    {
                        "host": ip_address,
                        "number": len(vul_list), 
                        "vulnerabilities": vul_list, 
                    }
                )

            if 'PORT' in row['risk']['reasons']:
                recommendation = ''
                exposure_risk = ''
                if row['port'] == 9200:
                    exposure_risk = 'High'
                    recommendation = 'Port 9200 is the default port for elastic search is very attractive given it is a database service, and multiple vulnerabilities have been associated over the years not only to this service, but other service often used in conjunction such as Kibana. Close the open port immediately.'
                elif row['port'] == 445:
                    exposure_risk = 'High'
                    recommendation = 'Port 445 is commonly used by Microsoft Active Directory (AD) services. It attracts the attention of malicious actors, given the potentially very valuable information that might be behind the authentication wall. Close the open port immediately.'
                elif row['port'] == 8888:
                    exposure_risk = 'Medium'
                    recommendation = 'Port 8888 is known to be used by developer when testing, or prototyping. It is often opened for a short amount of time, often with an HTTP service running, but it is also prone to be left open by mistake. Close the open port immediately.'
                elif row['port'] == 8081:
                    exposure_risk = 'Medium'
                    recommendation = 'Port 8081 is known to be used by developer when testing, or prototyping. It is often opened for a short amount of time, often with an HTTP service running, but it is also prone to be left open by mistake. Close the open port immediately.'
                elif row['port'] == 8080:
                    exposure_risk = 'Medium'
                    recommendation = 'Port 8080 is known to be used by developer when testing, or prototyping. It is often opened for a short amount of time, often with an HTTP service running, but it is also prone to be left open by mistake. Close the open port immediately.'
                elif row['port'] == 5432:
                    exposure_risk = 'Medium'
                    recommendation = 'Port 5432 is Postgresql database default port should not be open to the internet, if only because ports related to Database are often attracting unwanted attention from malicious actors. Close the open port immediately.'
                elif row['port'] == 3389:
                    exposure_risk = 'Medium'
                    recommendation = 'Port 3389 is associated to the RDP service which have been known to be prone to risk when available from the public internet. Close the open port immediately.'
                else:
                    exposure_risk = 'Low'
                    recommendation = 'N/A'
                exposure.append(
                    {
                        "host": ip_address,
                        "port": row['port'],
                        "risk": exposure_risk,
                        "recommendation": recommendation
                    }
                )
            if 'EXPIRED_SSL' in row['risk']['reasons']:
                ssl = True
        #print(data)
        return ({"exposure_number": len(exposure), "exposure": exposure, "vulnerabilities_number": vuln_number, "vulnerabilities": vulns, "ssl_expired": ssl})

    def check_marketplace(self, id):
        query = """/firework/v2/assets/{id}/feed?types[]=illicit_networks&order=desc&sort_by=created&time=&lite=true&merge_duplicates=true&fetch_type=results&risks[]=3&risks[]=4&risks[]=5&size=100&use_global_policies=true""".format(id=id)
        data = self.get(query)
        keys = ['actor', 'first_crawled_at', 'source', 'source_name', 'timestamp', 'risk']
        filtered_d = []
        for item in data['items']:
            filtered_d.append(filter_dict_keys(item, keys))

        return({'items': filtered_d})


def assess_exposure(exposure):
    count = {'total': 0, 'medium': 0, 'high': 0}
    for item in exposure:
        if item['risk'] == 'Medium':
            count['medium'] += 1
        elif item['risk'] == 'Medium':
            count['high'] += 1
    count['total'] =  count['medium'] + count['high']
    return count

def evaluate_risk(results):
    risk_score = {'creds_score': 0, 'exposure_score': 0, 'vuln_score': 0, 'ssl_score': 0, 'marketplace_score': 0}
    #score for credentials leaked
    # LOW(1) - no leaked credentials
    # MEDIUM(3) - leaked credentials over the past year
    # HIGH(5) - not sure
    if results['credentials']['total_creds_exposed'] == 0:
        risk_score['creds_score'] = 1
    elif results['credentials']['total_creds_exposed'] > 0:
        risk_score['creds_score'] = 3


    #score for vuls
    #LOW(1) - no vulns
    #MEDIUM(2) - medium risk vulns
    #HIGH(5) - high risk vulns determined by CVSS scores
    if len(results['exposure']['vulnerabilities']) == 0:
        risk_score['vuln_score'] = 1
    else:
        risk_score['vuln_score'] = 3

    #score for exposure
    #LOW - low risk ports exposed
    #MEDIUM - medium risk ports exposed
    #HIGH - high risk ports exposed
    if len(results['exposure']['exposure']) == 0:
        risk_score['exposure_score'] = 1
    else:
        exposure_results = assess_exposure(results['exposure']['exposure'])
        if exposure_results['high'] > 0:
            risk_score['exposure_score'] = 5
        elif exposure_results['medium'] > 0:
            risk_score['exposure_score'] = 3
        else:
            risk_score['exposure_score'] = 1
    #SSL
    #LOW - no expired SSL certs
    #HIGH - expired SSL certs exist
    if results['exposure']['ssl_expired']:
        risk_score['ssl_score'] = 5
    else:
        risk_score['ssl_score'] = 1
    #score for marketplace
    #LOW - no mentions on marketplaces
    #MEDIUM - mentions on marketplaces
    #HIGH - more than 5 mentions on marketplaces
    if len(results['marketplace']) == 0:
        risk_score['marketplace_score'] = 1
    elif len(results['marketplace']) < 10: 
        risk_score['marketplace_score'] = 3
    elif len(results['marketplace']) > 10: 
        risk_score['marketplace_score'] = 5
    
    return risk_score

def add_flare_identifier(name, domain):
    test = FlareAPI('https://api.flared.io', 'fw_pLsSHtlviSBiAwlHAmYYhNiZITrCZrCnOVHIHvmC')
    payload = generate_asset_payload(name, domain)
    new_asset = test.add_new_domain(payload)
    id = new_asset["asset"]["id"]
    leaked_creds = test.check_leaked_creds(domain)
    #sleep for 120 seconds to allow search results of flare to return
    time.sleep(5)
    subdomain_results = test.subdomain_scan_results(id, domain)
    marketplace_results = test.check_marketplace(id)

    return ({"asset": new_asset, "credentials": leaked_creds, "exposure": subdomain_results, "marketplace": marketplace_results})

def delete_identifier(id):
    flare = FlareAPI('https://api.flared.io', 'fw_pLsSHtlviSBiAwlHAmYYhNiZITrCZrCnOVHIHvmC')
    print("checking the id: ", id)
    response = flare.delete_domain(id)

    return response