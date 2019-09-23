import json
import botocore
import boto3
from logging import getLogger, INFO, DEBUG

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()
# logging.getLogger('aws_xray_sdk').setLevel(logging.DEBUG)

# boto3.set_stream_logger()
# botocore.session.Session().set_debug_logger()

logger = getLogger(__name__)
logger.setLevel(INFO)

logs_client = boto3.client('logs')
lambda_client = boto3.client('lambda')
apigateway_client = boto3.client('apigateway')

LAMBDA_FUNCTION_LOG_GROUP_NAME_PREFIX = '/aws/lambda/'
API_GATEWAY_EXECUTION_LOG_NAME_PREFIX = 'API-Gateway-Execution-Logs_'

def get_log_group_names():
    """
    CloudWatch Logs の全てのロググループ情報を取得し、ロググループ名のリストを返す

    Returns
    -------
    log_group_names: list
        ロググループ名のリスト
    """

    log_group_names = list()

    try:
        paginator = logs_client.get_paginator('describe_log_groups')
        for page in paginator.paginate():
            for log_group in page['logGroups']:
                log_group_names.append(log_group['logGroupName'])

    except Exception as e:
        logger.error(e)

    return log_group_names

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
        paginator = lambda_client.get_paginator('list_functions')
        for page in paginator.paginate():
            for function in page['Functions']:
                lambda_function_names.append(function['FunctionName'])

    except Exception as e:
        logger.error(e)

    return lambda_function_names

def extract_lambda_log_group_names(log_group_names):
    """
    ロググループ名のリストを受け取り、そこから Lambda 関数ロググループ名を抽出したリストを返す

    Parameters
    ----------
    log_group_names: list, required
        ロググループ名のリスト

    Returns
    -------
    lambda_function_names: list
        Lambda 関数ロググループ名のリスト
    """
    lambda_log_group_names = list()

    for log_group_name in log_group_names:
        if LAMBDA_FUNCTION_LOG_GROUP_NAME_PREFIX in log_group_name:
            lambda_log_group_names.append(log_group_name)

    return lambda_log_group_names

def delete_not_exist_lambda_log_groups(lambda_log_group_names, lambda_function_names):
    """
    Lambda 関数の全ての情報を取得し、Lambda 関数名のリストを返す

    Parameters
    ----------
    lambda_log_group_names: list, required
        Lambda 関数ロググループ名のリスト

    lambda_function_names: list, required
        Lambda 関数名のリスト
    """

    lambda_function_names_concatenate_log_group_prefix = list()

    for lambda_function_name in lambda_function_names:
        lambda_function_names_concatenate_log_group_prefix.append(
            LAMBDA_FUNCTION_LOG_GROUP_NAME_PREFIX + lambda_function_name
        )

    not_exist_lambda_log_groups = list(set(lambda_log_group_names) - set(lambda_function_names_concatenate_log_group_prefix))
    logger.info('delete lambda log group list')
    logger.info(json.dumps(not_exist_lambda_log_groups, ensure_ascii=False, indent=2))

    for not_exist_lambda_log_group in not_exist_lambda_log_groups:
        logs_client.delete_log_group(logGroupName=not_exist_lambda_log_group)

def get_apigateway_restapi_ids():
    """
    API Gateway Rest API の全ての情報を取得し、Rest Api ID のリストを返す

    Returns
    -------
    apigateway_restapi_ids: list
        Rest Api ID のリスト
    """

    apigateway_restapi_ids = list()

    try:
        paginator = apigateway_client.get_paginator('get_rest_apis')
        for page in paginator.paginate():
            for rest_api in page['items']:
                apigateway_restapi_ids.append(rest_api['id'])

    except Exception as e:
        logger.error(e)

    return apigateway_restapi_ids

def extract_apigateway_execution_log_group_names(log_group_names):
    """
    ロググループ名のリストを受け取り、そこから API Gateway 実行ロググループ名を抽出したリストを返す

    Parameters
    ----------
    log_group_names: list, required
        ロググループ名のリスト

    Returns
    -------
    apigateway_execution_log_group_names: list
        API Gateway 実行ロググループ名のリスト
    """
    apigateway_execution_log_group_names = list()

    for log_group_name in log_group_names:
        if API_GATEWAY_EXECUTION_LOG_NAME_PREFIX in log_group_name:
            apigateway_execution_log_group_names.append(log_group_name)

    return apigateway_execution_log_group_names


def delete_not_exist_apigateway_execution_log_groups(apigateway_execution_log_group_names, apigateway_restapi_ids):
    """
    API Gateway Rest Api リソースが存在しない実行ロググループを削除する

    Parameters
    ----------
    apigateway_execution_log_group_names: list, required
        API Gateway 実行ロググループ名のリスト

    apigateway_restapi_ids: list, required
        API Gateway Rest Api ID のリスト
    """

    not_exist_apigateway_execution_log_groups = list()

    for apigateway_execution_log_group_name in apigateway_execution_log_group_names:
        for apigateway_restapi_id in apigateway_restapi_ids:
            if apigateway_restapi_id in apigateway_execution_log_group_name:
                break
        else:
            not_exist_apigateway_execution_log_groups.append(apigateway_execution_log_group_name)

    logger.info('delete api gateway execution log group list')
    logger.info(json.dumps(not_exist_apigateway_execution_log_groups, ensure_ascii=False, indent=2))

    for not_exist_apigateway_execution_log_group in not_exist_apigateway_execution_log_groups:
        logs_client.delete_log_group(logGroupName=not_exist_apigateway_execution_log_group)


def lambda_handler(event, context):

    # recieved event
    logger.info(json.dumps(event, ensure_ascii=False, indent=2))

    # get all log groups list
    log_group_names = get_log_group_names()
    logger.debug(json.dumps(log_group_names, ensure_ascii=False, indent=2))

    # get lambda function names
    lambda_function_names = get_lambda_function_names()
    logger.debug(json.dumps(lambda_function_names, ensure_ascii=False, indent=2))

    # delete not exit lambda log groups
    lambda_log_group_names = extract_lambda_log_group_names(log_group_names)
    delete_not_exist_lambda_log_groups(lambda_log_group_names, lambda_function_names)

    # get API Gateway Rest Api IDs
    apigateway_restapi_ids = get_apigateway_restapi_ids()
    logger.debug(json.dumps(apigateway_restapi_ids, ensure_ascii=False, indent=2))

    # delete not exist API Gateway Rest Api execution log groups
    apigateway_execution_log_group_names = extract_apigateway_execution_log_group_names(log_group_names)
    delete_not_exist_apigateway_execution_log_groups(apigateway_execution_log_group_names, apigateway_restapi_ids)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
            # "location": ip.text.replace("\n", "")
        }),
    }
