import json
import time
import serial
import sys
import hashlib
import requests
import logging
from datetime import datetime

from class_conection import Connection
from class_requests import Request_read, Translate, Com_ports, Request_write


def md5_calc(data_to_request):
    text = f"{data_to_request[3]}-{str(data_to_request[4]).zfill(2)}-{data_to_request[5]}-neo"
    hash_object = hashlib.md5(text.encode('utf-8')).hexdigest()
    return hash_object


def api_request(data_to_request):

    url = f"https://neo-manager.ru/api/getPassword.php?datetime={data_to_request[2]}-{str(data_to_request[1]).zfill(2)}-{str(data_to_request[0]).zfill(2)}&procId={data_to_request[3]}-{data_to_request[4]}-{data_to_request[5]}&deviceNum={data_to_request[6]}&crc={md5_calc(data_to_request)}"
    print("Url for request", url)
    headers = {
        'Api-Key': 'IYYrqffqeWF9esyMvTrF586OqqywN2Dd3xk6L8vUjtUZDN46ocBM5K5TXrG4Cd58'}
    response = requests.get(url, headers=headers)
    api_answer = response.json()
    print(api_answer)
    return api_answer

# ports = serial.tools.list_ports.comports()


# ports_list = list()
# for port in ports:
#     ports_list.append(port.name)
# print(ports_list)

# if len(ports_list) == 0:
#     raise ValueError("No com ports")
# port_to_connect = str(ports_list[0])  # Записываю первый порт из спика

# # Устанавливаем соединение с портом (замените 'COM3' на ваш реальный порт)
# ser = serial.Serial(
#     port=port_to_connect,
#     baudrate=115200,
#     # parity=serial.PARITY_NONE,
#     # stopbits=serial.STOPBITS_ONE,
#     # bytesize=serial.EIGHTBITS,
#     timeout=1
# )

# # Проверяем, что порт открыт
# if ser.is_open:
#     print("Порт открыт")
#     ser.setRTS(True)  # переводим RTS в логическую 1
#     ser.setDTR(False)  # переводим DTR  в логический 0

#     # Отправляем команду AT+SCAN
#     ser.write(b'AT+SCAN\r\n')

#     # Ждем ответа (можно настроить время ожидания)
#     time.sleep(5)

#     # Читаем ответ
#     response = ser.read(ser.in_waiting)
#     answers = response.decode('utf-8').split('DEV')
#     print(answers)

#     mac_adresses = []
#     while found:
#         for answer in answers:
#             if 'NEO' in answer:
#                 print(answer)
#                 start = answer.find('=') + 1
#                 end = answer.find(',')
#                 mac_adress = answer[start:end]
#                 print(mac_adress)

#                 if mac_adress not in mac_adresses:
#                     mac_adresses.append(mac_adress)

#                 print(mac_adresses)
#             else:
#                 found = True
#                 print('no neo')

#     if len(mac_adresses) == 0:
#         print('No neo')
#         sys.exit(0)

#     for adress in mac_adresses:
#         answers = str()
#         while 'CONNECTED' not in str(answers):
#             ser.write(b'AT+DISC\r\n')
#             time.sleep(5)
#             action = ('AT+CONN' + adress + '\r\n').encode('utf-8')
#             print(action)
#             ser.write(action)

#         # Ждем ответа (можно настроить время ожидания)
#             time.sleep(7)

#         # Читаем ответ
#             response = ser.read(ser.in_waiting)
#             answers = response.decode('utf-8')
#             print(answers)

#         ser.setRTS(False)  # переводим RTS в логический 0
#         ser.setDTR(False)  # переводим DTR  в логический 0
delay = 1
com = Com_ports()
com.connection()
mac_adress_seq = com.mac_adress_list()
mac_adress = list(mac_adress_seq.keys())[0]

com.device_connection(mac_adress_seq, mac_adress)

with open('registers_for_login.json', 'r') as file:
    data_for_auth = json.load(file)

with open('register_type.json', 'r') as file:
    register_types_total = json.load(file)

new_data_total = []
for data in data_for_auth:
    register_type = register_types_total.get(data['register'])
    to_add = {'register_type': register_type}
    new_data = {**data, **to_add}
    new_data_total.append(new_data)
print('Новые данные для обработки', new_data_total)

request_data = []
for data in new_data_total:
    request_read = Request_read(data['register'])
    action = request_read.execute()
    print('Запрос короткий: ', action)
    action = bytes(':'+str(action)+'\r\n', 'utf-8')
    print('Запрос: ', action)
    com.device_write(action)
    time.sleep(delay)
    com.device_write(action)
    time.sleep(delay)
    response = com.device_read().decode('utf-8')
    print('Ответ: ', response)
    print('Регистр для расшифровки: ', data['register'])
    answer = Translate(response, data['register'])
    translated_answer = answer.execute()
    request_data.append(translated_answer)
print('Данные для запроса ', request_data)

password = api_request(request_data)
print(password['password'])
write = Request_write('8000')
action = write.execute(password['password'], 10)
com.device_write(action)
time.sleep(delay)
com.device_write(action)
time.sleep(delay)
response = com.device_read().decode('utf-8')
print('Ответ: ', response)
com.device_write(b':01031F54000485\r\n')
time.sleep(delay)
com.device_write(b':01031F54000485\r\n')
time.sleep(delay)
response = com.device_read().decode('utf-8')
print('Статус авторизации полный: ', response)
print('Статус авторизации: ', response[7:11])
if response[7:11] == '0002':
    print('Авторизация прошла успешно!')
else:
    print('Авторизация не прошла')
    sys.exit(0)


###############################################
# загрузка необходмых значений параметров
############################################
what_to_do = input(
    'Что делаем?  (параметрирование -1, запуск калибровки -2, остановка калибровки -3, запуск поверки -4')

if what_to_do == '1':
    with open('registers_for_param.json', 'r') as parameters:
        parameters = json.load(parameters)
    with open('register_type.json', 'r') as registers_type:
        registers_type = json.load(registers_type)
    year = str(datetime.now().year)
    month = str(datetime.now().month)
    day = str(datetime.now().day)
    hour = str(datetime.now().hour)
    minute = str(datetime.now().minute)

    parameters['year'][1] = year
    parameters['month'][1] = month
    parameters['day'][1] = day
    parameters['hour'][1] = hour
    parameters['minute'][1] = minute
    parameters['serial_number'][1] = input(str("Введите серийный номер: "))
    parameters['meter_size'][1] = input(str("Введите типоразмер счетчика: "))

    parameters_from_json = list(parameters.values())
    print(parameters_from_json)

    parameters_total = []

    for item in parameters_from_json:
        to_add = registers_type.get(str(item[0]))
        print(f"{item[0]} ,to_add value {to_add}")
        extanded = item + [to_add]
        parameters_total.append(extanded)

    for item in parameters_total:
        request_write = Request_write(item[0])
        action = request_write.execute(item[1], 0)
        com.device_write(action)
        time.sleep(delay)
        com.device_write(action)
        time.sleep(delay)
        response = com.device_read().decode('utf-8')
        print(
            f"Запись значения {item[1]} в регистр {item[0]}. Ответ: {response}")

elif what_to_do == '2':
    with open('start_calibration.json', 'r') as file:
        parameters = json.load(file)

    with open('register_type.json', 'r') as file:
        register_type = json.load(file)

    parameters_from_json = list(parameters.values())
    print(parameters_from_json)

    parameters_total = []

    for item in parameters_from_json:
        to_add = register_type.get(str(item[0]))
        print(f"{item[0]} ,to_add value {to_add}")
        extanded = item + [to_add]
        parameters_total.append(extanded)

    for item in parameters_total:
        request_write = Request_write(item[0])
        action = request_write.execute(item[1], 0)
        com.device_write(action)
        time.sleep(delay)
        com.device_write(action)
        time.sleep(delay)
        response = com.device_read().decode('utf-8')
        print(
            f"Запись значения {item[1]} в регистр {item[0]}. Ответ: {response}")

elif what_to_do == '3':
    with open('stop_calibration.json', 'r') as file:
        parameters = json.load(file)

    with open('register_type.json', 'r') as file:
        register_type = json.load(file)

    parameters_from_json = list(parameters.values())
    print(parameters_from_json)

    parameters_total = []

    for item in parameters_from_json:
        to_add = register_type.get(str(item[0]))
        print(f"{item[0]} ,to_add value {to_add}")
        extanded = item + [to_add]
        parameters_total.append(extanded)

    for item in parameters_total:
        request_write = Request_write(item[0])
        action = request_write.execute(item[1], 0)
        com.device_write(action)
        time.sleep(delay)
        com.device_write(action)
        time.sleep(delay)
        response = com.device_read().decode('utf-8')
        print(
            f"Запись значения {item[1]} в регистр {item[0]}. Ответ: {response}")

elif what_to_do == '4':
    with open('start_verification.json', 'r') as file:
        parameters = json.load(file)

    with open('register_type.json', 'r') as file:
        register_type = json.load(file)

    parameters_from_json = list(parameters.values())
    print(parameters_from_json)

    parameters_total = []

    for item in parameters_from_json:
        to_add = register_type.get(str(item[0]))
        print(f"{item[0]} ,to_add value {to_add}")
        extanded = item + [to_add]
        parameters_total.append(extanded)

    for item in parameters_total:
        request_write = Request_write(item[0])
        action = request_write.execute(item[1], 1)
        com.device_write(action)
        time.sleep(delay)
        com.device_write(action)
        time.sleep(delay)
        response = com.device_read().decode('utf-8')
        print(
            f"Запись значения {item[1]} в регистр {item[0]}. Ответ: {response}")

    read_satatus = Request_read('40057')
    action = read_satatus.execute()
    action = bytes(':'+str(action)+'\r\n', 'utf-8')
    com.device_write(action)
    time.sleep(delay)
    com.device_write(action)
    time.sleep(delay)
    responce = com.device_read().decode('utf-8')
    print('Статус поверки: ', responce)
    # answer = Translate(response, '40057')
    # answer.execute()
    # print('Статус поверки: ', answer.execute())
    # translated_answer = answer.execute()
    # print('Статус поверки: ', translated_answer)
    while translated_answer != '5':
        com.device_write(action)
        time.sleep(delay)
        com.device_write(action)
        time.sleep(delay)
        responce = com.device_read().decode('utf-8')
        print('Статус поверки: ', responce)
        # answer = Translate(response, '40057')
        # answer.execute()
        # print('Статус поверки: ', answer.execute())
        # translated_answer = answer.execute()
        # print('Статус поверки: ', translated_answer)
        time.sleep(10)

elif what_to_do == '5':
    with open('registers_for_verification.json', 'r') as file:
        data_for_auth = json.load(file)

    with open('register_type.json', 'r') as file:
        register_types_total = json.load(file)

    new_data_total = []
    for data in data_for_auth:
        register_type = register_types_total.get(data['register'])
        to_add = {'register_type': register_type}
        new_data = {**data, **to_add}
        new_data_total.append(new_data)
    print('Новые данные для обработки', new_data_total)

    request_data = []
    for data in new_data_total:
        request_read = Request_read(data['register'])
        action = request_read.execute()
        print('Запрос короткий: ', action)
        action = bytes(':'+str(action)+'\r\n', 'utf-8')
        print('Запрос: ', action)
        com.device_write(action)
        time.sleep(delay)
        com.device_write(action)
        time.sleep(delay)
        response = com.device_read().decode('utf-8')
        print('Ответ: ', response)
        print('Регистр для расшифровки: ', data['register'])
        answer = Translate(response, data['register'])
        translated_answer = answer.execute()
        request_data.append(translated_answer)
    print('Данные для запроса ', request_data)

com.set_rts(True)  # переводим RTS в логический 1
com.set_dtr(False)
com.device_write(b'AT+DISC\r\n')
time.sleep(delay)
print(com.device_read().decode('utf-8'))
com.close_connection()

print('Параметрирование завершено')
