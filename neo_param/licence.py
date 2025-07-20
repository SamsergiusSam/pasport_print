import requests
import hashlib
import json
import time

from neo_param.class_requests import Com_ports, Request_read, Request_write, Translate


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


def connect_as_producer(com_port, mac_adress):
    delay = 0.5
    com = Com_ports()
    com.connection_to_port(com_port)
    com.close_connection()
    # com.connection()

    com.device_connection(com_port, mac_adress)

    with open(r'neo_param/registers_for_login.json', 'r') as file:
        data_for_auth = json.load(file)

    with open(r'neo_param/register_type.json', 'r') as file:
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
    to_html = [f'Данные для запроса:{request_data}']

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
        to_html.append('Авторизация прошла успешно')
    else:
        to_html.apped('Авторизация не пройдена')


def read_values_for_licence(com_port, mac_adress):

    delay = 0.5
    com = Com_ports()
    com.connection_to_port(com_port)
    com.close_connection()
    # com.connection()

    com.device_connection(com_port, mac_adress)

    with open(r'neo_param/registers_for_licence.json', 'r') as file:
        data_for_auth = json.load(file)

    with open(r'neo_param/register_type.json', 'r') as file:
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
        name = data['name']
        request_data.append(f'##{name}##{translated_answer}##')
    print('Данные для запроса ', request_data)
    to_html = [f'Данные для запроса:{request_data}']


if __name__ == "__main__":
    com_port = "COM3"
    mac_adress = "3CA5519A6A54"
    connect_as_producer(com_port, mac_adress)
    read_values_for_licence(com_port, mac_adress)
