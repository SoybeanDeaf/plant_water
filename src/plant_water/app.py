import logging
import logging.config
import time

from plant_water.factory.mqtt import MQTTClientFactory
from plant_water.services.mqtt import MQTTMessageService

logging.config.fileConfig("resources/logging.conf")
logger = logging.getLogger("plant_watering")

def run():
    logger.info(" ################################################## ")
    logger.info(" #                                                # ")
    logger.info(" #            Starting the watering app           # ")
    logger.info(" #                                                # ")
    logger.info(" ################################################## ")

    mqtt_client = MQTTClientFactory.get_mqtt_client("plant_water")
    mqtt_service = MQTTMessageService(mqtt_client)
    mqtt_service.start()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    run()