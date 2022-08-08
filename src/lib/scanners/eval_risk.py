from datetime import datetime, timezone
import logging
from math import ceil
from src.lib.scanners.risk_recommendations import risk_recommendations


###################
# Get risk scores #
###################


def eval_creds_score(creds_results):
    """
    Evaluate the cyber risk that is a result of leaked credentials.
    Ranges from 1 to 5. 1 being the best score (Least risk), 5 being the worst (Most risk).
    Algorithm: If no credentials were leaked:                    score = 1
               If credentials were leaked more than 90 days ago: score = 3
               If credentials were leaked in the past 90 days:   score = 5
    :param creds_results:    credentials json from the results of scan_domain
    :type creds_results:     dict
    """
    logging.info("Evaluating credentials score....")
    if "error" in creds_results.keys():  # Return None if an error is present
        return None
    creds = creds_results["leaked_data"]
    creds_score = 1
    for cred in creds:
        name = cred["name"]
        passwds = cred["passwords"]
        for passwd in passwds:
            # Get datetime at which the credential is leaked
            leaked_dt = datetime.strptime(passwd["imported_at"], "%Y-%m-%dT%H:%M:%S.%f%z")

            time_interval = datetime.now(timezone.utc) - leaked_dt
            logging.debug(f"Credential: {name}, Days since leaked: {time_interval.days}")

            if time_interval.days > 90 and creds_score < 3:
                creds_score = 3
            elif time_interval.days <= 90:
                creds_score = 5
                return creds_score  # Terminate early since the max score is reached

    return creds_score


def eval_vulns_score(subdomain_results):
    """
    Evaluate the cyber risk that is a result of known CVE vulnerabilities.
    Ranges from 1 to 5. 1 being the best score (Least risk), 5 being the worst (Most risk).
    Algorithm: ceiling(max(CVSS scores) / 2)
               Divide by 2 since CVSS scores range form 0 to 10 but we want it to range from 1 to 5.
    :param subdomain_results:    subdomains json from the results of scan_domain
    :type subdomain_results:     dict
    """
    logging.info("Evaluating vulnerability score....")
    if type(subdomain_results) == dict and "error" in subdomain_results.keys():  # Return None if an error is present
        return None
    max_cvss = 1
    for subdomain in subdomain_results:
        for ip in subdomain["data"]:
            if "error" in ip.keys():
                continue
            for service in ip["exposure"]:
                if "vulns" in service.keys():  # vulns key will only be present if the service has a CVE(s)
                    for cve, cve_details in service["vulns"].items():
                        logging.debug(f"CVE: {cve}, CVSS: {cve_details['cvss']}")
                        cvss = float(cve_details["cvss"])
                        max_cvss = max(cvss, max_cvss)

    logging.debug(f"Max CVSS score: {max_cvss}")
    score = max(1, ceil(max_cvss / 2))  # Score may equal to 0 but we want the minimum score to be 1

    return score


def eval_ports_score(subdomain_results):
    """
    Evaluates the cyber risk that is a result of open ports.
    Ranges from 1 to 5. 1 being the best score (Least risk), 5 being the worst (Most risk).
    Algorithm: max(port_risk_level) = LOW:    score = 1
               max(port_risk_level) = MEDIUM: score = 3
               max(port_risk_level) = HIGH:   score = 5
    :param subdomain_results:    subdomains json from the results of scan_domain
    :type subdomain_results:     dict
    """
    logging.info("Evaluating port score....")
    if type(subdomain_results) == dict and "error" in subdomain_results.keys():  # Return None if an error is present
        return None
    max_severity = 1
    for subdomain in subdomain_results:
        for ip in subdomain["data"]:
            if "error" in ip.keys():
                continue
            ports = ip["ports"]  # Get ports that are opened for each IP address
            logging.debug(f"Ports: {ports}")
            if ports["high"]:
                max_severity = 5
                return max_severity  # Terminate early since max severity is reached
            elif ports["medium"] and max_severity < 3:
                max_severity = 3
    logging.debug(f"Max port severity: {max_severity}")
    return max_severity


def eval_ssl_expiry_score(subdomain_results):
    """
    Evaluates the cyber risk that is a result of expired SSL certificates.
    Ranges from 1 to 5. 1 being the best score (Least risk), 5 being the worst (Most risk).
    Algorithm: If no SSL certs or no expired SSL certs: score = 1
               If there are expired SSL certs: score = ceiling(proportion of expired SSL certs * 2 + 3)
    :param subdomain_results:    subdomains json from the results of scan_domain
    :type subdomain_results:     dict
    """
    logging.info("Evaluating ssl expiry score....")
    if type(subdomain_results) == dict and "error" in subdomain_results.keys():  # Return None if an error is present
        return None
    tot_ssl_certs = 0
    tot_ssl_expired_certs = 0
    for subdomain in subdomain_results:
        for ip in subdomain["data"]:
            if "error" in ip.keys():
                continue
            for service in ip["exposure"]:
                if "ssl_expiry" in service.keys():
                    tot_ssl_certs += 1
                    if service["ssl_expiry"]:
                        tot_ssl_expired_certs += 1
    logging.debug(f"Total SSL certs: {tot_ssl_certs}")
    logging.debug(f"Expired SSL certs: {tot_ssl_expired_certs}")

    # If there are no SSL certs or no expired SSL certs
    if not tot_ssl_certs or not tot_ssl_expired_certs:
        return 1
    else:
        return ceil((tot_ssl_expired_certs / tot_ssl_certs) * 2) + 3


def eval_marketplace_score(marketplace_results):
    """
    Evaluates the cyber risk that is a result of open ports.
    Ranges from 1 to 5. 1 being the best score (Least risk), 5 being the worst (Most risk).
    Algorithm: there are no marketplace mentions: score = 1
               there are marketplace mentions:    score = 5
    :param marketplace_results:    marketplace json from the results of scan_domain
    :type marketplace_results:     dict
    """
    logging.info("Evaluating marketplace score....")

    if "error" in marketplace_results.keys():  # Return None if an error is present in the data
        return None

    logging.debug(f"Marketplace results: {marketplace_results['items']}")
    if marketplace_results["items"]:
        return 5
    else:
        return 1


def eval_email_security_score(email_security_results):
    """
    Evaluates the cyber risk that is a result of missing email DNS records (DMARC and SPF).
    Ranges from 1 to 5. 1 being the best score (Least risk), 5 being the worst (Most risk).
    Algorithm: DMARC and SPF configured correctly:                             score = 1
               SPF configured correctly, DMARC pct parameter not equal to 100: score = 2
               SPF configured correctly, DMARC not implemented:                score = 3
               SPF not implemented, DMARC configured correctly:                score = 4
               SPF and DMARC not implemented:                                  score = 5
    :param email_security_results:    email security json from the results of scan_domain
    :type email_security_results:     dict
    """
    logging.info("Evaluating email security score....")
    # Return None if an error is present in the data
    if type(email_security_results) == list or "error" in email_security_results.keys():
        return None

    spf = email_security_results["spf"]
    dmarc = email_security_results["dmarc"]
    spf_valid = spf["valid"]
    dmarc_valid = dmarc["valid"]
    if dmarc_valid:
        dmarc_pct_100 = dmarc["tags"]["pct"]["value"] == 100
    else:
        dmarc_pct_100 = False

    logging.debug(f"SPF valid: {spf_valid}, DMARC valid: {dmarc_valid}, DMARC PCT: {dmarc_pct_100}")
    # Get score
    # TODO: COULD BE CLEARER
    if spf_valid and dmarc_valid:
        if dmarc_pct_100:
            return 1
        else:
            return 2
    elif spf_valid and not dmarc_valid:
        return 3
    elif not spf_valid and dmarc_valid:
        return 4
    else:
        return 5


def eval_sec_headers_score(sec_headers_results):
    """
    Evaluates the cyber risk that is a result of missing security headers.
    Ranges from 1 to 5. 1 being the best score (Least risk), 5 being the worst (Most risk).
    Algorithm: cookie = secure OR httponly
               score = 0.4 * xxss + 0.8 * nosniff + 0.8 * xframe + 0.8 * policy + 0.8 * cookie + 1.4 * hsts
    Relative severity of headers are referenced from : https://www.tenable.com/plugins/was/families
    :param sec_headers_results:    security headers json from the results of scan_domain
    :type sec_headers_results:     dict
    """
    logging.info("Evaluating web headers score....")
    if "error" in sec_headers_results.keys():  # Return 1 since there is no headers
        return 1

    # Check if all cookies have secure and httponly header
    secure_cookies = True  # Remains True if all cookies have the 'secure' header
    httponly_cookies = True  # Remains True if all cookies have the 'httponly' header
    for cookie in sec_headers_results["cookies"]:
        if not cookie["secure"]:
            secure_cookies = False
        if not cookie["httponly"]:
            httponly_cookies = False
        logging.debug(f"Cookie Name: {cookie['name']}, Secure: {cookie['secure']}, Httponly: {cookie['httponly']}")
        if not secure_cookies and not httponly_cookies:
            break  # Terminate early since both cookie headers are already False

    # Convert all booleans to 1 or 0
    # 1 being not implemented
    # 0 being implemented
    cookie_score = int(not (secure_cookies and httponly_cookies))
    xxss_score = int(not sec_headers_results["xxss"])
    nosniff_score = int(not sec_headers_results["nosniff"])
    xframe_score = int(not sec_headers_results["xframe"])
    hsts_score = int(not sec_headers_results["hsts"])
    policy_score = int(not sec_headers_results["policy"])

    logging.debug(f"Cookie score: {cookie_score}, "
                  f"Xxss_score: {xxss_score}, "
                  f"Nosniff_score: {nosniff_score}, "
                  f"Xframe_score: {xframe_score}, "
                  f"Hsts_score: {hsts_score}, "
                  f"Policy_score: {policy_score}"
                  )
    score = ceil(0.4 * xxss_score +
                 0.8 * nosniff_score +
                 0.8 * xframe_score +
                 0.8 * policy_score +
                 0.8 * cookie_score +
                 1.4 * hsts_score)

    return score


def eval_risk(scan_results):
    """
    Evaluates the cyber risk using the results obtained from scanning a domain.
    Ranges from 1 to 5. 1 being the best score (Least risk), 5 being the worst (Most risk).
    :param scan_results:    Results from scanning a domain
    :type scan_results:     dict
    """
    # Evaluate credentials
    logging.info("Evaluating risk scores....")
    creds_score = eval_creds_score(scan_results["credentials"])
    vulns_score = eval_vulns_score(scan_results["subdomains"])
    ports_score = eval_ports_score(scan_results["subdomains"])
    ssl_expiry_score = eval_ssl_expiry_score(scan_results["subdomains"])
    marketplace_score = eval_marketplace_score(scan_results["marketplace"])
    email_security_score = eval_email_security_score(scan_results["email_security"])
    web_headers_score = eval_sec_headers_score(scan_results["web_headers"])

    scores = {"creds_score": creds_score,
              "vulns_score": vulns_score,
              "ports_score": ports_score,
              "ssl_expiry_score": ssl_expiry_score,
              "marketplace_score": marketplace_score,
              "email_security_score": email_security_score,
              "web_headers_score": web_headers_score,
              }

    return scores


#######################
# Get recommendations #
#######################


def get_creds_rec(creds_results):
    """
    Get recommendations to reduce credentials risk based on scan results.
    Recommendations are based on whether any credentials have been leaked or not.
    :param creds_results:    credentials json from the results of scan_domain
    :type creds_results:     dict
    """
    logging.info("Getting recommendations for credentials scan results....")
    rec = {"area": risk_recommendations["creds"]["area"],
           "details": [],
           "impact": risk_recommendations["creds"]["impact"],
           }
    if "error" in creds_results.keys():
        # Don't return any rec if there's an error
        return rec

    has_creds_exposed = creds_results['total_creds_exposed'] > 0
    logging.debug(f"Has leaked credentials: {has_creds_exposed}")

    if has_creds_exposed:
        rec["details"].append(risk_recommendations["creds"]["details"][has_creds_exposed])
        # Get the latest day where a leak occurred
        latest_leak = datetime(1970, 1, 1)
        creds = creds_results["leaked_data"]
        for cred in creds:
            passwds = cred["passwords"]
            for passwd in passwds:
                # Get datetime at which the credential is leaked
                leaked_dt = datetime.strptime(passwd["imported_at"], "%Y-%m-%dT%H:%M:%S.%f%z").replace(tzinfo=None)
                latest_leak = max(latest_leak, leaked_dt)
        days_since_latest_leak = (datetime.now() - latest_leak).days
        leak_details = (f"<b>{creds_results['total_creds_exposed']} leaked credentials</b> discovered. "
                        f"The credentials were leaked <b>{days_since_latest_leak}</b> days ago."
                        )
        rec["details"][0]["finding"] = leak_details

    return rec


def get_vulns_rec(subdomain_results):
    """
    Get recommendations to reduce vulnerability risk based on scan results.
    Recommendations are based on whether any CVEs have been found or not.
    :param subdomain_results:    subdomains json from the results of scan_domain
    :type subdomain_results:     dict
    """
    logging.info("Getting recommendations for vulnerabilities scan results....")
    rec = {"area": risk_recommendations["vulns"]["area"],
           "details": [],
           "impact": risk_recommendations["vulns"]["impact"],
           }
    if type(subdomain_results) == dict and "error" in subdomain_results.keys():
        # Don't return any rec if there's an error
        return rec

    # Check how many vulnerabilities were found
    vulns_count = 0
    for subdomain in subdomain_results:
        for ip in subdomain["data"]:
            vulns_count += len(ip.get("vulns", []))
    if vulns_count > 0:
        logging.debug(f"{vulns_count} CVEs found.")
        rec["details"].append(risk_recommendations["vulns"]["details"][True])
        if vulns_count == 1:
            finding_str = f"<b>{vulns_count}</b> vulnerability was discovered. "
        else:
            finding_str = f"<b>{vulns_count}</b> vulnerabilities were discovered. "
        rec["details"][0]["finding"] = finding_str
    else:
        logging.debug("CVEs not found.")
    return rec


def get_ports_rec(subdomain_results):
    """
    Get recommendations to reduce port risk based on scan results.
    Recommendations are based on whether any high risk ports have been found or not.
    :param subdomain_results:    subdomains json from the results of scan_domain
    :type subdomain_results:     dict
    """
    logging.info("Getting recommendations for ports scan results....")
    rec = {"area": risk_recommendations["ports"]["area"],
           "details": [],
           "impact": risk_recommendations["ports"]["impact"],
           }
    if type(subdomain_results) == dict and "error" in subdomain_results.keys():
        # Don't return any rec if there's an error
        return rec

    all_high_ports = []
    all_medium_ports = []
    for subdomain in subdomain_results:
        for ip in subdomain["data"]:
            if "error" in ip.keys():
                continue
            all_high_ports += ip["ports"]["high"]
            all_medium_ports += ip["ports"]["medium"]
    all_high_ports = set(all_high_ports)
    all_medium_ports = set(all_medium_ports)
    logging.debug(f"High ports: {all_high_ports}")
    logging.debug(f"Medium ports: {all_medium_ports}")

    # Create the recommendation
    for port in all_high_ports:  # Build on rec for each high port
        rec["details"].append(risk_recommendations["ports"]["details"][port])
        # rec += (risk_recommendations["ports"]["details"][port]["rec"] + "<br/><br/>")

    for port in all_medium_ports:  # Build on rec for each medium port
        rec["details"].append(risk_recommendations["ports"]["details"][port])
        # rec += (risk_recommendations["ports"]["details"][port]["rec"] + "<br/><br/>")
    # rec = rec.strip()

    return rec


def get_ssl_expiry_rec(subdomain_results):
    """
    Get recommendations to reduce SSL expiry risk based on scan results.
    :param subdomain_results:    subdomains json from the results of scan_domain
    :type subdomain_results:     dict
    """
    logging.info("Getting recommendations for ssl_expiry scan results....")
    rec = {"area": risk_recommendations["ssl_expiry"]["area"],
           "details": [],
           "impact": risk_recommendations["ssl_expiry"]["impact"],
           }
    if type(subdomain_results) == dict and "error" in subdomain_results.keys():  # Return None if an error is present
        return rec
    for subdomain in subdomain_results:
        for ip in subdomain["data"]:
            if "error" in ip.keys():
                continue
            for service in ip["exposure"]:
                if service.get("ssl_expiry", False):
                    rec["details"].append(risk_recommendations["ssl_expiry"]["details"][True])
                    return rec

    return rec


def get_marketplace_rec(marketplace_results):
    """
    Get recommendations to reduce marketplace risk based on scan results.
    Recommendations are based on whether any details of the company is being sold on the darkweb marketplace.
    :param marketplace_results:    marketplace json from the results of scan_domain
    :type marketplace_results:     dict
    """
    logging.info("Getting recommendations for marketplace scan results....")
    rec = {"area": risk_recommendations["marketplace"]["area"],
           "details": [],
           "impact": risk_recommendations["marketplace"]["impact"],
           }
    if "error" in marketplace_results.keys():
        # Don't return any rec if there's an error
        return rec

    has_marketplace_mentions = bool(marketplace_results["items"])
    logging.debug(f"Marketplace mentions: {has_marketplace_mentions}")

    if has_marketplace_mentions:
        rec["details"].append(risk_recommendations["marketplace"]["details"][has_marketplace_mentions])
    return rec


def get_email_security_rec(email_security_results):
    """
    Get recommendations to reduce email security risk based on scan results.
    Recommendations are based on whether SPF and DMARC are implemented or not.
    :param email_security_results:    email security json from the results of scan_domain
    :type email_security_results:     dict
    """
    logging.info("Getting recommendations for email_security scan results....")
    rec = {"area": risk_recommendations["email_security"]["area"],
           "details": [],
           "impact": risk_recommendations["email_security"]["impact"],
           }
    if type(email_security_results) == list or "error" in email_security_results.keys():
        # Don't return any rec if there's an error
        return rec

    spf_valid = email_security_results["spf"]["valid"]
    dmarc_valid = email_security_results["dmarc"]["valid"]
    logging.debug(f"SPF valid: {spf_valid}, DMARC valid: {dmarc_valid}")

    # Create the recommendation
    if not spf_valid:
        rec["details"].append(risk_recommendations["email_security"]["details"]["spf"])
        # rec += (risk_recommendations["email_security"]["details"]["spf"]["rec"] + "<br/>")
    if not dmarc_valid:
        rec["details"].append(risk_recommendations["email_security"]["details"]["dmarc"])
        # rec += risk_recommendations["email_security"]["details"]["dmarc"]["rec"]
    # rec = rec.strip()

    return rec


def get_sec_headers_rec(sec_headers_results):
    """
    Get recommendations to reduce web security header risk based on scan results.
    Recommendations are based on whether the security headers are implemented or not.
    :param sec_headers_results:    security headers json from the results of scan_domain
    :type sec_headers_results:     dict
    """
    logging.info("Getting recommendations for security_headers scan results....")
    rec = {"area": risk_recommendations["security_headers"]["area"],
           "details": [],
           "impact": risk_recommendations["security_headers"]["impact"],
           }
    if "error" in sec_headers_results.keys():
        # Don't return any rec if there's an error
        return rec

    headers = [("nosniff", sec_headers_results["nosniff"]),
               ("xframe", sec_headers_results["xframe"]),
               ("hsts", sec_headers_results["hsts"]),
               ("policy", sec_headers_results["policy"])
               ]
    logging.debug(f"Headers: {headers}")

    # Create the recommendation
    for header, is_implemented in headers:
        if not is_implemented:
            rec["details"].append(risk_recommendations["security_headers"]["details"][header])
            # rec += (risk_recommendations["security_headers"]["details"][header]["rec"] + "<br/>")
    # rec = rec.strip()

    return rec


def get_recs(scan_results):
    """
    Get recommendations for a company based on results from scan_domain
    :param scan_results:    Results from scanning a domain
    :type scan_results:     dict
    """
    logging.info("Getting recommendations based on scan results....")
    creds_rec = get_creds_rec(scan_results["credentials"])
    vulns_rec = get_vulns_rec(scan_results["subdomains"])
    ports_rec = get_ports_rec(scan_results["subdomains"])
    ssl_expiry_rec = get_ssl_expiry_rec(scan_results["subdomains"])
    marketplace_rec = get_marketplace_rec(scan_results["marketplace"])
    email_security_rec = get_email_security_rec(scan_results["email_security"])
    web_headers_rec = get_sec_headers_rec(scan_results["web_headers"])

    recs = {"creds_rec": creds_rec,
            "vulns_rec": vulns_rec,
            "ports_rec": ports_rec,
            "ssl_expiry_rec": ssl_expiry_rec,
            "marketplace_rec": marketplace_rec,
            "email_security_rec": email_security_rec,
            "web_headers_rec": web_headers_rec,
            }

    return recs
