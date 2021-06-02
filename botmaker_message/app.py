import json
import os
import requests

from mongoengine import connect, DynamicDocument
from pymongo.errors import ServerSelectionTimeoutError

MONGO_URI = os.environ['MONGO_URI']
SANDBOX_URL = os.environ.get('SANDBOX_URL', None)
SANDBOX_MODE = True if os.environ.get('SANDBOX_MODE', 'false') == 'true' else False

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
        if SANDBOX_MODE and SANDBOX_URL:
            try:
                auth_bm_token = event['headers'].get('auth-bm-token', '')
                requests.post(
                    SANDBOX_URL,
                    json=payload,
                    headers={"auth-bm-token": auth_bm_token}
                )
            except Exception as e:
                pass
        return respond(None, dict(success=True))
    except json.decoder.JSONDecodeError:
        return respond(dict(message="Incorrect request body"))
    except ServerSelectionTimeoutError:
        return respond(dict(message="No connection to mongo"))
