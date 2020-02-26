from os import environ
from datetime import datetime
from typing import Union

from boto3 import resource
from boto3.dynamodb.conditions import Key

from pointing_poker.models import models


class SessionsDynamoDBRepo:
    def __init__(self):
        self.db = resource('dynamodb')
        self.table = self.db.Table(environ['SESSIONS_TABLE_NAME'] if 'SESSIONS_TABLE_NAME' in environ else 'sessions')

    def create(self, session: models.Session) -> None:
        self.table.put_item(
            Item={
                'id': session.id,
                'sessionID': session.id,
                'createdAt': str(session.createdAt),
                'name': session.name,
                'reviewingIssueTitle': session.reviewingIssue.title,
                'reviewingIssueDescription': session.reviewingIssue.description,
                'reviewingIssueURL': session.reviewingIssue.url,
                'isOpen': session.isOpen,
                'pointingMax': session.pointingMax,
                'pointingMin': session.pointingMin,
                'expiration': session.expiration,
                'type': 'session'
            }
        )

    def get(self, session_id: str) -> Union[models.Session, None]:
        records = self.table.query(
            KeyConditionExpression=Key('sessionID').eq(session_id)
        )

        items = records['Items']

        if not items:
            return None

        participants = [models.Participant(
            id=item['id'],
            name=item['name'],
            isModerator=item['isModerator'],
            currentVote=item['currentVote']
        ) for item in items if item['type'] == 'participant']

        session_item = [item for item in items if item['type'] == 'session'][0]

        return models.Session(
            id=session_item['sessionID'],
            name=session_item['name'],
            createdAt=datetime.fromisoformat(session_item['createdAt']),
            isOpen=session_item['isOpen'],
            pointingMax=session_item['pointingMax'],
            pointingMin=session_item['pointingMin'],
            expiration=session_item['expiration'],
            reviewingIssue=models.ReviewingIssue(
                title=session_item['reviewingIssueTitle'],
                description=session_item['reviewingIssueDescription'],
                url=session_item['reviewingIssueURL'],
            ),
            participants=participants
        )

    def get_participant(self, session_id: str, participant_id: str) -> Union[models.Participant, None]:
        record = self.table.get_item(
            Key={
                'sessionID': session_id,
                'id': participant_id,
            }
        )

        if 'Item' not in record:
            return None

        item = record['Item']

        return models.Participant(
            id=item['id'],
            name=item['name'],
            isModerator=item['isModerator'],
            currentVote=item['currentVote']
        )

    def add_participant(self, session_id: str, participant: models.Participant) -> None:
        self.table.put_item(
            Item={
                'sessionID': session_id,
                'id': participant.id,
                'name': participant.name,
                'isModerator': participant.isModerator,
                'currentVote': participant.currentVote,
                'type': 'participant'
            }
        )

    def remove_participant(self, session_id: str, participant_id: str) -> None:
        self.table.delete_item(
            Key={
                'sessionID': session_id,
                'id': participant_id
            }
        )