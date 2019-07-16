import datetime
import json
import os

MONGO_URI = os.environ['MONGO_URI']
CORS_ORIGIN = os.environ['CORS_ORIGIN']

from mongoengine import *
connect('omni', host=MONGO_URI)

class CustomerForCard(DynamicDocument):
    pass

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': json.dumps(err) if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST",
            "Access-Control-Allow-Origin": CORS_ORIGIN
        },
    }

def lambda_handler(event, context):
    if event['httpMethod'] == "POST":
        try:
            payload = json.loads(event['body'])
            customer_for_card =  CustomerForCard.objects(
                client_id=payload['client_id'],
                entered_address=False
            )
            if customer_for_card:
                geocoding_gmaps = payload['geocoding_gmaps']
                if 'comment' in payload and payload['comment']:
                    geocoding_gmaps['comment'] = payload['comment']
                if 'internal_number' in payload and payload['internal_number']:
                    geocoding_gmaps['internal_number'] = payload['internal_number']
                customer_for_card.update(**dict(
                    geocoding_gmaps=geocoding_gmaps,
                    entered_address=True,
                    updated_at=datetime.datetime.utcnow()
                ))
                return respond(None, dict(message=True))
            else:
                return respond(dict(message="client_id does not exist"))
            
        except Exception as e:
            return respond(dict(message="Incorrect request body"))
    else:
        return respond(None, dict(message="method no allowed"))