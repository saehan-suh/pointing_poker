from pointing_poker.aws.repositories import sessions as session_repo
from pointing_poker.aws.services import sessions as session_service
from pointing_poker.models import models


def create_session(event, _):
    payload = event['sessionDescription']

    reviewing_issue = payload['reviewingIssue']

    session_description = models.SessionDescription(
        name=payload['name'],
        pointingMax=payload['pointingMax'],
        pointingMin=payload['pointingMin'],
        reviewingIssue=models.ReviewingIssue(
            title=reviewing_issue['title'],
            description=reviewing_issue['description'],
            url=reviewing_issue['url']
        )
    )

    resp = session_service.SessionService(session_repo.SessionsDynamoDBRepo()).create_session(
        session_description).to_json()

    resp['createdAt'] = str(resp['createdAt'])

    return resp


def session(event, _):
    session_id = event['sessionID']

    resp = session_service.SessionService(session_repo.SessionsDynamoDBRepo()).session(session_id).to_json()

    resp['createdAt'] = str(resp['createdAt'])

    return resp


def join_session(event, _):
    session_id = event['sessionID']
    payload = event['participant']

    participant_description = models.ParticipantDescription(
        name=payload['name']
    )

    return session_service.SessionService(session_repo.SessionsDynamoDBRepo()).join_session(
        session_id, participant_description).to_json()
