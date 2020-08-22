import json
import pytest

from plant_water.services.sensor_service import SensorService
from config import Config
from mockito import mock, when, expect, verify, unstub
from datetime import datetime
from collections import namedtuple

class TestSensorService:
    @classmethod
    def setup_method(self):
        self.mock_mqtt_service  = mock()
        self.mock_db_connection = mock()
        self.mock_db_cursor     = mock()
        self.service = SensorService(mqtt_message_service=self.mock_mqtt_service,
                                     db_connection=self.mock_db_connection)
        when(self.mock_db_connection).cursor().thenReturn(self.mock_db_cursor)

    @classmethod
    def teardown_method(self):
        unstub()

    def test_subscribes_to_sensor_topic(self):
        expect(self.mock_mqtt_service, times=1).subscribe(topic="sensor/moisture/#", handler=self.service._handle_moisture_reading)
        self.service.start()
        verify(self.mock_mqtt_service, times=1).subscribe(topic="sensor/moisture/#", handler=self.service._handle_moisture_reading)

    def test_callback_inserts_sensor_reading_to_db(self):
        payload = json.dumps({ "moisture_level": 13.0, "measured_at": "2020-08-20T13:33:22.539073" })
        msg = mock({ "payload": payload })
        expect(self.mock_db_cursor, times=1).execute("INSERT INTO moisture_reading VALUES (13.0, '2020-08-20T13:33:22.539073')")
        expect(self.mock_db_connection, times=1).commit()
        self.service._handle_moisture_reading(None, None, msg)
        verify(self.mock_db_cursor, times=1).execute("INSERT INTO moisture_reading VALUES (13.0, '2020-08-20T13:33:22.539073')")
        verify(self.mock_db_connection, times=1).commit()

    def test_on_moisture_reading_update_last_received_event_time(self):
        payload = json.dumps({ "moisture_level": 13.0, "measured_at": "2020-08-20T13:33:22.539073" })
        msg = mock({ "payload": payload })
        self.service.last_received_sensor_reading = datetime(1970, 1, 1)
        self.service._handle_moisture_reading(None, None, msg)
        assert self.service.last_received_sensor_reading == datetime(2020, 8, 20, 13, 33, 22, 539073)

    def test_sends_alert_when_reading_is_unreasonably_low(self):
        payload = json.dumps({ "moisture_level": 0.0, "measured_at": "2020-08-20T13:33:22.539073" })
        msg = mock({ "payload": payload })

        expect(self.mock_mqtt_service, times=1).publish("alert/email", "Unexpected moisture level 0% detected")
        self.service._handle_moisture_reading(None, None, msg)
        verify(self.mock_mqtt_service, times=1).publish("alert/email", "Unexpected moisture level 0% detected")

    def test_sends_alert_when_reading_is_unreasonably_high(self):
        payload = json.dumps({ "moisture_level": 100.0, "measured_at": "2020-08-20T13:33:22.539073" })
        msg = mock({ "payload": payload })

        expect(self.mock_mqtt_service, times=1).publish("alert/email", "Unexpected moisture level 100% detected")
        self.service._handle_moisture_reading(None, None, msg)
        verify(self.mock_mqtt_service, times=1).publish("alert/email", "Unexpected moisture level 100% detected")

    def test_logs_exception_when_unreadable_mqtt_message_payload(self):
        payload = "this is invalid json {}"
        msg = mock({ "payload": payload })
        expect(self.service.logger, times=1).exception("Error reading moisture reading")
        self.service._handle_moisture_reading(None, None, msg)
        verify(self.service.logger, times=1).exception("Error reading moisture reading")

    def test_when_moisture_reading_below_threshold_create_watering_event(self):
        payload = json.dumps({ "moisture_level": 1.0, "measured_at": "2020-08-20T13:33:22.539073" })
        msg = mock({ "payload": payload })
        expect(self.mock_mqtt_service, times=1).publish("event/water_plant", None)
        self.service._handle_moisture_reading(None, None, msg)
        verify(self.mock_mqtt_service, times=1).publish("event/water_plant", None)

    def test_when_moisture_reading_above_threshold_no_watering_event_created(self):
        payload = json.dumps({ "moisture_level": 50.0, "measured_at": "2020-08-20T13:33:22.539073" })
        msg = mock({ "payload": payload })
        expect(self.mock_mqtt_service, times=0).publish("event/water_plant")
        self.service._handle_moisture_reading(None, None, msg)
        verify(self.mock_mqtt_service, times=0).publish("event/water_plant")