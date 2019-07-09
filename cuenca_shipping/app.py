import datetime
import json
import os

from mongoengine import *
connect('omni', host=os.environ['MONGO_URI'])

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
            "Access-Control-Allow-Origin": os.environ['CORS_ORIGIN']
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
                customer_for_card.update(**dict(
                    geocoding_gmaps=payload['geocoding_gmaps'],
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