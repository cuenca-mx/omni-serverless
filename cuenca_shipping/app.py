import json
import os

from mongoengine import *
connect('db', host=os.environ['MONGO_URI'])

class CuencaShipping(DynamicDocument):
    street = StringField(required=True)
    neighborhood = StringField(required=True)
    zipCode = StringField(required=True)
    latitude = StringField(required=True)
    longitude = StringField(required=True)
    externalNumber = StringField(required=True)
    internalNumber = StringField()
    comment = StringField(required=True)
    googleResult = DictField(required=True)


def validatePayload(payload: dict) -> dict:
    validfields = set(CuencaShipping._fields) & set(payload)
    payload = {k:payload[k] for k in validfields}
    return payload


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
            try:
                payload = validatePayload(json.loads(event['body']))
                address = CuencaShipping(**payload)
                address.save()
                return respond(None, {"success": True})
            except ValidationError as e:
                return respond(e.to_dict())
        except Exception as e:
            return respond({"message": "Incorrect request body"})
    else:
        return respond(None, {"success": True})