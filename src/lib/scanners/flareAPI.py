import requests
import logging
from math import ceil
from time import sleep

from src.lib.scanners.utils import filter_dict_keys


class FlareAPI:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        self.token = self.initialize()
        self.sleep_duration = 0.3

    def initialize(self):
        url = self.base_url + '/tokens/generate'
        req = requests.post(url, auth=('', self.api_key))
        data = req.json()
        return data['token']

    def get(self, path, max_tries=3):
        url = self.base_url + path
        for i in range(max_tries):
            try:
                response = requests.get(url, headers={'Authorization': 'Bearer ' + self.token}, timeout=120)
            except requests.exceptions.Timeout as e:
                logging.warning(f"Request timeout. Trying again...")
                if i < max_tries - 1:
                    sleep(self.sleep_duration)
                    continue
                else:
                    raise e
            if not response .status_code // 100 == 2:
                logging.warning(f"Unexpected response {response}")
                if i < max_tries - 1:
                    sleep(self.sleep_duration)
                    continue
            response.raise_for_status()
            json_obj = response.json()
            return json_obj

    def post(self, path, data, max_tries=3):
        url = self.base_url + path
        for i in range(max_tries):
            try:
                response = requests.post(url, headers={'Authorization': 'Bearer ' + self.token}, json=data)
            except requests.exceptions.Timeout as e:
                logging.warning(f"Request timeout. Trying again...")
                if i < max_tries - 1:
                    sleep(self.sleep_duration)
                    continue
                else:
                    raise e
            if not response .status_code // 100 == 2:
                logging.warning(f"Unexpected response {response}")
                if i < max_tries - 1:
                    sleep(self.sleep_duration)
                    continue
            response.raise_for_status()

            json_obj = response.json()
            return json_obj

    def put(self, path, data, max_tries=3):
        url = self.base_url + path
        for i in range(max_tries):
            try:
                response = requests.put(url, headers={'Authorization': 'Bearer ' + self.token}, json=data)
            except requests.exceptions.Timeout as e:
                logging.warning(f"Request timeout. Trying again...")
                if i < max_tries - 1:
                    sleep(self.sleep_duration)
                    continue
                else:
                    raise e
            if not response .status_code // 100 == 2:
                logging.warning(f"Unexpected response {response}")
                if i < max_tries - 1:
                    sleep(self.sleep_duration)
                    continue
            response.raise_for_status()

            json_obj = response.json()
            return json_obj

    def delete(self, path, data, max_tries=3):
        sleep_duration = 0.3
        url = self.base_url + path
        for i in range(max_tries):
            try:
                response = requests.delete(url, headers={'Authorization': 'Bearer ' + self.token}, json=data)
            except requests.exceptions.Timeout as e:
                logging.warning(f"Request timeout. Trying again...")
                if i < max_tries - 1:
                    sleep(sleep_duration)
                    continue
                else:
                    raise e
            if not response.status_code // 100 == 2:
                logging.warning(f"Unexpected response {response}")
                if i < max_tries - 1:
                    sleep(sleep_duration)
                    continue
            response.raise_for_status()
            json_obj = response.json()
            return json_obj

    @staticmethod
    def generate_asset_payload(name, domain):
        """
        this function is used to create the query payload for flare api

        :param name:  name of the company to be scanned
        :type name:   string
        :param domain:    domain to be scanned
        :type domain:     string
        """
        return (
            {
                "name": name,
                "data": {
                    "fqdn": domain,
                    "is_scanning_enabled": False,
                    "is_shadow_asset_relations_discovery_needed": True
                },
                "fetching_progress": 0,
                "id": 0,
                "risks": [],
                "search_types": [
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

    def add_new_domain(self, name, domain):
        payload = self.generate_asset_payload(name, domain)
        response = self.post('/firework/v2/assets/', payload)
        return response

    def delete_domain(self, _id):
        response = self.delete(f'/firework/v2/assets/{_id}', _id)
        return response

    def check_leaked_creds(self, domain):
        step = 200  # Max number of credentials that will be returned per request
        query_count = f"/firework/v2/activities/leak/leaksdb/{domain}/count"
        count = self.get(query_count)["count"]

        query_creds = f"/firework/v2/activities/leak/leaksdb/{domain}?order_by_desc=true&size={step}"
        creds_data = self.get(query_creds)

        # # Loop runs if the credentials request above cannot retrieve all credentials found (number of creds more than
        # # step variable).
        # # NOTE: If this for loop runs, there may be a few duplicate credentials in the data (probably due to the api).
        # #       Problem is very minor (so far got at most 6 duplicates in 30k credentials)
        # for _ in range(max(0, ceil(count / step) - 1)):
        #     min_id = creds_data['activity']['data']['identities'][-1]['passwords'][-1]['id']
        #     query_more_creds = (f"/firework/v2/activities/leak/leaksdb/{domain}?order_by_desc=true&size={step}&"
        #                         f"from={min_id}")
        #     more_creds_data = self.get(query_more_creds)
        #     creds_data['activity']['data']['identities'] += more_creds_data['activity']['data']['identities']

        return {"total_creds_exposed": count, "leaked_data": creds_data['activity']['data']['identities']}

    def subdomains(self, _id):
        url = f"https://api.flare.systems/firework/v3/identifiers/{_id}/children"
        data = requests.get(url, headers={'Authorization': 'Bearer ' + self.token}, timeout=5)
        data = data.json()
        sub_list = []
        
        data_subdomain = data['items']

        for item in data_subdomain:
            sub_list.append(item['child_identifier']['name'])
        
        page_record = []
        
        while data['next'] not in page_record:
            
            next_page = data['next']
            url =   f"https://api.flare.systems/firework/v3/identifiers/{_id}/children" \
                    f"?from={next_page}" 
            
            data = requests.get(url, headers={'Authorization': 'Bearer ' + self.token}, timeout=5)
            data = data.json()
            data_subdomain = data['items']

            page_record.append(next_page)

            for item in data_subdomain:
                sub_list.append(item['child_identifier']['name'])

        return sub_list

    def check_marketplace(self, _id):
        query = f"/firework/v2/assets/{_id}/feed?types[]=illicit_networks&order=desc&sort_by=created&time=&lite=true&" \
                f"merge_duplicates=true&fetch_type=results&risks[]=3&risks[]=4&risks[]=5&size=100&" \
                f"use_global_policies=true"
        data = self.get(query)
        keys = ['actor', 'first_crawled_at', 'source', 'source_name', 'timestamp', 'risk']
        filtered_d = []
        for item in data['items']:
            filtered_d.append(filter_dict_keys(item, keys))

        return {'items': filtered_d}
