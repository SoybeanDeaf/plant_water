import logging
import logging.config
import time
import os
import sqlite3

from plant_water.factory.mqtt import MQTTClientFactory
from plant_water.services.mqtt_service import MQTTMessageService
from plant_water.services.sensor_service import SensorService
from config import Config

logging.config.fileConfig("./src/resources/logging.conf")
logger = logging.getLogger("plant_watering")

def run():
    logger.info("Starting app...")
    mqtt_client = MQTTClientFactory.get_mqtt_client("plant_water")
    mqtt_service = MQTTMessageService(mqtt_client)
    sensor_service = SensorService(mqtt_service, sqlite3.connect(Config.Database.DATABASE_NAME))

    sensor_service.start()
    mqtt_service.start()

    while True:
        time.sleep(0.1)
        pass

if __name__ == "__main__":
    run()