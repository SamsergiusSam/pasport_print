import paho.mqtt.client as mqtt
import json
from datetime import date, datetime

from app_init import Climat, db

mqtt_ip = "89.109.5.208"
mqtt_port = int("61111")

result = {'temp': '', 'hum': ''}
data_storage = {}


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("/devices/ivtm7m3_1/controls/Temperature")
    client.subscribe("/devices/ivtm7m3_1/controls/Humidity")
    client.subscribe("/devices/wb-gpio/controls/EXT1_K8")


def on_message(client, userdata, msg):
    global result
    day = datetime.now().date()
    time = datetime.now().time().strftime('%H:%M')
    temp = msg.payload.decode()
    temp_json = json.loads(temp)
    data_storage[msg.topic] = temp_json

    print(data_storage)
    # result_list=[]
    # result_list.append
    # print(f"Received message: {msg.topic} - {msg.payload.decode()}")
    return data_storage


def send_data(client, topic, data):
    payload = json.dumps(data)
    client.publish(topic, payload, qos=1)


# Создание клиента
client = mqtt.Client()

# Регистрация обратных вызовов
client.on_connect = on_connect
client.on_message = on_message

# Подключение к брокеру
client.connect(mqtt_ip, mqtt_port, 60)

# try:

# while True:
#     value = int(input('Введите значение '))
#     send_data(client, "/devices/wb-gpio/controls/EXT1_K8/on", value)
#     client.loop_start()

# except KeyboardInterrupt:
#     client.disconnect()

# Запуск цикла обработки сообщений
client.loop_forever()
