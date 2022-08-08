import socket


def filter_dict_keys(dictionary, keys):
    """Filters a dict by only including certain keys."""
    key_set = set(keys) & set(dictionary.keys())
    return {key: dictionary[key] for key in key_set}


# Query shodan for website enumeration
def get_ips_by_dns_lookup(target, port=None):
    """
    this function takes the passed target and optional port and does a dns
    lookup. it returns the ips that it finds to the caller.

    :param target:  the URI that you'd like to get the ip address(es) for
    :type target:   string
    :param port:    which port do you want to do the lookup against?
    :type port:     integer
    :returns ips:   all of the discovered ips for the target
    :rtype ips:     list of strings
    """

    if not port:
        port = 443

    return list(map(lambda x: x[4][0], socket.getaddrinfo('{}.'.format(target), port, type=socket.SOCK_STREAM)))


def categorize_ports(ports):
    ports = set(ports)
    high_risk_ports = {9200, 445}
    medium_risk_ports = {8888, 8081, 8080, 5432, 3389}
    return {"high": list(ports & high_risk_ports),
            "medium": list(ports & medium_risk_ports),
            "low": list(ports - high_risk_ports - medium_risk_ports)}
