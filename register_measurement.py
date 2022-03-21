"""
Persists measurements to a DB
"""
import asyncio
import json

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_1

import config
from models import Measurement


def put_measurement(measurement: Measurement) -> None:
    """Stores temperature measurements in a DynamoDB table and updates the latest measurement if needed."""
    dynamodb = boto3.resource("dynamodb")

    # DynamoDB does not support datetime types, so we store them as strings
    iso_timestamp = measurement.timestamp.isoformat()

    item = {
        "pk": iso_timestamp,
        "value": measurement.value,
        "timestamp": iso_timestamp
    }

    table = dynamodb.Table(config.TABLE_NAME)

    # Record measurement in DB
    table.put_item(Item=item)

    # Update latest measurement if needed
    item['pk'] = 'latest'

    try:
        table.put_item(
            Item=item,
            ConditionExpression=Attr('timestamp').lt(iso_timestamp)
        )

    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            # If the conditional check fails, it is possible that there is no "latest" record yet
            # In that case, we check if it exists
            table.put_item(
                Item=item,
                ConditionExpression=Attr('pk').not_exists()
            )

        else:
            raise e


async def main():
    """Listens for new measurements events and persists them to a database."""
    client = MQTTClient()

    await client.connect(config.BROKER_URL)

    await client.subscribe([
        (config.MEASUREMENTS_TOPIC, QOS_1),
    ])

    while True:
        message = await client.deliver_message()

        packet = message.publish_packet

        json_data = json.loads(packet.payload.data.decode())

        measurement = Measurement(**json_data)

        put_measurement(measurement)


if __name__ == "__main__":
    asyncio.run(main())
