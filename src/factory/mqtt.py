from paho.mqtt.client import Client # type: ignore

class MQTTClientFactory:
    def __init__(self):
        pass

    @classmethod
    def get_mqtt_client(self, client_id: str= None) -> Client:
        """
        Returns an MQTT client for a given client ID

        Parameters:
            client_id: The client ID to use with the MQTT broker.
        """
        return Client(client_id)