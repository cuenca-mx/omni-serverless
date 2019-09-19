import json
import os

from mongoengine import connect, DynamicDocument
from pymongo.errors import ServerSelectionTimeoutError

MONGO_URI = os.environ['MONGO_URI']

connect('db', host=MONGO_URI, serverSelectionTimeoutMS=3000)


class BotmakerMessages(DynamicDocument):
    meta = {
        'indexes': [
            {'fields': ['$date']}
        ]
    }


class BotmakerStatus(DynamicDocument):
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
        if 'LAST_MESSAGE' in payload:
            message = payload['LAST_MESSAGE']
            search_date = message['date'].split(".")[0]
            
            botmaker_message =  BotmakerMessages.objects(
                message_id=message['_id_']
            )
            if not botmaker_message:
                botmaker_message =  BotmakerMessages.objects(
                    contactId=message['contactId'],
                    message=message['message']
                ).search_text(search_date).first()

            if botmaker_message:
                botmaker_message.update(
                    message_id=message['_id_'],
                    date=message['date'],
                    chatPlatform=message['chatPlatform'],
                    customerId=message['customerId'],
                    message_status=payload['STATUS'],
                )
            elif message["fromName"] == "Bot":
                botmaker =  BotmakerMessages(
                    **message,
                    message_id=message['_id_']
                )
                botmaker.save()

            botmaker_status =  BotmakerStatus(**payload)
            botmaker_status.save()
        else:     
            botmaker =  BotmakerMessages(**payload)
            botmaker.save()
        return respond(None, dict(success=True))
    except json.decoder.JSONDecodeError:
        return respond(dict(message="Incorrect request body"))
    except ServerSelectionTimeoutError:
        return respond(dict(message="No connection to mongo"))
