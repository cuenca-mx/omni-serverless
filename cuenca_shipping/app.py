import datetime
import json
import os

from mongoengine import connect, DynamicDocument

MONGO_URI = os.environ['MONGO_URI']
CORS_ORIGIN = os.environ['CORS_ORIGIN']

connect('db', host=MONGO_URI, serverSelectionTimeoutMS=3000)

class ShipmentInvitations(DynamicDocument):
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

def cuenca_shipping(event, context):
    if event['httpMethod'] == "POST":
        try:
            payload = json.loads(event['body'])
            shipment_invitation =  ShipmentInvitations.objects(
                client_id=payload['client_id'],
                entered_address=False,
                shipment_canceled__exists=False
            )
            if shipment_invitation:
                geocoding_gmaps = payload['geocoding_gmaps']
                if 'comment' in payload and payload['comment']:
                    geocoding_gmaps['comment'] = payload['comment']
                if 'internal_number' in payload and payload['internal_number']:
                    geocoding_gmaps['internal_number'] = payload['internal_number']
                shipment_invitation.update(**dict(
                    geocoding_gmaps=geocoding_gmaps,
                    entered_address=True,
                    updated_at=datetime.datetime.utcnow()
                ))
                return respond(None, dict(message=True))
            else:
                return respond(dict(message="client_id does not exist"))
        except json.decoder.JSONDecodeError:
            return respond(dict(message="Incorrect request body"))
        except ServerSelectionTimeoutError:
            return respond(dict(message="No connection to mongo"))
    else:
        return respond(None, dict(message="method no allowed"))