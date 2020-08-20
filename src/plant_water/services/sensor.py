from paho.mqtt.client import Client, MQTTMessage # type: ignore
from typing import Any, List

from plant_water.models.sensor import Sensor
from plant_water.services.mqtt import MQTTMessageService

class SensorService:
    def __init__(self, mqtt_message_service: MQTTMessageService):
        self.sensors: List[Sensor] = []
        self.mqtt_message_service = mqtt_message_service
        self.mqtt_message_service.subscribe("sensors/moisture/#", self._handle_moisture_reading)

    def _handle_moisture_reading(self, client: Client, userdata: Any, message: MQTTMessage):
        sensor = self.sensors[message.topic]
        print(sensor)

    def _get_sensor_id_from_topic(self, topic: str) -> int:
        pass

        
