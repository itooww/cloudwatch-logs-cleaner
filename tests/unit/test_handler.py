import json

import pytest

from cleaner import app


@pytest.fixture()
def cw_scheduled_event():
    """ Generates CloudWatch Scheduled Event"""

    return {
        "id": "cdc73f9d-aea9-11e3-9d5a-835b769c0d9c",
        "detail-type": "Scheduled Event",
        "source": "aws.events",
        "account": "",
        "time": "1970-01-01T00:00:00Z",
        "region": "us-east-1",
        "resources": [
            "arn:aws:events:us-east-1:123456789012:rule/ExampleRule"
        ],
        "detail": {}
    }


def test_lambda_handler(cw_scheduled_event):

    ret = app.lambda_handler(cw_scheduled_event, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "message" in ret["body"]
    assert data["message"] == "hello world"
    # assert "location" in data.dict_keys()
