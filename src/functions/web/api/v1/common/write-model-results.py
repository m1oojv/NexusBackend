import json
import logging
from decimal import Decimal

import src.lib.sqlfunctions as sql_functions

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)

logging.getLogger().setLevel(logging.INFO)

def handler(event, context):
    connection = sql_functions.make_connection()
    update_results_query = """update financial set risk = '{AAL}', \
    loss_exceedence = '{loss_exceedence}', threat_category_losses = '{threat_category}', \
    loss_by_return_period = '{return_period}' WHERE company_id = '{uuid}'
    """.format(AAL=event['AAL'], loss_exceedence=json.dumps(event['lossExceedence']),
        threat_category=json.dumps(event['threatCategory']), return_period=json.dumps(event['returnPeriod']),
        uuid=event['uuid'])

    update_assessment_progress_query = """
    update company set assessment_progress = 'COMPLETED',
    control_status = 'COMPLETED' where id = %s 
    """

    try:
        sql_functions.update_rows(connection, update_results_query)
        sql_functions.update_rows_safe(connection, update_assessment_progress_query, (event['uuid'],))
    except Exception as e:
        logging.exception(e)
        connection[1].close()
        connection[0].close()
        return False

    connection[1].close()
    connection[0].close()

    logging.debug(f"Threat category: {event['threatCategory']}\n"
                  f"Loss exceedence: {event['lossExceedence']}\n"
                  f"AAL: {event['AAL']}")
    return
