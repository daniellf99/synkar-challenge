"""
Emulates an IoT agent
"""

import asyncio
import json
import random
from datetime import datetime

from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_0, QOS_1

import config
from models import Measurement, Coefficients

coefficients = Coefficients(a=1, b=1)


def get_measurement() -> Measurement:
    """Returns a random measurement."""
    return Measurement(
        value=random.randint(1,20),
        timestamp=datetime.now()
    )


def correct(measurement: Measurement, coeff: Coefficients) -> Measurement:
    """Returns a new measurement with value corrected by a linear calibration curve."""
    value = (coeff.a * measurement.value) + coeff.b

    return Measurement(
        value=value,
        timestamp=measurement.timestamp
    )


async def calibrate():
    """Subscribes to calibration events and persists changes locally. Runs forever."""
    client = MQTTClient()

    await client.connect(config.BROKER_URL)

    await client.subscribe([
            (config.CALIBRATION_TOPIC, QOS_1),
         ])

    while True:
        message = await client.deliver_message()

        packet = message.publish_packet

        json_data = json.loads(packet.payload.data.decode())

        new_coeff = Coefficients(**json_data)

        global coefficients

        coefficients = new_coeff


async def publish_measurements():
    """Publishes the latest temperature measurement every 10 seconds. Runs forever."""
    client = MQTTClient()

    await client.connect(config.BROKER_URL)

    while True:
        measurement = correct(get_measurement(), coefficients)

        payload = measurement.json().encode()

        await client.publish(config.MEASUREMENTS_TOPIC, payload, qos=QOS_1)

        await asyncio.sleep(10)


async def main():
    calibration_task = asyncio.create_task(calibrate())
    measurements_task = asyncio.create_task(publish_measurements())

    await calibration_task
    await measurements_task


if __name__ == '__main__':
    asyncio.run(main())
