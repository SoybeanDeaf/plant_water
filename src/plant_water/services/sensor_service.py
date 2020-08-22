import json
import sqlite3
import logging

from paho.mqtt.client import Client, MQTTMessage # type: ignore
from typing import Optional, Any, List
from plant_water.services.mqtt_service import MQTTMessageService
from datetime import datetime
from config import Config

class SensorService:
    def __init__(self, mqtt_message_service: MQTTMessageService):
        self.logger = logging.getLogger(__name__)
        self.mqtt_message_service = mqtt_message_service

        self.last_received_sensor_reading: Optional[datetime] = None 
        self.plant_watering_threshold: Optional[float] = 5.0

    def start(self) -> None:
        self.mqtt_message_service.subscribe(topic="sensor/moisture/#",
                                            handler=self._handle_moisture_reading)


    def _handle_moisture_reading(self, client: Client, userinfo: str, msg: MQTTMessage) -> None:
        try:
            payload = json.loads(msg.payload)
            moisture_level = payload.get("moisture_level")

            self.update_last_sensor_received_time(payload)
            self.save_reading_to_db(payload)
            if moisture_level == 0.0 or moisture_level == 100.0:
                self.send_email_alert(f"Unexpected moisture level {int(moisture_level)}% detected")
            elif self.plant_watering_threshold and moisture_level <= self.plant_watering_threshold:
                self.water_plant()
        except ValueError:
            self.logger.exception("Error reading moisture reading")

    def _get_db_connection(self):
        return sqlite3.connect(Config.Database.DATABASE_NAME)

    def update_last_sensor_received_time(self, msg_payload) -> None:
        self.last_received_sensor_reading = datetime.fromisoformat(msg_payload.get("measured_at"))

    def save_reading_to_db(self, msg_payload) -> None:
        connection = self._get_db_connection()
        connection.cursor().execute(f"INSERT INTO moisture_reading VALUES ({msg_payload.get('moisture_level')}, '{msg_payload.get('measured_at')}')")
        connection.commit()

    def send_email_alert(self, alert_content) -> None:
        self.mqtt_message_service.publish("alert/email", alert_content)

    def water_plant(self) -> None:
        self.mqtt_message_service.publish("event/water_plant", None)