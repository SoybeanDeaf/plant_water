import pytest

from plant_water.services.mqtt import MQTTMessageService
from plant_water.config import Config
from mockito import mock, when, expect, verify, unstub


class TestMQTTMessageService:
    @classmethod
    def setup_method(self):
        self.client = mock()
        self.service = MQTTMessageService(self.client)

    @classmethod
    def teardown_method(self):
        unstub()

    def test_mqtt_loop_starts_when_starting_service(self):
        expect(self.client, times=1).loop_start()
        self.service.start()
        verify(self.client, times=1).loop_start()

    def test_mqtt_client_connects_when_starting_service(self):
        expect(self.client, times=1).connect(host=Config.MQTT.BROKER,
                                             port=Config.MQTT.PORT,
                                             keepalive=Config.MQTT.KEEP_ALIVE)
        self.service.start()
        verify(self.client, times=1).connect(host=Config.MQTT.BROKER,
                                             port=Config.MQTT.PORT,
                                             keepalive=Config.MQTT.KEEP_ALIVE)

    def test_service_keeps_track_of_whether_connected_after_starting(self):
        self.service.running = False
        self.service.start()
        assert self.service.running

    def test_service_does_not_connect_or_loop_if_already_running(self):
        expect(self.client, times=0).loop_start()
        expect(self.client, times=0).connect(host=Config.MQTT.BROKER,
                                             port=Config.MQTT.PORT,
                                             keepalive=Config.MQTT.KEEP_ALIVE)
        self.service.running = True
        self.service.start()
        verify(self.client, times=0).loop_start()
        verify(self.client, times=0).connect(host=Config.MQTT.BROKER,
                                             port=Config.MQTT.PORT,
                                             keepalive=Config.MQTT.KEEP_ALIVE)

    def test_client_disconnects_when_stopping_service(self):
        expect(self.client, times=1).disconnect()
        self.service.running = True
        self.service.stop()
        verify(self.client, times=1).disconnect()
    
    def test_loop_stops_when_stopping_service(self):
        expect(self.client, times=1).loop_stop()
        self.service.running = True
        self.service.stop()
        verify(self.client, times=1).loop_stop()

    def test_service_keeps_track_of_whether_connected_after_stopping(self):
        self.service.running = False
        self.service.stop()
        assert not self.service.running
        
    def test_service_does_not_disconnect_or_stop_loop_if_not_running(self):
        expect(self.client, times=0).loop_stop()
        expect(self.client, times=0).disconnect()
        self.service.running = False
        self.service.stop()
        verify(self.client, times=0).loop_start()
        verify(self.client, times=0).connect()

    def test_subscribes_to_topic_and_adds_callback(self):
        mock_callback = mock()
        expect(self.client, times=1).subscribe("my_topic")
        expect(self.client, times=1).message_callback_add("my_topic", mock_callback)
        self.service.subscribe("my_topic", mock_callback)
        verify(self.client, times=1).subscribe("my_topic")
        verify(self.client, times=1).message_callback_add("my_topic", mock_callback)
        assert self.service.subscriptions == { "my_topic": mock_callback }

    def test_unsubscribes_to_topic_and_removes_callback(self):
        expect(self.client, times=1).unsubscribe("my_topic")
        expect(self.client, times=1).message_callback_remove("my_topic")
        self.service.subscriptions = { "my_topic": mock() }
        self.service.unsubscribe("my_topic")
        verify(self.client, times=1).unsubscribe("my_topic")
        verify(self.client, times=1).message_callback_remove("my_topic")
        assert self.service.subscriptions == {}

    def test_publishes_message_with_correct_topic(self):
        expect(self.client, times=1).publish(topic="topic", payload="message")
        self.service.publish("topic", "message")
        verify(self.client, times=1).publish(topic="topic", payload="message")

    def test_callback_and_subscription_wont_be_added_if_already_exists(self):
        mock_callback = mock()
        expect(self.client, times=0).subscribe("my_topic")
        expect(self.client, times=0).message_callback_add("my_topic", mock_callback)
        self.service.subscriptions = { "my_topic": mock() }
        self.service.subscribe("my_topic", mock_callback)
        verify(self.client, times=0).subscribe("my_topic")
        verify(self.client, times=0).message_callback_add("my_topic", mock_callback)

    def test_callback_and_subscription_wont_be_removed_if_does_not_exist(self):
        expect(self.client, times=0).unsubscribe("my_topic")
        expect(self.client, times=0).message_callback_remove("my_topic")
        self.service.subscriptions = {}
        self.service.unsubscribe("my_topic")
        verify(self.client, times=0).unsubscribe("my_topic")
        verify(self.client, times=0).message_callback_remove("my_topic")