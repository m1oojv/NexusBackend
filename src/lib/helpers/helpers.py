from datetime import datetime
import json
import logging

import src.lib.sqlfunctions as sql_functions
from src.lib.scanners.risk_recommendations import risk_recommendations


def list_to_string(s):
    # Initialize an empty string
    str1 = " "
    # Return string
    return str1.join(s)


def get_score(score, control_id, uuid):
    if score == 1:
        return {"control_attribute_id": control_id,
                "control_assessment_id": uuid,
                "body":{
                    "maturity": 4,
                    "effectiveness_adaptability": 'Strong',
                    "effectiveness_relevance": 'Strong',
                    "effectiveness_timeliness": 'Strong',
                    "group_coverage": 0.8,
                    }
                }
    elif score == 2:
        return {"control_attribute_id": control_id,
                "control_assessment_id": uuid,
                "body":{
                    "maturity": 3,
                    "effectiveness_adaptability": 'Strong',
                    "effectiveness_relevance": 'Strong',
                    "effectiveness_timeliness": 'Moderate',
                    "group_coverage": 0.6,
                    }
                }
    elif score == 3:
        return {"control_attribute_id": control_id,
                "control_assessment_id": uuid,
                "body":{
                    "maturity": 3,
                    "effectiveness_adaptability": 'Moderate',
                    "effectiveness_relevance": 'Moderate',

                    "effectiveness_timeliness": 'Moderate',
                    "group_coverage": 0.4,
                    }
                }
    elif score == 4:
        return {"control_attribute_id": control_id,
                "control_assessment_id": uuid,
                "body":{
                    "maturity": 3,
                    "effectiveness_adaptability": 'Moderate',
                    "effectiveness_relevance": 'Moderate',
                    "effectiveness_timeliness": 'Moderate',
                    "group_coverage": 0.3,
                    }
                }
    elif score == 5:
        return {"control_attribute_id": control_id,
                "control_assessment_id": uuid,
                "body":{
                    "maturity": 2,
                    "effectiveness_adaptability": 'Weak',
                    "effectiveness_relevance": 'Weak',
                    "effectiveness_timeliness": 'Weak',
                    "group_coverage": 0.2,
                    }
                }

    return True


def get_controls_scores(controls, risk_score, control_assessment_id):
    results = []
    indicator2score = {"vuln": "vulns_score",
                       "creds": "creds_score",
                       "exposure": "ports_score",
                       "marketplace": "marketplace_score",
                       "ssl_expiry": "ssl_expiry_score",
                       "email_security": "email_security_score",
                       "web_headers": "web_headers_score",
                       "self_assess": "vulns_score"
                       }
    for row in controls:
        if row['scan_indicator'] in indicator2score.keys():
            score = indicator2score[row['scan_indicator']]
            results.append(get_score(risk_score[score], str(row['control_attribute_id']), control_assessment_id))

    return results


def filter_scan_info(scan_results):
    """
    Returns the data to be used in the frontend from the raw scan domain data that is derived
    from running scan_domain.
    :param scan_results:    data field of the results from scan_domain
    :type scan_results:     dict
    """
    # Filter out for relevant credentials info (which in this case is everything)
    creds = scan_results["credentials"]
    if "error" in creds.keys():
        # Return an empty dict if error occurs, don't need to propagate error
        # message to frontend
        creds = dict()

    # Filter out for relevant email security info
    raw_email_sec = scan_results["email_security"]
    if type(raw_email_sec) == list or "error" in raw_email_sec.keys():
        # Don't need to propagate error message to frontend
        email_sec = dict()
    else:
        email_sec = {"spf": {"valid": raw_email_sec["spf"]["valid"],
                             "error": raw_email_sec["spf"].get("error", "")
                             },
                     "dmarc": {"valid": raw_email_sec["dmarc"]["valid"],
                               "error": raw_email_sec["dmarc"].get("error", "")
                               }
                     }

    # Filter out for relevant marketplace
    marketplace = []
    if "error" in scan_results["marketplace"].keys():
        pass  # Return marketplace as an empty list
    else:
        marketplace_items = set()
        for item in scan_results["marketplace"]["items"]:
            # Convert timestamp to datetime
            timestamp = datetime.strptime(item["timestamp"][::-1].replace(":", "", 1)[::-1], "%Y-%m-%dT%H:%M:%S%z")
            timestamp_str = timestamp.strftime("%d/%m/%Y")

            raw_item = (item["source"], " ".join(item["risk"]["reasons"]), timestamp_str)
            if raw_item in marketplace_items:
                continue
            else:
                marketplace_items.add(raw_item)
                marketplace.append({"source": item["source"],
                                    "reason": item["risk"]["reasons"],
                                    "date": timestamp_str,
                                    })

    raw_subdomains = scan_results["subdomains"]
    if type(raw_subdomains) == dict and "error" in raw_subdomains.keys():
        vulns = dict()
        ports = dict()
    else:
        # Filter out for relevant vulnerabilities
        vulns_data = set()
        for subdomain in raw_subdomains:
            for ip in subdomain["data"]:
                if "error" in ip.keys():
                    continue
                for service in ip["exposure"]:
                    if "vulns" in service.keys():
                        for cve, cve_details in service["vulns"].items():
                            cvss = float(cve_details["cvss"])
                            summary = cve_details["summary"]
                            vulns_data.add((ip["ip"], cve, cvss, summary))
                            # vulns_data.add({"ip": ip["ip"],
                            #                 "cve": cve,
                            #                 "cvss": cvss,
                            #                 "summary": summary
                            #                 })
        vulns = {"totalNumberOfVulns": len(vulns_data),
                 "data": [{"ip": vuln[0], "cve": vuln[1], "cvss": vuln[2], "summary": vuln[3]} for vuln in vulns_data]
                 }

        # Filter out for relevant ports
        ports_data = {"high": [], "medium": []}
        for subdomain in raw_subdomains:
            for ip in subdomain["data"]:
                if "error" in ip.keys():
                    continue
                high_ports = ip["ports"]["high"]
                medium_ports = ip["ports"]["medium"]
                if not high_ports and not medium_ports:  # If there are no high or medium ports exposed
                    continue
                for service in ip["exposure"]:
                    if service["port"] in high_ports:
                        ports_data["high"].append({"ip": ip["ip"],
                                                   "service": service["service"],
                                                   "port": service["port"],
                                                   "risk": "High",
                                                   })
                    elif service["port"] in medium_ports:
                        ports_data["medium"].append({"ip": ip["ip"],
                                                     "service": service["service"],
                                                     "port": service["port"],
                                                     "risk": "Medium",
                                                     })
        ports = {"totalNumberOfHighRisk": len(ports_data["high"]),
                 "totalNumberOfMediumRisk": len(ports_data["medium"]),
                 "data": ports_data
                 }

    filtered_data = {"credentials": creds,
                     "email_security": email_sec,
                     "vulns": vulns,
                     "marketplace": marketplace,
                     "ports": ports,
                     }

    return filtered_data


def filter_rec_info(rec_info):
    """
    Join recommendations from the same field together into 1 string.
    :param rec_info:    recommendations from scan_domain
    :type rec_info:     dict
    """
    for k, v in rec_info.items():
        desc = "<br/>".join([detail["rec"] for detail in v["details"]])
        rec_info[k] = desc
    return rec_info


def get_pdf_data(scan_results):
    """
    Returns nice clean data that will be used when generating a PDF report of the company's
    risk assessment.
    Output data structure: [{"idx": entry_index,
                             "area": risk_area,
                             "finding": findings,
                             "rec": recommendations,
                             "level": risk_level
                             }]
    TODO: Find a way to streamline this function (and probably how the data are stored in the
          database to minimize the need to manipulate the data after extracting it from the
          database.
    :param scan_results:    Results from scan_domain after passing the "data" field's data
                            through filter_scan_info to get only the necessary data.
                            Aka: scan_results = scan_domain(data['companyName'], data['domain'])
                                 scan_results['data'] = helpers.filter_scan_info(scan_results['data'])
                                 pdf_data = get_pdf_data(scan_results)
    :type scan_results:     dict
    """
    # Dictionary to map key values of recommendations to the key values of their risk scores
    # Needed since scores and recommendations are stored in 2 different dictionaries but we want
    # to pair up scores with their recommendations in the pdf data.
    recs2score = {"creds_rec": "creds_score",
                  "vulns_rec": "vulns_score",
                  "ports_rec": "ports_score",
                  "ssl_expiry_rec": "ssl_expiry_score",
                  "marketplace_rec": "marketplace_score",
                  "email_security_rec": "email_security_score",
                  "web_headers_rec": "web_headers_score",
                  }
    # Dictionary to map risk scores to their risk levels
    score2risk_level = {1: "Low Risk",
                        2: "Low Risk",
                        3: "Medium Risk",
                        4: "High Risk",
                        5: "High Risk"}
    pdf_data = []
    idx = 1
    for rec_name, rec_details in scan_results["risk_recommendations"].items():
        if rec_name == "ports_rec" or rec_name == "ssl_expiry_rec" or rec_name == "web_headers_rec":
            # Ignore these fields since they aren't used so far
            # Ports will be included into the pdf data at the end of this function
            continue
        for detail in rec_details["details"]:
            row = {"idx": idx,
                   "area": rec_details["area"],
                   "finding": detail['finding'],
                   "rec": detail['rec'],
                   "level": score2risk_level[scan_results["risk_results"][recs2score[rec_name]]]
                   }

            # For these recommendation fields, add in extra data to their findings column
            if rec_name == 'creds_rec':
                row["finding"] += ("<br/><br/>" + "Contact us for more details.")
            elif rec_name == "vulns_rec":
                # Include CVE details
                total_vulns_count = scan_results['data']['vulns']['totalNumberOfVulns']
                row["finding"] += (f"<br/><br/>"
                                   f"Total number of vulnerabilities: {total_vulns_count}<br/>"
                                   f"Vulnerabilities found:<ol>")
                for vuln in scan_results["data"]["vulns"]["data"]:
                    row["finding"] += (f"<li>"
                                       f"IP: {vuln['ip']}<br/>"
                                       f"CVE: {vuln['cve']}<br/>"
                                       f"CVSS Score: {vuln['cvss']}<br/>"
                                       f"Summary: {vuln['summary']}"
                                       f"</li>")
                row["finding"] += "</ol>"
            elif rec_name == "marketplace_rec":
                # Include marketplace details
                row["finding"] += ("<br/><br/>"
                                   "Marketplace Mentions:<ol>")
                for mention in scan_results["data"]["marketplace"]:
                    row["finding"] += (f"<li>"
                                       f"Source: {mention['source']}<br/>"
                                       f"Reason: {mention['reason'][0]}"
                                       f"</li>")
                row["finding"] += "</ol>"
            pdf_data.append(row)
            idx += 1

    # Include port recommendations and details into pdf_info
    # This is done separately to the other recommendations as ports are split into 1 per row
    # in pdf_info. But the scan_results data only give aggregated port data. Thus will need
    # to re-construct the data.

    # A dictionary of port number to their risk level and a list of IPs and services with the
    # using that particular port number.
    # Schema:
    # ports = {port_number: {"level": "risk level",
    #                          "details": [{"ip": "ip",
    #                                       "service": "service"
    #                                       }]
    #                        }
    ports = {}
    for port in scan_results["data"]["ports"]["data"]["high"]:
        if port["port"] not in ports.keys():
            ports[port["port"]] = {"level": "High Risk", "details": []}
        ports[port["port"]]["details"].append({"ip": port["ip"], "service": port["service"]})
    for port in scan_results["data"]["ports"]["data"]["medium"]:
        if port["port"] not in ports.keys():
            ports[port["port"]] = {"level": "Medium Risk", "details": []}
        ports[port["port"]]["details"].append({"ip": port["ip"], "service": port["service"]})

    # Construct the rows of data to put into pdf_info
    for port, details in ports.items():
        row = {"idx": idx,
               "area": risk_recommendations["ports"]["area"],
               "finding": risk_recommendations["ports"]["details"][port]['finding'],
               "level": details["level"],
               "rec": risk_recommendations["ports"]["details"][port]['rec']}
        row["finding"] += ("<br/><br/>"
                           "Affected IPs:"
                           "<ul>")
        # Add IPs and Services that uses the specific port to that port's findings column
        for detail in details["details"]:
            row["finding"] += f"<li>IP: {detail['ip']}<br/>Service: {detail['service']}</li>"
        row["finding"] += "</ul>"

        pdf_data.append(row)
        idx += 1

    return pdf_data


class User:
    """
    Extracts the user and tenant id from the jwt of a request sent to an endpoint.
    Used for user validation.
    """

    def __init__(self, event):
        self.user_id = "e75d9c98-d162-439f-a641-3f376c8729a1"
        #self.user_id = event['requestContext']['authorizer']['jwt']['claims']['sub']
        try:
            self.tenant_id = event['requestContext']['authorizer']['jwt']['claims']['custom:tenant_id']  # NOT IMPLEMENTED YET
        except:
            pass 


def validate_user(event, request_user_id):
    connection = sql_functions.make_connection()

    user = User(event)
    user_id = sql_functions.retrieve_rows_safe(connection,
                                               "SELECT ic.user_id FROM company ic WHERE ic.id = %s",
                                               (request_user_id,))[0][0]
    if user_id != user.user_id:
        logging.error("User validation failed....")
        return {'statusCode': 403,
                'headers': {'Content-Type': 'application/json'},
                }

    logging.info("User validation passed....")
    return
