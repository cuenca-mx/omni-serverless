import json
import os

from mongoengine import connect, DynamicDocument
from pymongo.errors import ServerSelectionTimeoutError

MONGO_URI = os.environ['MONGO_URI']

connect('db', host=MONGO_URI, serverSelectionTimeoutMS=3000)

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

def botmaker_message(event, context):
    try:
        payload = json.loads(event['body'])
        botmaker =  BotmakerMessages(**payload)
        botmaker.save()
        return respond(None, dict(success=True))
    except json.decoder.JSONDecodeError:
        return respond(dict(message="Incorrect request body"))
    except ServerSelectionTimeoutError:
        return respond(dict(message="No connection to mongo"))