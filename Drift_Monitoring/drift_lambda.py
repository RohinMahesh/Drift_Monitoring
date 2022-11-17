import base64
import boto3
from datetime import datetime, timedelta
from evidently.pipeline.column_mapping import ColumnMapping
from evidently.model_profile import Profile
from evidently.model_profile.sections import DataDriftProfileSection
from evidently.options import DataDriftOptions
from helperFunctions import calculate_drift, create_drift_report, get_drift_data
from io import StringIO
import json
import numpy as np
import pandas as pd
import os


def lambda_handler(event, context):

    # Identify filtering conditions for S3 Select
    today = datetime.now()
    beginning = today - timedelta(days=14)
    mid = today - timedelta(days=7)

    # Extract comparison and reference data
    sql_query = """SELECT S.* FROM s3object S WHERE RecordDate >= {0}""".format(
        beginning
    )
    bucket_name = ""
    file_key = ""

    comparison_data, reference_data = get_drift_data(
        bucket_name, file_key, sql_query, beginning, mid
    )

    # Define required input for drift detection
    target = "target"
    numerical = list()
    categorical = list()
    d_time = "RecordDate"

    # Get drift report
    drift_report = create_drift_report(
        reference=reference_data,
        comparison=comparison_data,
        target=target,
        numerical_f=numerical,
        categorical_f=categorical,
        d_time=d_time,
    )

    # If there is any drift, send SNS notification
    if drift_report["any_drift"]:
        client = boto3.client("sns")
        response = client.publish(
            TargetArn="<ARN of the SNS topic>",
            Message=json.dumps({"default": drift_report}),
            MessageStructure="json",
        )

    return {"Status": "Drift report saved!"}
