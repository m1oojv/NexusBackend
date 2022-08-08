import json
import logging
import socket
import shodan
from src.lib.scanners.utils import get_ips_by_dns_lookup, categorize_ports


class ShodanQueryObject:
    """
    Holds all information on a shodan query. Helps to filter out useful information.
    :param ip:    ip address used in the shodan query
    :type ip:     str
    :param data:     data from a shodan query
    :type data:    dict
    """
    def __init__(self, ip, data):
        self.ip = ip
        self.data = data
        self.ports = self.get_ports()
        self.vulns = self.get_vulns()
        self.exposure = self.get_exposure()
        self.vulns_exists = self.get_vulns_exists()
        self.ssl_expiry_exists = self.get_ssl_expiry_exists()
        self.ssl_self_signed_exists = self.get_ssl_self_signed_exists()

    def __str__(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def check_ssl_self_signed(ssl):
        return len(ssl['chain']) == 1 and ssl['cert']['issuer'] == ssl['cert']['subject']

    def to_dict(self):
        """
        Returns all useful information stored in the form of a dictionary.
        """
        return {"ip": self.ip,
                "ports": self.ports,
                "vulns": self.vulns,
                "exposure": self.exposure,
                "exposure_exists": {"vulns_exists": self.vulns_exists,
                                    "ssl_expiry_exists": self.ssl_expiry_exists,
                                    "ssl_self_signed_exists": self.ssl_self_signed_exists
                                    }
                }

    def get_ports(self):
        return categorize_ports(self.data["ports"])

    def get_vulns(self):
        return self.data["vulns"] if "vulns" in self.data.keys() else []

    def get_exposure(self):
        exposure = []
        for raw_data in self.data['data']:
            service = {"service": raw_data['_shodan']['module'],
                       "port": raw_data['port'],
                       }
            if 'vulns' in raw_data.keys():
                service['vulns'] = raw_data['vulns']
            if 'ssl' in raw_data.keys():
                service['ssl_expiry'] = raw_data['ssl']['cert']['expired']
                service["ssl_self_signed"] = self.check_ssl_self_signed(raw_data['ssl'])
            exposure.append(service)
        return exposure

    def get_vulns_exists(self):
        return "vulns" in self.data.keys() and self.data["vulns"]

    def get_ssl_expiry_exists(self):
        for raw_data in self.data['data']:
            if 'ssl' in raw_data.keys() and raw_data['ssl']['cert']['expired']:
                return True
        return False

    def get_ssl_self_signed_exists(self):
        for raw_data in self.data['data']:
            if 'ssl' in raw_data.keys() and self.check_ssl_self_signed(raw_data['ssl']):
                return True
        return False


class ShodanAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api = shodan.Shodan(api_key)

    def query(self, ip, max_tries=3):
        ip_data = dict()
        for i in range(max_tries):
            try:
                ip_data = self.api.host(ip)
                break
            except shodan.exception.APITimeout as e:
                if i == max_tries - 1:
                    ip_data = {"error": str(e)}
                else:
                    continue
            except shodan.exception.APIError as e:
                ip_data = {"error": str(e)}
                break
        return ip_data

    def scan_subdomains(self, subdomains, max_subdomains=75):
        data = list()
        subdomain2ip = dict()
        if len(subdomains) > 75:
            logging.info(f"Too many subdomains, reducing to {max_subdomains} subdomains....")
            subdomains = subdomains[:75]
        logging.info(f"Total number of subdomains: {len(subdomains)}")
        for subdomain in subdomains:
            try:
                ips = get_ips_by_dns_lookup(subdomain)
            except socket.gaierror:
                continue
            subdomain2ip[subdomain] = ips

        # Reduce the number of IPs in case there's too many
        total_ip_count = sum([len(x) for x in subdomain2ip.values()])
        if total_ip_count > max_subdomains * 2:
            logging.info("Too many IPs to scan, reducing to 2 per subdomains....")
            for subdomain, ips in subdomain2ip.items():
                subdomain2ip[subdomain] = subdomain2ip[subdomain][:2]
        logging.info(f"Total number of IPs: {sum([len(x) for x in subdomain2ip.values()])}")

        for subdomain, ips in subdomain2ip.items():
            subdomain_data = dict()
            subdomain_data['name'] = subdomain
            subdomain_data['data'] = []
            for ip in ips:
                query_data = self.query(ip)
                if "error" in query_data.keys():
                    subdomain_data['data'].append(query_data)
                else:
                    subdomain_data['data'].append(ShodanQueryObject(ip, query_data).to_dict())
            data.append(subdomain_data)
        return data
