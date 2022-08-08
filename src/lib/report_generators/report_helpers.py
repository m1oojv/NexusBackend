from copy import copy
from datetime import datetime

from src.lib.scanners.risk_recommendations import risk_recommendations
from src.lib.report_generators.raw_data import vulns_data, leaked_creds_data


def get_prelim_pdf_data(raw_pdf_data):
    """
    Returns data that will be used when generating a prelim PDF report of the company's risk assessment.
    Output data structure: {"company": "string",
                            "doc_date": "string",
                            "exposure_amt": float,
                            "risk_counts": {"low": int,
                                            "medium": int,
                                            "high": int
                                            },
                            "email_misconfig_count": int,
                            "threat_category": [{"risk": int,
                                                 "threatCategory": "string"
                                                 },
                                                 ...
                                                ],
                            "leaked_creds": {"latest": [{"email": "string",
                                                         "hash": "string",
                                                         "date": "DD/MM/YYYY",
                                                         "source": "string"
                                                         },
                                                         ...
                                                        ],
                                             "count": int,
                                             "percentile": float,
                                             "median": int
                                             },
                            "vulns": {"count": int,
                                      "percentile": float,
                                      "median": int
                                      }
                            }

    :param raw_pdf_data:    Raw data of the company from scanResults (after passing through filter_scan_results)
    :type raw_pdf_data:     dict
    """

    pdf_data = {"company": get_company_name(raw_pdf_data),
                "doc_date": get_application_date(raw_pdf_data),
                "exposure_amt": get_overall_risk(raw_pdf_data),
                "risk_counts": get_risk_counts(raw_pdf_data),
                "email_misconfig_count": get_email_misconfig_count(raw_pdf_data),
                "threat_category": get_threat_cat_risk(raw_pdf_data),
                "leaked_creds": {"latest": get_leaked_creds(raw_pdf_data, n=5, mask_email=True),
                                 "count": get_leaked_creds_count(raw_pdf_data),
                                 "percentile": get_leaked_creds_percentile(raw_pdf_data),
                                 "median": get_leaked_creds_median(raw_pdf_data),
                                 },
                "vulns": {"count": get_vulns_count(raw_pdf_data),
                          "percentile": get_vulns_percentile(raw_pdf_data),
                          "median": get_vulns_median(raw_pdf_data),
                          },
                }

    return pdf_data


def get_full_pdf_data(raw_pdf_data):
    """
    Returns data that will be used when generating a prelim PDF report of the company's risk assessment.
    Output data structure: {"company": "string",
                            "doc_date": "string",
                            "exposure_amt": float,
                            "risk_counts": {"low": int,
                                            "medium": int,
                                            "high": int
                                            },
                            "email_misconfig_count": int,
                            "threat_category": [{"risk": int,
                                                 "threatCategory": "string"
                                                 },
                                                 ...
                                                ],
                            "leaked_creds": {"latest": [{"email": "string",
                                                         "hash": "string",
                                                         "date": "DD/MM/YYYY",
                                                         "source": "string"
                                                         },
                                                         ...
                                                        ],
                                             "data": [{"email": "string",
                                                       "hash": "string",
                                                       "date": "DD/MM/YYYY",
                                                       "source": "string"
                                                       },
                                                       ...
                                                      ],
                                             "count": int,
                                             "percentile": "string",
                                             "median": int
                                             },
                            "vulns": {"data": [{"ip": "string",
                                                "cve": "string",
                                                "cvss": float,
                                                "summary": "string"
                                                },
                                                ...
                                               ],
                                      "count": int,
                                      "percentile": "string",
                                      "median": int
                                      },
                            "insecure_headers_count": int,
                            "exposed_service_count": int,
                            "marketplace_mentions": {"total_count": int,
                                                     "data": [{"name": "string",
                                                               "count": int
                                                               },
                                                               ...
                                                              ]
                                                     },
                            "finding": [{"area": "string",
                                         "finding": "string",
                                         "rec": "string",
                                         "impact": "string",
                                         "level": "string"
                                         },
                                         ...
                                        ]
                            }

    :param raw_pdf_data:    Raw data of the company from scanResults (after passing through filter_scan_results)
    :type raw_pdf_data:     dict
    """

    pdf_data = {"company": get_company_name(raw_pdf_data),
                "doc_date": get_application_date(raw_pdf_data),
                "exposure_amt": get_overall_risk(raw_pdf_data),
                "risk_counts": get_risk_counts(raw_pdf_data),
                "email_misconfig_count": get_email_misconfig_count(raw_pdf_data),
                "threat_category": get_threat_cat_risk(raw_pdf_data),
                "leaked_creds": {"latest": get_leaked_creds(raw_pdf_data, n=5, mask_email=False),
                                 "data": get_leaked_creds(raw_pdf_data),
                                 "count": get_leaked_creds_count(raw_pdf_data),
                                 "percentile": get_leaked_creds_percentile(raw_pdf_data),
                                 "median": get_leaked_creds_median(raw_pdf_data),
                                 },
                "vulns": {"data": get_vulns(raw_pdf_data),
                          "count": get_vulns_count(raw_pdf_data),
                          "percentile": get_vulns_percentile(raw_pdf_data),
                          "median": get_vulns_median(raw_pdf_data),
                          },
                "insecure_headers_count": get_insecure_headers_count(raw_pdf_data),
                "exposed_service_count": get_exposed_service_count(raw_pdf_data),
                "marketplace_mentions": {"total_count": get_marketplace_mentions_count(raw_pdf_data),
                                         "data": get_marketplace_mentions(raw_pdf_data)
                                         },
                "findings": get_findings(raw_pdf_data),
                }

    return pdf_data


def get_leaked_creds(raw_pdf_data, n=200, mask_email=False):
    """
    Returns a list of leaked credentials details in the correct format.
    :param raw_pdf_data:    Raw data of the company from scanResults (after passing through filter_scan_results)
    :type raw_pdf_data:     dict
    :param n:    max number of leaked credentials to return. Do not increase this value too much as the lambda function
                 will fail.
    :type n:     int
    :param mask_email:    flag to mask the email addresses returned
    :type mask_email:     bool
    """
    leaked_creds = [{"email": user["name"],
                     "hash": passwd["hash"],
                     "date": passwd["imported_at"],
                     "source": passwd["source_id"]
                     } for user in raw_pdf_data["scanResults"]["data"]["credentials"]["leaked_data"]
                    for passwd in user["passwords"]
                    ]
    leaked_creds.sort(key=lambda leaked_cred: leaked_cred["date"], reverse=True)
    leaked_creds = leaked_creds[:n]  # TODO: TRY EXCEPT TO ENSURE INTEGER VALUE FOR N
    for i, leaked_cred in enumerate(leaked_creds):
        leaked_cred["date"] = datetime.strptime(leaked_cred["date"].split('T')[0], "%Y-%m-%d").strftime("%d/%m/%Y")
        if mask_email:
            leaked_cred["email"] = get_mask_email(leaked_cred["email"])
    return leaked_creds


def get_threat_cat_risk(raw_pdf_data):
    """
    Returns a list of threat categories and how much risk is associated with each category.
    :param raw_pdf_data:    Raw data of the company from scanResults (after passing through filter_scan_results)
    :type raw_pdf_data:     dict
    """
    threat_categories = raw_pdf_data["financials"]["threatCategory"]["data"]
    threat_categories_sorted = sorted(threat_categories, key=lambda d: d['risk'])
    return threat_categories_sorted


def get_exposed_service_count(raw_pdf_data):
    """
    Returns the number of exposed services.
    :param raw_pdf_data:    Raw data of the company from scanResults (after passing through filter_scan_results)
    :type raw_pdf_data:     dict
    """
    ports = raw_pdf_data["scanResults"]["data"]["ports"]
    exposed_service_count = ports["totalNumberOfHighRisk"] + ports["totalNumberOfMediumRisk"]
    return exposed_service_count


def get_insecure_headers_count(raw_pdf_data):
    web_headers = raw_pdf_data["scanResults"]["data"]["web_headers"]
    if "error" in web_headers.keys():
        return 0
    insecure_cookie_headers_count = sum(
        [(not cookie["secure"]) + (not cookie["httponly"]) for cookie in web_headers["cookies"]])
    insecure_headers_count = (not web_headers["xxss"]) + (not web_headers["nosniff"]) + (not web_headers["xframe"]) + (
        not web_headers["hsts"]) + (not web_headers["policy"]) + insecure_cookie_headers_count
    return insecure_headers_count


def get_company_name(raw_pdf_data):
    return raw_pdf_data["companyName"]


def get_application_date(raw_pdf_data):
    """
    Returns the date on which the risk assessment was ran.
    :param raw_pdf_data:    Raw data of the company from scanResults (after passing through filter_scan_results)
    :type raw_pdf_data:     dict
    """
    return raw_pdf_data["applicationDatetime"].strftime("%d %b %Y")


def get_overall_risk(raw_pdf_data):
    return raw_pdf_data["financials"]["risk"]


def get_risk_counts(raw_pdf_data):
    risk_counts = {"low": 0, "medium": 0, "high": 0}
    for risk_score in raw_pdf_data["scanResults"]["risk_results"].values():
        if risk_score == 1:
            risk_counts["low"] += 1
        elif risk_score >= 2 and risk_score != 5:
            risk_counts["medium"] += 1
        else:
            risk_counts["high"] += 1
    return risk_counts


def get_leaked_creds_count(raw_pdf_data):
    """
    Returns the total number of leaked credentials exposed. May indicate more credentials than retrieved by
    get_leaked_creds since get_leaked_creds have an upper limit on the number of credentials returned.
    :param raw_pdf_data:    Raw data of the company from scanResults (after passing through filter_scan_results)
    :type raw_pdf_data:     dict
    """
    return raw_pdf_data["scanResults"]["data"]["credentials"]["total_creds_exposed"]


def get_vulns_count(raw_pdf_data):
    return raw_pdf_data["scanResults"]["data"]["vulns"]["totalNumberOfVulns"]


def get_vulns(raw_pdf_data):
    return raw_pdf_data["scanResults"]["data"]["vulns"]["data"]


def get_email_misconfig_count(raw_pdf_data):
    spf_validity = raw_pdf_data["scanResults"]["data"]["email_security"]["spf"]["valid"]
    dmarc_validity = raw_pdf_data["scanResults"]["data"]["email_security"]["dmarc"]["valid"]
    email_misconfig_count = int(not spf_validity) + int(not dmarc_validity)
    return email_misconfig_count


def get_leaked_creds_percentile(raw_pdf_data):
    """
    Calculates the percentile of a the number of leaked credentials a company has against the number of leaked
    credentials other companies in the same category has.
    """
    employees_count = int(raw_pdf_data["employees"])
    leaked_creds_count = get_leaked_creds_count(raw_pdf_data)

    category = employees_count2org_cat(employees_count)
    data = leaked_creds_data[category]
    leaked_creds_percentile = add_suffix(calc_percentile(data, leaked_creds_count))

    return leaked_creds_percentile


def get_leaked_creds_median(raw_pdf_data):
    """
    Calculates the median number of leaked_credentials across all companies in a particular category (small, medium,
    large, enterprise).
    """
    employees_count = int(raw_pdf_data["employees"])
    leaked_creds_count = get_leaked_creds_count(raw_pdf_data)

    category = employees_count2org_cat(employees_count)
    data = leaked_creds_data[category]
    leaked_creds_median = calc_median(data, leaked_creds_count)

    return leaked_creds_median


def get_vulns_percentile(raw_pdf_data):
    """
    Calculates the percentile of a the number of vulnerabilities a company has against the number of vulnerabilities
    other companies in the same category has.
    """
    employees_count = int(raw_pdf_data["employees"])
    vulns_count = get_vulns_count(raw_pdf_data)

    category = employees_count2org_cat(employees_count)
    data = vulns_data[category]
    vulns_percentile = add_suffix(calc_percentile(data, vulns_count))

    return vulns_percentile


def get_vulns_median(raw_pdf_data):
    """
    Calculates the median number of vulnerabilities across all companies in a particular category (small, medium,
    large, enterprise).
    """
    employees_count = int(raw_pdf_data["employees"])
    vulns_count = get_vulns_count(raw_pdf_data)
    category = employees_count2org_cat(employees_count)
    data = vulns_data[category]
    vulns_median = calc_median(data, vulns_count)

    return vulns_median


def get_marketplace_mentions_count(raw_pdf_data):
    marketplace_mentions_count = len(raw_pdf_data["scanResults"]["data"]["marketplace"])
    return marketplace_mentions_count


def get_marketplace_mentions(raw_pdf_data):
    marketplaces = raw_pdf_data["scanResults"]["data"]["marketplace"]
    marketplace_names = [market["source"] for market in marketplaces]
    marketplace_names_unique = set(marketplace_names)
    marketplace_data = [{"name": name, "count": marketplace_names.count(name)} for name in marketplace_names_unique]
    return marketplace_data


def get_mask_email(email):
    location = email.find('@')
    masked_email = email[:3] + "***" + email[location:]

    return masked_email


def calc_percentile(numbers, x):
    """
    Calculate the percentile of a value in a list of numbers.
    :param numbers:  list of integers
    :type numbers:   list
    :param x:    value to calculate the percentile for
    :type x:     int
    """
    numbers.sort()
    pos = len(numbers)
    for idx, num in enumerate(numbers):
        if num >= x:
            pos = idx
            break
    return round((1 - pos / (len(numbers) + 1)) * 100)


def add_suffix(x):
    """
    Adds a suffix to the given integer.
    :param x:  number to add a suffix to.
    :type x:   int
    """
    last_digit = x % 10
    if last_digit == 1:
        x_suffix = f"{x}st"
    elif last_digit == 2:
        x_suffix = f"{x}nd"
    elif last_digit == 3:
        x_suffix = f"{x}rd"
    else:
        x_suffix = f"{x}th"
    return x_suffix


def calc_median(numbers, x):
    """
    Calculate the median in a list of numbers after including .

    :param numbers:  list of integers
    :type numbers:   list
    :param x:    included here just for consistency
    :type x:     int
    """
    new_numbers = copy(numbers)
    new_numbers.append(x)
    new_numbers.sort()
    return round(numbers[int(len(numbers) / 2)])


def employees_count2org_cat(employees_count):
    """
    Returns the size of an organization given the number of employees of the company.
    According to Nixon, the categories are tentatively as follows:
        Small - < 50 employees
        Medium - >= 50 and <= 250
        Large - > 250 and <= 5000
        Enterprise - > 5000
    :param employees_count:  Number of employees in company
    :type employees_count:   int
    """
    if employees_count < 50:
        return "small"
    elif employees_count < 251:
        return "medium"
    elif employees_count < 5001:
        return "large"
    else:
        return "enterprise"


def get_findings(raw_pdf_data):
    """
    Returns nice clean data that will be used when generating a PDF report of the company's
    risk assessment.
    Output data structure: [{"area": risk_area,
                             "finding": findings,
                             "rec": report recommendations,
                             "impact": impact,
                             "level": risk_level
                             }]
    TODO: Find a way to streamline this function (and probably how the data are stored in the
          database to minimize the need to manipulate the data after extracting it from the
          database.
    """
    scan_results = raw_pdf_data["scanResults"]
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
                        5: "High Risk"
                        }
    pdf_data = []
    for rec_name, rec_details in scan_results["risk_recommendations"].items():
        # If there are no findings, use default no abnormalities found
        if not rec_details["details"]:
            row = {"area": rec_details["area"],
                   "finding": "No abnormalities found.",
                   "rec": "",
                   "impact": rec_details["impact"],
                   "level": "Low Risk",
                   }
            pdf_data.append(row)
            continue
        # Ports will be included into the pdf data at the end of this function
        if rec_name == "ports_rec":
            continue
        for detail in rec_details["details"]:
            row = {"area": rec_details["area"],
                   "finding": detail['finding'],
                   "rec": detail['report_rec'],
                   "impact": rec_details["impact"],
                   "level": score2risk_level[scan_results["risk_results"][recs2score[rec_name]]]
                   }

            # For these recommendation fields, add in extra data to their findings column
            if rec_name == "creds_rec":
                row["finding"] += " A full list of credentials (Up to 200 credentials) may be found in the Appendix."

            if rec_name == "vulns_rec":
                row["finding"] += " A full list of vulnerabilities can be found in the Appendix."

            # Each individual web header risk is hardcoded to be medium.
            # This is so as the original risk level is an overall risk level for all headers together.
            if rec_name == "web_headers_rec":
                row["level"] = "Medium Risk"
            pdf_data.append(row)

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
        row = {"area": risk_recommendations["ports"]["area"],
               "finding": risk_recommendations["ports"]["details"][port]['finding'],
               "level": details["level"],
               "rec": risk_recommendations["ports"]["details"][port]['report_rec'],
               "impact": risk_recommendations["ports"]["impact"],
               }

        pdf_data.append(row)

    return pdf_data
