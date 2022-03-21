"""
RESTful HTTP API
"""

import boto3
import uvicorn
from fastapi import FastAPI
from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_1

import config
from models import Measurement, Coefficients

app = FastAPI()


@app.post("/set-coeff")
async def set_coeff(coefficient: Coefficients):
    client = MQTTClient()

    await client.connect(config.BROKER_URL)

    payload = coefficient.json().encode()

    await client.publish(config.CALIBRATION_TOPIC, payload, qos=QOS_1)


@app.get("/measurement", response_model=Measurement)
async def get_temperature():
    """Returns the latest temperature measurement"""
    dynamodb = boto3.resource("dynamodb")

    table = dynamodb.Table(config.TABLE_NAME)

    response = table.get_item(Key={'pk': 'latest'})

    measurement = Measurement(**response['Item'])

    return measurement


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8080)
