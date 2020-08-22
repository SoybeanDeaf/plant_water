from paho.mqtt.client import Client # type: ignore

class MQTTClientFactory:
    @classmethod
    def get_mqtt_client(self, client_id: str) -> Client:
        """
        Returns an MQTT client for a given client ID

        Parameters:
            client_id: The client ID to use with the MQTT broker.
        """
        return Client(client_id)