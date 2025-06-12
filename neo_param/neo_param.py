from flask import Blueprint, render_template, request, redirect, url_for, flash
import json
import time
import requests
from neo_param.class_requests import Com_ports, Request_read, Request_write, Translate
import hashlib
from datetime import datetime

neo_param = Blueprint('neo_param', __name__, url_prefix='/neo_param',
                      static_folder='static', template_folder='templates')


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


@neo_param.route('/')
def neo_param_page():
    return render_template('neo_param/neo_param.html')


@neo_param.route('/mac_adresses')
def mac_adresses():
    try:
        com = Com_ports()
        # com.close_connection()
        com_ports = com.connection()
        mac_adress_list = com.mac_adress_list()

        com.close_connection()
        return render_template('neo_param/neo_param.html', mac_adress_seq=mac_adress_list, com_ports=com_ports)
    except Exception as e:
        flash("ошибка", e)
        return redirect(url_for('.neo_param_page'))
    except TypeError as e:
        flash("ошибка", e)
        return redirect(url_for('.neo_param_page'))
    except ValueError as e:
        flash("ошибка", e)


@neo_param.route('/save/<int:index>', methods=['GET', 'POST'])
async def save(index):
    serial_number = int(request.form.get(f'serial_number_{index}'))
    size = request.form.get(f'size_{index}')
    mac_adress = request.form.get(f'mac_adress_{index}')
    com_port = request.form.get(f'com_port_{index}')

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

    with open(r'neo_param/registers_for_param.json', 'r') as parameters:
        parameters = json.load(parameters)
    with open(r'neo_param/register_type.json', 'r') as registers_type:
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
    parameters['serial_number'][1] = serial_number
    parameters['meter_size'][1] = size

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
        to_html.append(
            f"Запись значения {item[1]} в регистр {item[0]}. Ответ: {response}")
        print(
            f"Запись значения {item[1]} в регистр {item[0]}. Ответ: {response}")
    return to_html
