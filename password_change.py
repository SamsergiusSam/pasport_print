import requests
import hashlib
import json
import time
from urllib.parse import quote
from sqlalchemy.orm import joinedload

from app_init import Distributer, Supplier_password, app
from class_requests import Com_ports, Request_read, Request_write, Translate


def md5_calc_for_password(value):
    hash_object = hashlib.md5(value.encode('utf-8')).hexdigest()
    return hash_object


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
    delay = 0.2
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
        to_html.append('Авторизация не пройдена')


def supplier_password(distributer_name):
    distributer = Distributer.query.options(joinedload(
        Distributer.supplier_pas)).filter_by(name=str(distributer_name)).first()

    password = distributer.supplier_pas.password
    return password


def download_password(com_port, mac_adress, distr):
    print(supplier_password(distr))
    password_to_download = md5_calc_for_password(supplier_password(distr))
    delay = 0.2
    com = Com_ports()
    com.connection_to_port(com_port)
    com.close_connection()
    # com.connection()

    com.device_connection(com_port, mac_adress)
    write = Request_write('8010')
    action = write.execute(password_to_download)
    com.device_write(action)
    time.sleep(delay)
    response = com.device_read().decode('utf-8')
    print('Ответ: ', response)

    com.device_write(b':01031F55000187\r\n')
    time.sleep(delay)
    response = com.device_read().decode('utf-8')
    print(f'статус записи нового пароля {response}')
    return "password has been changed"


if __name__ == "__main__":
    with app.app_context():
        com_port = "COM4"
        mac_adress = "3CA5519A6A54"
        distr = "Промтепло"

        connect_as_producer(com_port, mac_adress)
        download_password(com_port, mac_adress, distr)
