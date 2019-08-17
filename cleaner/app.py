import json
import botocore
import boto3
from logging import getLogger, INFO, DEBUG

# boto3.set_stream_logger()
# botocore.session.Session().set_debug_logger()

logger = getLogger(__name__)
logger.setLevel(INFO)

logs_client = boto3.client('logs')
lambda_client = boto3.client('lambda')

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

def get_lambda_function_names():
    """
    Lambda 関数の全ての情報を取得し、Lambda 関数名のリストを返す

    Returns
    -------
    lambda_function_names: list
        Lambda 関数名のリスト
    """

    lambda_function_names = list()

    try:
        responses = list()
        response = lambda_client.list_functions()
        responses.append(response)
        logger.debug(response)
        next_marker = response['nextMarker'] if 'nextMarker' in response else ''

        while next_marker:
            response = lambda_client.list_functions(Marker=next_marker) if next_marker else lambda_client.list_functions()
            logger.debug(response)

            responses.append(response)
            next_marker = response['nextMarker'] if 'nextMarker' in response else ''

        for response in responses:
            for lambda_function in response['Functions']:
                logger.debug(lambda_function)
                lambda_function_names.append(lambda_function['FunctionName'])

    except Exception as e:
        logger.error(e)

    return lambda_function_names

def lambda_handler(event, context):

    # recieved event
    logger.info(json.dumps(event, ensure_ascii=False, indent=2))

    # get log groups list
    log_groups = get_log_groups()
    logger.debug(json.dumps(log_groups, ensure_ascii=False, indent=2))

    lambda_function_names = get_lambda_function_names()
    logger.debug(json.dumps(lambda_function_names, ensure_ascii=False, indent=2))

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
            # "location": ip.text.replace("\n", "")
        }),
    }
