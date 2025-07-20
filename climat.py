import paho.mqtt.client as mqtt
import time
from datetime import datetime

from app_init import Climat, db, app

mqtt_ip = "89.109.5.208"
mqtt_port = int("61612")


class SingleMessageClient:
    def __init__(self, broker, port, topic):
        self.message_received = False
        self.message = None
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(broker, port, 60)
        self.topic = topic

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        self.client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        print(f"Received message: {msg.topic} - {msg.payload.decode()}")
        self.message = msg.payload.decode()
        self.message_received = True
        self.client.loop_stop()
        self.client.disconnect()

    def get_message(self, timeout=5):
        self.client.loop_start()
        start_time = time.time()

        while not self.message_received:
            if time.time() - start_time > timeout:
                self.client.loop_stop()
                self.client.disconnect()
                raise TimeoutError(
                    "Не удалось получить сообщение в течение заданного времени")
            time.sleep(0.1)

        return self.message


# Пример использования
def climat_load():
    broker = mqtt_ip  # Замените на адрес вашего брокера
    port = mqtt_port  # Порт по умолчанию
    topic = "/devices/ivtm7m3_1/controls/Temperature"

    topics = ["/devices/ivtm7m3_1/controls/Temperature",
              "/devices/ivtm7m3_1/controls/Humidity",
              "/devices/ivtm7m3_2/controls/Temperature",
              "/devices/ivtm7m3_2/controls/Humidity",
              ]
    climat_to_download = {'Участок калибровки': {'temperature': '', 'humidity': ''},
                          'Участок сборки': {'temperature': '', 'humidity': ''}
                          }
    for topic in topics:
        try:
            client = SingleMessageClient(broker, port, topic)
            message = client.get_message()
            if topic == "/devices/ivtm7m3_1/controls/Temperature":
                climat_to_download['Участок сборки']['temperature'] = message
                print(f"Полученное сообщение: {message}")
            elif topic == "/devices/ivtm7m3_1/controls/Humidity":
                climat_to_download['Участок сборки']['humidity'] = message
                print(f"Полученное сообщение: {message}")
            elif topic == "/devices/ivtm7m3_2/controls/Temperature":
                climat_to_download['Участок калибровки']['temperature'] = message
                print(f"Полученное сообщение: {message}")
            elif topic == "/devices/ivtm7m3_2/controls/Humidity":
                climat_to_download['Участок калибровки']['humidity'] = message
                print(f"Полученное сообщение: {message}")
        except TimeoutError as e:
            print(f"Ошибка: {e}")

    print(climat_to_download)
    with app.app_context():
        for key in climat_to_download:
            add = Climat(day=datetime.now().date(), time=datetime.now().time(),
                         temperature=climat_to_download[key]['temperature'], humidity=climat_to_download[key]['humidity'],
                         place=f'{key}')
            db.session.add(add)
            db.session.commit()
