import json
import os

from mongoengine import connect, DynamicDocument

MONGO_URI = os.environ['MONGO_URI']

connect('db', host=MONGO_URI)

class BotmakerMessages(DynamicDocument):
    pass

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': json.dumps(err) if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json'
        },
    }

def lambda_handler(event, context):
    try:
        payload = json.loads(event['body'])
        botmaker =  BotmakerMessages(**payload)
        botmaker.save()
        return respond(None, dict(success=True))
    except Exception as e:
        return respond(dict(message="Incorrect request body"))