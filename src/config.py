import os 

class Config:
    class MQTT:
        BROKER = os.environ.get("MQTT_BROKER", "mosquitto")
        PORT = int(os.environ.get("MQTT_PORT", 1883))
        KEEP_ALIVE = 60

    class Database:
        DATABASE_NAME = "sensors.db"