import logging
import os

from paho.mqtt.client import Client, MQTTMessage, MQTTMessageInfo # type: ignore
from typing import Callable, Any, Dict
from config import Config

class MQTTMessageService:
    """
    Service responsible for handling MQTT publishing and subscriptions to the mosquitto broker.
    """

    def __init__(self, mqtt_client: Client):
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.client = mqtt_client
        self.client.on_connect=self._on_connect
        self.subscriptions: Dict[str, Callable] = {}

    def start(self) ->  None:
        """
        Start the MQTT client loop and begin handling messages
        """
        if not self.running:
            self.client.loop_start()
            self.client.connect(host=Config.MQTT.BROKER, port=Config.MQTT.PORT, keepalive=Config.MQTT.KEEP_ALIVE)
            self.running = True
            self.subscriptions = {}

    def stop(self) ->  None:
        """
        Stop the MQTT client loop and cease handling messages
        """
        if self.running:
            self.client.loop_stop()
            self.client.disconnect()
            self.running = False
            self.subscriptions = {}

    def subscribe(self, topic: str, handler: Callable[[Client, Any, MQTTMessage], Any]) -> None:
        """
        Subscribe to a given topic. When a message is received for the topic, the provided handler will be called.

        Parameters:
            topic:   The topic name to subscribe to.
            handler: A callback function to be executed when a message is received for this topic.
        """

        if topic not in self.subscriptions:
            self.logger.debug(f"Subscribing to topic {topic}")
            self.subscriptions[topic] = handler
            self.client.subscribe(topic)
            self.client.message_callback_add(topic, handler)
        else:
            self.logger.warning("Attempted to subscribe to a topic already subscribed to")

    def unsubscribe(self, topic: str) -> None:
        """
        Unsubscribe from a given topic.

        Parameters:
            topic: The topic name to stop receiving messages for.
        """
        if topic in self.subscriptions:
            self.logger.debug(f"Unsubscribing to topic {topic}")
            self.subscriptions.pop(topic)
            self.client.unsubscribe(topic)
            self.client.message_callback_remove(topic)
        else:
            self.logger.warning("Attempted to unsubscribe from a topic not subscribed to")

    def publish(self, topic: str, message: str) -> MQTTMessageInfo:
        """
        Publish a message onto a given topic.

        Parameters:
            topic:   The topic name to publish a message to.
            message: The message that will be published to the MQTT broker.
        """
        self.logger.debug(f"Publishing message {message} on topic {topic}")
        return self.client.publish(
            topic=topic,
            payload=message
        )

    def _on_connect(self, client, userdata, flags, rc):
        self.logger.debug("Connected to MQTT broker")