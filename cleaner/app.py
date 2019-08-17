import json
import botocore
import boto3
from logging import getLogger, INFO, DEBUG

# boto3.set_stream_logger()
# botocore.session.Session().set_debug_logger()

logger = getLogger(__name__)
logger.setLevel(INFO)

logs_client = boto3.client('logs')

def get_log_groups():
    """
    CloudWatch Logs の全てのロググループ情報を取得し、ロググループ名のリストを返す

    Returns
    -------
    log_groups: list
        ロググループ名のリスト
    """

    log_groups = list()

    try:
        responses = list()
        response = logs_client.describe_log_groups()
        logger.debug(response)
        next_token = response['nextToken'] if 'nextToken' in response else ''

        while next_token:
            response = logs_client.describe_log_groups(nextToken=next_token) if next_token else logs_client.describe_log_groups()
            logger.debug(response)

            responses.append(response)
            next_token = response['nextToken'] if 'nextToken' in response else ''

        for response in responses:
            for log_group in response['logGroups']:
                logger.debug(log_group)
                log_groups.append(log_group['logGroupName'])

    except Exception as e:
        logger.error(e)

    return log_groups



def lambda_handler(event, context):

    # recieved event
    logger.info(json.dumps(event, ensure_ascii=False, indent=2))

    # get log groups list
    log_groups = get_log_groups()
    logger.debug(json.dumps(log_groups, ensure_ascii=False, indent=2))

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
            # "location": ip.text.replace("\n", "")
        }),
    }