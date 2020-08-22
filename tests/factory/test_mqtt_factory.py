import pytest

from plant_water.factory.mqtt import MQTTClientFactory
from plant_water.factory import mqtt
from mockito import mock, when, expect, verify, unstub

class TestMqttFactory:

    @classmethod
    def teardown_method(self):
        unstub()

    def test_should_get_mqtt_client_with_given_id(self):
        mock_client = mock()
        expect(mqtt, times=1).Client("client_id").thenReturn(mock_client)
        client = MQTTClientFactory.get_mqtt_client("client_id")
        assert client == mock_client
        verify(mqtt, times=1).Client("client_id")
