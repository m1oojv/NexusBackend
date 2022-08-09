import json
import src.lib.sqlfunctions as sqlfunctions
import decimal
import collections

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal): return float(obj)

def investments(event, context):
    connection = sqlfunctions.make_connection()

    ## write string queries ##
    investments_query = """
    SELECT * FROM public.investments
    """.format(id=id)

    ## this retrives rows from DB as a list
    investments_data = sqlfunctions.retrieve_rows(connection, investments_query)

    # parse data into dict
    investments_key = ('name', 'value', 'startDate', 'endDate')
    investments_result = []
    for row in investments_data:
        investments_result.append(dict(zip(investments_key, row)))

    response = json.dumps(investments_result, cls = Encoder)
    print (response)
    connection[1].close()
    connection[0].close()
    return {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': response,
    }