import json
import logging
from decimal import Decimal

import src.lib.sqlfunctions as sql_functions

logging.getLogger().setLevel(logging.INFO)

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)

class ModelParameters:
    """A class for aggregating retrieving model parameters.
    An instance of this class is created by taking in the profile of a policyholder 
    such as industry, revenue, number of employees, etc.
    Parameters
    ----------
    name : str
        Name of the threat category
    uuid : str
        UUID of the policyholder.
    Examples
    --------
    """

    def __init__(self, name, uuid):
        self.name = name
        self.uuid = uuid
        self.ratios = self.retrieve_ratios()

        self.resiliency = self.retrieve_resiliency(uuid)
        self.company_details = self.retrieve_company_details(uuid)
        logging.debug(f"Company details:\n{self.company_details}")
        self.revenue = self.company_details[0][2]
        self.company_size = self.calculate_size(self.revenue)
        self.industry = self.company_details[0][4]
        self.employees = self.company_details[0][5]
        self.pii = self.company_details[0][3]
        self.pci = self.company_details[0][6] * 0.5  # 30% of pci records affected in breach
        self.loss_magnitude = self.calculate_lm(self.pii, self.industry, self.name, self.revenue, self.uuid)
        self.tef = self.retrieve_tef(self.company_size, self.name, self.industry, self.employees)
        self.lef = {k: Decimal(v) * (self.resiliency / 5) for k, v in self.tef.items()}

    def __call__(self):
        return {"lossMagnitude": self.loss_magnitude,
                "threatCategory": self.name,
                "lef": self.lef,
                "uuid": self.uuid
                }

    def retrieve_ratios(self):
        return {"data": [{"name": "Business Email Compromise",
                          "average": 123000,
                          "ratio": 1.338
                          },
                         {"name": "Ransomware",
                          "average": 123000,
                          "ratio": 3.271
                          },
                         {"name": "Data Espionage",
                          "average": 430000,
                          "ratio": 7.540
                          },
                         {"name": "Malware",
                          "average": 160000,
                          "ratio": 1.728
                          },
                         {"name": "Phishing",
                          "average": 72000,
                          "ratio": 0.713
                          },
                         {"name": "Insider",
                          "average": 91000,
                          "ratio": 1.334
                          },
                         {"name": "Supply Chain Attack",
                          "average": 33000,
                          "ratio": 0.229
                          },
                         {"name": "DDOS",
                          "average": 85000,
                          "ratio": 0.214
                          }
                         ]
                }

    def calculate_size(self, revenue):
        """Returns the size of the company based on revenue.
        Returns
        -------
        Company Size
            The company size of the policyholder.
        """
        if revenue <= 10000000:
            return "Small"
        elif revenue <= 100000000:
            return "Medium"
        elif revenue <= 1000000000:
            return "Large"
        else:
            return "Enterprise"

    def calculate_records_band(self, records):
        """Calculates the category based on the number of records held by company.
        Returns
        -------
        Records Band
            The records band based on number of records.
        """
        if records <= 50000:
            return 1
        elif records <= 100000:
            return 2
        elif records <= 500000:
            return 3
        elif records <= 1000000:
            return 4
        elif records <= 5000000:
            return 5
        else:
            return 6

    def calculate_lm(self, pii, industry, threat_category, revenue, uuid):
        """Calculates loss magnitude of the policyholder based on number of records, industry, threat category
        and revenue.
        There are 9 threat categories as follows:
        •	Business Email Compromise,
        •	Cyber Espionage,
        •	Data Breach, 
        •	Distributed Denial of Service, 
        •	Insider Threats, 
        •	Phishing, 
        •	Ransomware,
        •	Supply Chain Attacks, and
        •	Misconfiguration.
        Returns
        -------
        Loss Magnitude
            The records band based on number of records.
        """
        connection = sql_functions.make_connection()

        # DLP control family resiliency score to weight records
        control_family = ['Information Protection Processes and Procedures']
        control_family_results = sql_functions.control_family_score(connection, control_family, uuid)
        control_family_score = (control_family_results[0][1] + (control_family_results[0][2] * 2)) / 3 * \
                               control_family_results[0][3]
        logging.debug(f"Control family: {control_family_score}")

        # Recover nist function resiliency score
        nist_resiliency_query = """
        select round(avg(tri_score_stage)::numeric,2) as score, nist_function from score_result \
        where company_id = %s and existence = 'Exists' group by nist_function order by CASE nist_function WHEN 'Identify' THEN 1 WHEN 'Protect' THEN 2 WHEN 'Detect' THEN 3 WHEN 'Respond' THEN 4 ELSE 5 END
        """
        nist_resiliency_query_fields = (uuid,)
        nist_resiliency = sql_functions.retrieve_rows_safe(connection, nist_resiliency_query,
                                                           nist_resiliency_query_fields)
        downtime_weight = 0.5 / float(nist_resiliency[4][0])
        logging.debug(f"Recover resiliency: {nist_resiliency[4][0]} {downtime_weight}")

        records_band = self.calculate_records_band(round(pii * (control_family_score / 2.5)))
        logging.debug(f"PII: {pii}, Records band: {records_band}")

        if threat_category == 'Ransomware':
            cost_item = ('Incident Response', 'PR Support', 'Regulatory Fines (PII)')
            records_costs_query = """
            select cost_low, cost_mode, cost_high from asset_cost_record acr where cost_item in %s and records_category = %s 
            """
            records_costs_query_fields = (cost_item, records_band)
            records_costs = sql_functions.retrieve_rows_safe(connection, records_costs_query,
                                                             records_costs_query_fields)

            total_records_cost = [0, 0, 0]
            for cost_category in records_costs:
                total_records_cost[0] = total_records_cost[0] + cost_category[0]
                total_records_cost[1] = total_records_cost[1] + cost_category[1]
                total_records_cost[2] = total_records_cost[2] + cost_category[2]
            logging.debug(f"Records costs: {records_costs}")
            logging.debug(f"Total records costs: {total_records_cost}")

            downtime_query = """
            select ratio, downtime_low, downtime_mode, downtime_high from asset_downtime_industry adi \
            where threat_category = %s and industry = %s
            """
            downtime_query_fields = (threat_category, industry)
            downtime = sql_functions.retrieve_rows_safe(connection, downtime_query, downtime_query_fields)
            downtime_costs = [(downtime[0][0] * downtime[0][1] * downtime_weight * revenue / 365),
                              (downtime[0][0] * downtime[0][2] * downtime_weight * revenue / 365),
                              (downtime[0][0] * downtime[0][3] * downtime_weight * revenue / 365)]
            loss_magnitude = [(total_records_cost[0] + downtime_costs[0]), (total_records_cost[1] + downtime_costs[1]),
                              (total_records_cost[2] + downtime_costs[2])]
            logging.debug(f"Threat Category: {threat_category}, downtime: {downtime}")
        elif threat_category == 'Data Espionage':
            cost_item = ('Incident Response', 'PR Support', 'Regulatory Fines (PII)', 'Regulatory Fines (PCI)')
            records_costs_query = """
            select cost_low, cost_mode, cost_high from asset_cost_record acr where cost_item in %s and records_category = %s 
            """
            records_costs_query_fields = (cost_item, records_band)
            records_costs = sql_functions.retrieve_rows_safe(connection, records_costs_query,
                                                             records_costs_query_fields)
            logging.debug(f"Records costs: {records_costs}")

            # PCI cost multiply by number of records
            pci_records_cost = [records_costs[3][0] * self.pci, records_costs[3][1] * self.pci,
                                records_costs[3][2] * self.pci]
            logging.debug(f"PCI records costs: {pci_records_cost}")
            records_costs[3] = pci_records_cost

            # Sum the total cost of records
            total_records_cost = [0, 0, 0, 0]
            for cost_category in records_costs:
                total_records_cost[0] = total_records_cost[0] + cost_category[0]
                total_records_cost[1] = total_records_cost[1] + cost_category[1]
                total_records_cost[2] = total_records_cost[2] + cost_category[2]
            logging.debug(f"Records costs: {records_costs}")
            logging.debug(f"Total records cost: {total_records_cost}")

            downtime_query = """
            select ratio, downtime_low, downtime_mode, downtime_high from asset_downtime_industry adi \
            where threat_category = %s and industry = %s
            """
            downtime_query_fields = (threat_category, industry)
            downtime = sql_functions.retrieve_rows_safe(connection, downtime_query, downtime_query_fields)
            downtime_costs = [(downtime[0][0] * downtime[0][1] * downtime_weight * revenue / 365),
                              (downtime[0][0] * downtime[0][2] * downtime_weight * revenue / 365),
                              (downtime[0][0] * downtime[0][3] * downtime_weight * revenue / 365)]
            loss_magnitude = [(total_records_cost[0] + downtime_costs[0]), (total_records_cost[1] + downtime_costs[1]),
                              (total_records_cost[2] + downtime_costs[2])]
            logging.debug(f"Threat Category: {threat_category}, downtime: {downtime}")
        elif threat_category == 'Supply Chain Attack':
            cost_item = ('Incident Response', 'PR Support', 'Regulatory Fines (PII)')
            records_costs_query = """
            select cost_low, cost_mode, cost_high from asset_cost_record acr where cost_item in %s and records_category = %s 
            """
            records_costs_query_fields = (cost_item, records_band)
            records_costs = sql_functions.retrieve_rows_safe(connection, records_costs_query,
                                                             records_costs_query_fields)

            total_records_cost = [0, 0, 0]
            for cost_category in records_costs:
                total_records_cost[0] = total_records_cost[0] + cost_category[0]
                total_records_cost[1] = total_records_cost[1] + cost_category[1]
                total_records_cost[2] = total_records_cost[2] + cost_category[2]
            logging.debug(f"Records costs: {records_costs}")
            logging.debug(f"Total records cost: {total_records_cost}")

            downtime_query = """
            select ratio, downtime_low, downtime_mode, downtime_high from asset_downtime_industry adi \
            where threat_category = %s and industry = %s
            """
            downtime_query_fields = (threat_category, industry)
            downtime = sql_functions.retrieve_rows_safe(connection, downtime_query, downtime_query_fields)
            downtime_costs = [(downtime[0][0] * downtime[0][1] * downtime_weight * revenue / 365),
                              (downtime[0][0] * downtime[0][2] * downtime_weight * revenue / 365),
                              (downtime[0][0] * downtime[0][3] * downtime_weight * revenue / 365)]
            loss_magnitude = [(total_records_cost[0] + downtime_costs[0]), (total_records_cost[1] + downtime_costs[1]),
                              (total_records_cost[2] + downtime_costs[2])]
            logging.debug(f"Threat Category: {threat_category}, downtime: {downtime}")
        elif threat_category == 'DDOS':
            ddos_costs_query = """
            select cost from asset_ddos_cost adc where company_size = %s
            """
            ddos_costs_query_fields = (self.calculate_size(revenue),)
            ddos_costs = sql_functions.retrieve_rows_safe(connection, ddos_costs_query, ddos_costs_query_fields)
            loss_magnitude = [(0.7 * ddos_costs[0][0]), ddos_costs[0][0], (1.3 * ddos_costs[0][0])]
            logging.debug(f"DDOS: {ddos_costs}")
        elif threat_category == 'Phishing':
            cost_item = ('Incident Response', 'PR Support', 'Regulatory Fines (PII)')
            records_costs_query = """
            select cost_low, cost_mode, cost_high from asset_cost_record acr where cost_item in %s and records_category = %s 
            """
            records_costs_query_fields = (cost_item, records_band)
            records_costs = sql_functions.retrieve_rows_safe(connection, records_costs_query,
                                                             records_costs_query_fields)

            total_records_cost = [0, 0, 0]
            for cost_category in records_costs:
                total_records_cost[0] = total_records_cost[0] + cost_category[0]
                total_records_cost[1] = total_records_cost[1] + cost_category[1]
                total_records_cost[2] = total_records_cost[2] + cost_category[2]
            logging.debug(f"Records costs: {records_costs}")
            logging.debug(f"Total records cost: {total_records_cost}")

            loss_magnitude = [total_records_cost[0], total_records_cost[1], total_records_cost[2]]

        elif threat_category == 'Business Email Compromise':
            cost_item = ('Incident Response', 'Fraud')
            records_costs_query = """
            select cost from asset_cost_fraud acf where cost_item in %s and company_size = %s
            """
            records_costs_query_fields = (cost_item, self.calculate_size(revenue))
            records_costs = sql_functions.retrieve_rows_safe(connection, records_costs_query,
                                                             records_costs_query_fields)
            logging.debug(f"Records costs: {records_costs}")
            total_records_cost = [0, 0, 0]
            for cost_category in records_costs:
                total_records_cost[0] = total_records_cost[0] + cost_category[0]
                total_records_cost[1] = total_records_cost[1] + cost_category[0]
                total_records_cost[2] = total_records_cost[2] + cost_category[0]
            logging.debug(f"Records costs: {records_costs}")
            logging.debug(f"Total records cost: {total_records_cost}")

            loss_magnitude = [total_records_cost[0], total_records_cost[1], total_records_cost[2]]

        connection[1].close()
        connection[0].close()
        logging.debug(f"Threat category: {threat_category}")
        ratio = list(filter(lambda x: x["name"] == threat_category, self.ratios['data']))
        logging.debug(f"Ratio: {ratio[0]['ratio']}")
        total_lm = {"mean": loss_magnitude[1],
                    "sd": loss_magnitude[1] * ratio[0]['ratio'],
                    }
        return total_lm

    def retrieve_resiliency(self, uuid):
        connection = sql_functions.make_connection()
        resiliency_query = """
        select round(sum(tri_stage)::numeric,2) from (select avg(tri_score_stage) as tri_stage from score_result as a \
        where a.company_id = '{uuid}' and a.existence = 'Exists' group by nist_function) as a
        """.format(uuid=uuid)
        resiliency = sql_functions.retrieve_rows(connection, resiliency_query)[0][0]
        logging.debug(f"Resiliency: {resiliency}")
        connection[1].close()
        connection[0].close()
        return resiliency

    def retrieve_company_details(self, uuid):
        connection = sql_functions.make_connection()
        company_details_query = """
        select ic.id, ic.name, ic.revenue, ic.pii, ic.industry, ic.employees, ic.pci FROM company as ic \
        where ic.id ='{uuid}'
        """.format(uuid=uuid)

        company_details = sql_functions.retrieve_rows(connection, company_details_query)
        connection[1].close()
        connection[0].close()
        return company_details

    def retrieve_tef(self, company_size, threat_category, industry, employees):
        """Returns the threat event frequency based on the threat category.
        There are 9 threat categories as follows:
        •	Business Email Compromise,
        •	Cyber Espionage,
        •	Data Breach, 
        •	Distributed Denial of Service, 
        •	Insider Threats, 
        •	Phishing, 
        •	Ransomware,
        •	Supply Chain Attacks, and
        •	Misconfiguration.
        Returns
        -------
        Company Size
            The company size of the policyholder.
        """
        connection = sql_functions.make_connection()
        tef_query = """
        select tef_low, tef_mode, tef_high from tef_company_size tcs \
        where threat_category = %s and company_size = %s
        """
        logging.debug(f"Employees: {employees}")
        tef_query_fields = (threat_category, company_size)
        tef = sql_functions.retrieve_rows_safe(connection, tef_query, tef_query_fields)
        if threat_category == 'Ransomware':
            output = {"small": tef[0][0],
                      "mode": tef[0][1],
                      "high": tef[0][2]
                      }
        elif threat_category == 'Data Espionage':
            tef_ratio_query = """
            select ratio from tef_industry \
            where threat_category = %s and industry = %s
            """
            tef_ratio_fields = (threat_category, industry)
            tef_ratio = sql_functions.retrieve_rows_safe(connection, tef_ratio_query, tef_ratio_fields)
            output = {"small": float(tef[0][0]) * float(tef_ratio[0][0]),
                      "mode": float(tef[0][1]) * float(tef_ratio[0][0]),
                      "high": float(tef[0][2]) * float(tef_ratio[0][0])
                      }
        elif threat_category == 'Supply Chain Attack':
            output = {"small": tef[0][0],
                      "mode": tef[0][1],
                      "high": tef[0][2]
                      }
        elif threat_category == 'DDOS':
            output = {"small": tef[0][0],
                      "mode": tef[0][1],
                      "high": tef[0][2]
                      }
        elif threat_category == 'Phishing':
            # 3% of employees clickthrough based on Statista, 10% of emails result in major breach
            output = {"small": float(tef[0][0]) * float(employees) * 0.03 * 0.1,
                      "mode": float(tef[0][1]) * float(employees) * 0.03 * 0.1,
                      "high": float(tef[0][2]) * float(employees) * 0.03 * 0.1
                      }
        elif threat_category == 'Business Email Compromise':
            output = {"small": tef[0][0],
                      "mode": tef[0][1],
                      "high": tef[0][2]
                      }
        connection[1].close()
        connection[0].close()
        return output

def handler(event, context):
    uuid = event['uuid']
    logging.debug(f"Event:\n{event}")
    ransomware = ModelParameters("Ransomware", uuid)
    data_espionage = ModelParameters("Data Espionage", uuid)
    ddos = ModelParameters("DDOS", uuid)
    supply_chain = ModelParameters("Supply Chain Attack", uuid)
    bec = ModelParameters("Business Email Compromise", uuid)
    phishing = ModelParameters("Phishing", uuid)
    return [ransomware(), data_espionage(), ddos(), supply_chain(), bec(), phishing()]
