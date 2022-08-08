import checkdmarc
import logging
import requests
from src.lib.scanners.flareAPI import FlareAPI
from src.lib.scanners.shodanAPI import ShodanAPI
from src.lib.scanners.header_scanner import HeaderScanner
from src.lib.scanners.eval_risk import eval_risk, get_recs


def email_security_check(domain):
    """
    this function is checks the domain for the required email DNS records (DMARC and SPF)
    :param domain:    domain to be scanned
    :type domain:     string
    """
    results = checkdmarc.check_domains([domain])
    return results


def delete_identifier(id):
    flare_base_url = "https://api.flared.io"
    flare_api_key = "fw_pLsSHtlviSBiAwlHAmYYhNiZITrCZrCnOVHIHvmC"
    flare_client = FlareAPI(flare_base_url, flare_api_key)
    print("checking the id: ", id)
    response = flare_client.delete_domain(id)

    return response


def scan_domain(name, domain):
    flare_base_url = "https://api.flared.io"
    flare_api_key = "fw_pLsSHtlviSBiAwlHAmYYhNiZITrCZrCnOVHIHvmC"
    shodan_api_key = "atj5KW3BHFbYUwVYWWNfP6ZhXBxvVkA8"

    flare_client = FlareAPI(flare_base_url, flare_api_key)
    shodan_client = ShodanAPI(shodan_api_key)

    try:
        logging.info("Creating new flare asset....")
        new_asset = flare_client.add_new_domain(name, domain)

        _id = new_asset["asset"]["id"]

        try:
            # check marketplace mentions in darkweb
            logging.info('Checking marketplace mentions....')
            marketplace_results = flare_client.check_marketplace(_id)
        except Exception as e:
            logging.exception(e)
            marketplace_results = {"error": str(e)}

        try:
            # get list of subdomains
            subdomains = flare_client.subdomains(_id)
            print("Subdomain" + str(subdomains))
            logging.info('Checking domain and subdomains on Shodan....')
            subdomains_results = shodan_client.scan_subdomains(subdomains)

        except Exception as e:
            logging.exception(e)
            try:
                subdomain_names = ['mail', 'mail2', 'www', 'ns2', 'ns1', 'blog', 'localhost', 'm', 'ftp', 'mobile',
                                   'ns3', 'smtp', 'search', 'api', 'dev', 'secure', 'webmail', 'admin', 'img', 'news',
                                   'sms', 'marketing', 'test', 'video', 'www2', 'media', 'static', 'ads', 'mail2',
                                   'beta', 'wap', 'blogs', 'download', 'dns1', 'www3', 'origin', 'shop', 'forum',
                                   'chat', 'www1', 'image', 'new', 'tv', 'dns', 'services', 'music', 'images', 'pay',
                                   'ddrint', 'conc']
                validated_subdomain = []

                for subdomain in subdomain_names:
                    url = f"https://{subdomain}.{domain}"
                    try:
                        requests.get(url, timeout=5)
                        validated_subdomain.append(f'{subdomain}.{domain}')

                    except:
                        pass
                print("validated_subdomain: " + str(validated_subdomain))
                subdomains_results = shodan_client.scan_subdomains(validated_subdomain)
            except Exception as e:
                logging.exception(e)
                subdomains_results = {"error": str(e)}

        # Delete asset since there's a cap on maximum number of assets that can be created
        logging.info('Deleting asset from Flare....')
        flare_client.delete_domain(_id)

    except Exception as e:
        logging.exception(e)
        new_asset = {"error": str(e)}
        marketplace_results = {"error": str(e)}
        subdomains_results = {"error": str(e)}

    try:
        # perform scans
        logging.info('Checking leaked creds....')
        leaked_creds = flare_client.check_leaked_creds(domain)
    except Exception as e:
        logging.exception(e)
        leaked_creds = {"error": str(e)}

    try:
        # check email security
        logging.info('Checking email DNS records....')
        email_security = email_security_check(domain)
    except Exception as e:
        logging.exception(e)
        email_security = {"error": str(e)}

    try:
        # check web headers
        logging.info('Checking web headers....')
        web_headers = HeaderScanner(domain).run()
    except Exception as e:
        logging.exception(e)
        web_headers = {"error": str(e)}

    scan_results = {"asset": new_asset,
                    "credentials": leaked_creds,
                    "marketplace": marketplace_results,
                    "subdomains": subdomains_results,
                    "email_security": email_security,
                    "web_headers": web_headers
                    }

    risk_results = eval_risk(scan_results)
    risk_recs = get_recs(scan_results)

    results = {"data": scan_results, "risk_results": risk_results, "risk_recommendations": risk_recs}

    return results