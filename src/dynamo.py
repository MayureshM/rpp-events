import boto3
import humps
from util import TRACER
from boto3.dynamodb.conditions import Key
from environs import Env
from voluptuous import Any
from aws_lambda_powertools import Logger


LOGGER = Logger()
ENV = Env()

TABLE_NAME = ENV("INVENTORY_TABLE", validate=Any(str))
DYNAMO = boto3.resource("dynamodb")
TABLE = DYNAMO.Table(name=TABLE_NAME)

RPP_EVENTS_TABLE_NAME = ENV("RPP_EVENTS_TABLE_NAME", validate=Any(str))
DYNAMO = boto3.resource("dynamodb")
RPP_EVENTS_TABLE = DYNAMO.Table(name=RPP_EVENTS_TABLE_NAME)


@TRACER.capture_method
def get_active_and_completed_tasks(pk):
    """get all active and completed tasks.

    :param pk:
    """
    completed_tasks = []
    active_tasks = []
    if pk:
        key_condition_exp = Key("pk").eq(pk)
        qr = TABLE.query(
            KeyConditionExpression=key_condition_exp,
            ProjectionExpression="pk,sk,completed_on,created_on,task_name,updated",
        )

        completed_tasks = [
            _format_task(i) for i in qr["Items"] if i["sk"].startswith("completed_task")
        ]
        active_tasks = [
            _format_task(i) for i in qr["Items"] if i["sk"].startswith("active_task")
        ]

    return active_tasks, completed_tasks


@TRACER.capture_method
def _format_task(task):

    f_task = humps.camelize(task)
    f_task.pop("sk")
    f_task.pop("pk")
    f_task["type"] = f_task.pop("taskName")

    return f_task


@TRACER.capture_method
def get_parts_count(pk, sk):
    """get number of parts linked to a labor.

    :param pk:
    :param sk:
    """

    key_condition_exp = Key("pk").eq(pk) & Key("sk").begins_with(
        "part#" + sk.replace(":", "#")
    )
    parts_count = TABLE.query(KeyConditionExpression=key_condition_exp, Select="COUNT")[
        "Count"
    ]

    return parts_count


def get_event_data(event_type: str) -> dict:
    """
    Fetch data from DynamoDB table for a specific event type
    Args:
        event_type (str): The event type to fetch data for
    Returns:
        dict: The event data if found, empty dict if not found
    Raises:
        Exception: If there's an error accessing DynamoDB
    """
    try:
        response = RPP_EVENTS_TABLE.get_item(Key={"event_type": event_type})
        LOGGER.info(
            {
                "message": "Successfully fetched data from DynamoDB",
                "event_type": event_type,
                "fetched_item": response.get("Item", {}),
            }
        )
        return response.get("Item", {})
    except Exception as e:
        LOGGER.error(
            {
                "message": "Error fetching data from DynamoDB",
                "event_type": event_type,
                "error": str(e),
            }
        )
        raise


def upsert_event_data(event_type: str, data: dict) -> bool:
    """
    Upsert (update if exists, insert if not) data in DynamoDB table for a specific event type
    Args:
        event_type (str): The event type to update/insert data for
        data (dict): The data to store
    Returns:
        bool: True if successful, False otherwise
    Raises:
        Exception: If there's an error accessing DynamoDB
    """
    try:
        # Create the update expression and attribute values
        update_expr = "SET "
        expr_attr_values = {}
        expr_attr_names = {}

        for key, value in data.items():
            update_expr += f"#{key} = :{key}, "
            expr_attr_values[f":{key}"] = value
            expr_attr_names[f"#{key}"] = key

        # Remove trailing comma and space
        update_expr = update_expr.rstrip(", ")

        response = RPP_EVENTS_TABLE.update_item(
            Key={"event_type": event_type},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_attr_values,
            ExpressionAttributeNames=expr_attr_names,
            ReturnValues="ALL_NEW",
        )

        LOGGER.info(
            {
                "message": "Successfully upserted data in DynamoDB",
                "event_type": event_type,
                "updated_item": response.get("Attributes", {}),
            }
        )
        return True

    except Exception as e:
        LOGGER.warning(
            {
                "message": "Error upserting data in DynamoDB",
                "event_type": event_type,
                "data": data,
                "error": str(e),
            }
        )


def upsert_subscription_details(
    event_type: str, subscription_key: str, subscription_data: dict
) -> bool:
    """
    Upsert subscription details for a specific event type, supporting multiple subscriptions
    Args:
        event_type (str): The event type
        subscription_key (str): Unique key for this subscription
        subscription_data (dict): The subscription data including expand and subscription_id
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # First try to get existing item
        existing_response = RPP_EVENTS_TABLE.get_item(Key={"event_type": event_type})

        existing_item = existing_response.get("Item", {})

        # Initialize structure if it doesn't exist
        if not existing_item:
            existing_item = {"event_type": event_type, "details": {}, "expansions": []}

        # Ensure details exists
        if "details" not in existing_item:
            existing_item["details"] = {}

        # Update expansions for this specific subscription
        existing_item["details"][subscription_key] = subscription_data

        # Recalculate global expansions by collecting from all subscription details
        all_expansions = set()
        for sub_data in existing_item["details"].values():
            all_expansions.update(sub_data.get("expand", []))

        existing_item["expansions"] = list(all_expansions)

        # Handle global target information (SQS and Lambda ARNs)
        if "sqs" in subscription_data:
            if "sqs" not in existing_item:
                existing_item["sqs"] = subscription_data["sqs"]
            subscription_data.pop("sqs")
        if "lambda" in subscription_data:
            if "lambda" not in existing_item:
                existing_item["lambda"] = subscription_data["lambda"]
            subscription_data.pop("lambda")
        existing_item["subscription_id"] = subscription_data.get("subscription_id")
        subscription_data.pop("subscription_id", None)
        # Add/update this subscription's details
        existing_item["details"][subscription_key] = subscription_data

        # Put the updated item back
        RPP_EVENTS_TABLE.put_item(Item=existing_item)

        LOGGER.info(
            {
                "message": "Successfully upserted subscription details in DynamoDB",
                "event_type": event_type,
                "subscription_key": subscription_key,
                "updated_item": existing_item,
            }
        )
        return True

    except Exception as e:
        LOGGER.error(
            {
                "message": "Error upserting subscription details in DynamoDB",
                "event_type": event_type,
                "subscription_key": subscription_key,
                "subscription_data": subscription_data,
                "error": str(e),
            }
        )
        return False


def delete_event_data(event_type: str) -> bool:
    """
    Delete data from DynamoDB table for a specific event type
    Args:
        event_type (str): The event type to delete data for
    Returns:
        bool: True if successful, False otherwise
    Raises:
        Exception: If there's an error accessing DynamoDB
    """
    try:
        response = RPP_EVENTS_TABLE.delete_item(
            Key={"event_type": event_type}, ReturnValues="ALL_OLD"
        )

        LOGGER.info(
            {
                "message": "Successfully deleted data from DynamoDB",
                "event_type": event_type,
                "deleted_item": response.get("Attributes", {}),
            }
        )
        return True

    except Exception as e:
        LOGGER.error(
            {
                "message": "Error deleting data from DynamoDB",
                "event_type": event_type,
                "error": str(e),
            }
        )
        return False
