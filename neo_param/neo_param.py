from flask import Blueprint, render_template, request, redirect, url_for, flash
import json
import time
import requests
import hashlib
from datetime import datetime
from urllib.parse import quote
from sqlalchemy.orm import joinedload

from neo_param.class_requests import Com_ports, Request_read, Request_write, Translate
from app_init import FlowDirect, db, Distributer, psi
from licence import api_request_for_licence


neo_param = Blueprint('neo_param', __name__, url_prefix='/neo_param',
                      static_folder='static', template_folder='templates')


def calculate_lrc(data):
    # Преобразуем HEX-строку в байты
    bytes_data = bytes.fromhex(data)

    # Инициализируем LRC
    lrc = 0

    # Проходим по каждому байту
    for byte in bytes_data:
        lrc = (lrc + byte) & 0xFF

    # Вычисляем итоговый LRC
    lrc = (255 - lrc + 1) & 0xFF
    lrc_hex = hex(lrc)[2:]
    if len(lrc_hex) < 2:
        lrc_hex = '0'+str(lrc_hex)

    return lrc_hex


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


@neo_param.route('/')
def neo_param_page():
    return render_template('neo_param/neo_param.html')


@neo_param.route('/mac_adresses')
def mac_adresses():
    distrs = Distributer.query.with_entities(
        Distributer.name
    ).group_by(Distributer.name).all()
    list_of_distr = []
    for distr in distrs:
        list_of_distr.append(distr.name)
    print(list_of_distr)
    try:
        com = Com_ports()
        # com.close_connection()
        com_ports = com.connection()
        mac_adress_list = com.mac_adress_list()

        com.close_connection()
        return render_template('neo_param/neo_param.html', mac_adress_seq=mac_adress_list, com_ports=com_ports, list_of_distr=list_of_distr)
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
    meter_version = request.form.get(f'meter_version_{index}')
    mac_adress = request.form.get(f'mac_adress_{index}')
    com_port = request.form.get(f'com_port_{index}')
    if request.form.get(f'flow_direction_{index}') == "1":
        flow_direction = 1
    else:
        flow_direction = 2
    status = request.form.get(f'atm_pressure_{index}')
    # print(f'Статус переклчателя {status}')
    # atm_pressure = request.form.get(f'atm_pressure_{index}')
    if request.form.get(f'atm_pressure_{index}') == 'on':
        atm_pressure = 1
    else:
        atm_pressure = 0
    standard_pressure = request.form.get(f'standard_pressure_{index}')
    distributer_name = request.form.get(f'distr_{index}')

    delay = 0.5
    com = Com_ports()
    com.connection_to_port(com_port)
    com.close_connection()

    com.device_connection(com_port, mac_adress)
    flash("Параметризация прибора", 'info')
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
        flash('Успешная авторизация под уровнем "Производитель"', 'success')
    else:
        to_html.apped('Авторизация не пройдена')
        flash('Авторизация не пройдена', 'warning')
##########################
# проверка дисплея
##########################
    write = Request_write('4010')
    action = write.execute('true', 10)
    com.device_write(action)
    time.sleep(delay)
    response = com.device_read().decode('utf-8')
    print('Ответ: ', response)
    time.sleep(10)
    write = Request_write('4010')
    action = write.execute('false', 10)
    com.device_write(action)
    time.sleep(delay)
    response = com.device_read().decode('utf-8')
    print('Ответ: ', response)
    to_html.append('Проверка ЖКИ')
##########################
# основаное параметрирование
##########################
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
    parameters['atm_pressure'][1] = atm_pressure
    if atm_pressure == 1:
        parameters['standard_pressure'][1] = standard_pressure
    else:
        parameters['standard_pressure'][1] = '101.325'

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
        flash(
            f"Запись значения {item[1]} в регистр {item[0]}. Ответ: {response}", 'info')
        print(
            f"Запись значения {item[1]} в регистр {item[0]}. Ответ: {response}")
    ###############################
# вывод на связь
################################
    print("вывод на сервер")
    write = Request_write('4007')
    action = write.execute('true', 1)
    com.device_write(action)
    time.sleep(delay)
    com.device_read().decode('utf-8')
    time.sleep(1)
    translated_answer = ''
    while len(translated_answer.replace(' ', '')) != 37:
        # for i in range(10):
        request_read = Request_read('63')
        action = request_read.execute()
        print('Запрос короткий: ', action)
        action = bytes(':'+str(action)+'\r\n', 'utf-8')
        print('Запрос: ', action)
        print('отправляем запрос на счетчние из регистра 63')
        com.device_write(action)
        time.sleep(delay)
        print('читаем отает на запрос из регистра 63')
        response = com.device_read().decode('utf-8').replace(' ', '')
        print('Ответ: ', response)
        answer = Translate(response, '63')
        translated_answer = answer.execute()
        print(f"Ответ без пробелов {translated_answer.replace(' ','')}")
        print(
            f"Длинаответа без пробелов {len(translated_answer.replace(' ',''))}")
        time.sleep(5)
    to_html.append(f'вывели на сервер')

    '''для запсиси лицензии в файл registers_for_licence_activation.json записываем значения, полученные из функции
    api_request_for_licence из файла licence.py
    '''
    flash("Загрузка лицензии", 'info')
    with open(r'neo_param/registers_for_licence.json', 'r') as file:
        data_for_licence = json.load(file)

    with open(r'neo_param/register_type.json', 'r') as file:
        register_types_total = json.load(file)

    new_data_total = []
    for data in data_for_licence:
        register_type = register_types_total.get(data['register'])
        to_add = {'register_type': register_type}
        new_data = {**data, **to_add}
        new_data_total.append(new_data)
    print('Новые данные для обработки', new_data_total)

    request_data = []
    pi_list = []
    lic_key = []
    lic_key_hex = []
    data_for_request = {}
    for data in new_data_total:
        request_read = Request_read(data['register'])
        action = request_read.execute()
        # print('Запрос короткий: ', action)
        action = bytes(':'+str(action)+'\r\n', 'utf-8')
        # print('Запрос: ', action)
        com.device_write(action)
        time.sleep(delay)
        response = com.device_read().decode('utf-8')
        if len(response) < 5:
            com.device_write(action)
            time.sleep(delay)
            response = com.device_read().decode('utf-8')
        # print('Ответ: ', response)
        # print('Регистр для расшифровки: ', data['register'])
        answer = Translate(response, data['register'])
        translated_answer = answer.execute()
        if data['register'] in ['30095', '30097', '30099']:
            pi_list.append(translated_answer)
            if len(pi_list) == 3:
                request_data.append(
                    f'##pi##{pi_list[0]}-{pi_list[1]}-{pi_list[2]}##')
                data_for_request.update({'proc_id': pi_list})

        elif data['register'] in ['10000', '10002', '10004', '10006', '10008']:
            print(
                f'Лицензии, регистр-{data["register"]}, значение-{translated_answer}')
            lic_key.append(translated_answer)
            lic_key_hex.append(hex(translated_answer)[2:])
            if len(lic_key_hex) == 5:
                data_for_request.update({'lic_key': lic_key_hex})

        else:
            if data['register'] in ['18', '30135', '30136']:
                name = data['name']
                data_for_request.update({name: translated_answer})
                request_data.append(f'##{name}##{translated_answer}##')
            else:
                name = data['name']
                request_data.append(f'##{name}##{translated_answer}##')

        print(f"Message {request_data}")
    result_string = ','.join(request_data)
    message = quote(result_string, safe='')
    print('Данные для запроса ', result_string)
    to_html.append(f'Данные для запроса:{request_data}')
    app_id = '21817-59705-19123'
    data_for_request.update({'app_id': app_id})
    timestamp = int(time.time())
    data_for_request.update({'timestamp': timestamp})
    print(f'Данные для url запроса {data_for_request}')

    licence_keys = api_request_for_licence(data_for_request, message)
    licence_keys_list = str(licence_keys).split('-')
    licence_key_for_download = str(licence_keys).replace('-', '')
    print(licence_keys)
    print(type(licence_keys))
    print(licence_keys_list)
    print(type(licence_keys_list))

# запись лицензии в лоб
    # write = Request_write('40400')
    # action = write.execute(licence_key_for_download, 10)
    # com.device_write(action)
    # time.sleep(delay)
    # response = com.device_read().decode('utf-8')
    # print(f'Ответ на запись ключей в регистры')
    # # com.device_write(action)
    # # time.sleep(delay)
    # com.device_write(b':010503E8FF0010\r\n')
    # time.sleep(delay)
    # response = com.device_read().decode('utf-8')
    # print(f'ответ на запись true в 1000 регистр {response}')
    # com.device_write(b':0104756C000119\r\n')
    # time.sleep(delay)
    # response = com.device_read().decode('utf-8')
    # print(f'Статус загрузки лицензии {response}')
    # to_html.append(f'Статус активации лицензии: {response}')
##########

    with open(r'neo_param/registers_for_licence_activation.json', 'r') as file:
        data_for_licence_activation = json.load(file)

    data_for_licence_activation["key_licence_1"][1] = licence_keys_list[0]
    data_for_licence_activation["key_licence_2"][1] = licence_keys_list[1]
    data_for_licence_activation["key_licence_3"][1] = licence_keys_list[2]
    data_for_licence_activation["key_licence_4"][1] = licence_keys_list[3]
    data_for_licence_activation["key_licence_5"][1] = licence_keys_list[4]

    parameters_from_json = list(data_for_licence_activation.values())
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


################################
# измениение пароля поставщика
#################################
    distributer = db.session.query(Distributer)\
        .options(joinedload(Distributer.supplier_password))\
        .filter_by(name=distributer_name)\
        .first()
    password = distributer.supplier_password.password
    password_to_download = md5_calc_for_password(password)
    write = Request_write('8010')
    action = write.execute(password_to_download)
    com.device_write(action)
    time.sleep(delay)
    response = com.device_read().decode('utf-8')
    print('Ответ: ', response)
    time.sleep(delay)
    com.device_write(b':01031F55000187\r\n')
    time.sleep(delay)
    response = com.device_read().decode('utf-8')
    to_html.append(
        f"Запись нового пароля поставщика. Ответ: {response}")

    distr_to_sell = Distributer.query.filter_by(name=distributer_name).first()
    distr_to_sell_id = distr_to_sell.id
    add = FlowDirect(serial_number=serial_number,
                     flow_direction=flow_direction, distr_to_sell_id=distr_to_sell_id, meterVersion=meter_version)

    db.session.add(add)
    db.session.commit()
    to_html.append('Направление потока в базу загружено')

    # выключение ble
    write = Request_write('4048')
    action = write.execute('true', 1)
    com.device_write(action)
    time.sleep(delay)
    com.device_read().decode('utf-8')

    return to_html


@neo_param.route('/param_values', methods=["GET", "POST"])
def param_values():
    with open(r'neo_param/registers_for_param.json', 'r') as file:
        param_values = json.load(file)
    # return param_values
    return render_template('neo_param/param_values.html', param_values=param_values)


@neo_param.route('/param_values_save', methods=["POST"])
def param_values_save():
    form_values = request.form
    with open(r'neo_param/registers_for_param.json', 'r') as file:
        old_values = json.load(file)

    for key, value in form_values.items():

        if value != old_values[key][1]:
            updated_value = [old_values[key][0], value, old_values[key][2]]
            print(updated_value)
            old_values[key] = updated_value

    with open(r'neo_param/registers_for_param.json', 'w', encoding='utf-8') as f:
        json.dump(old_values, f, ensure_ascii=False, indent=4)
    return redirect(url_for('.neo_param_page'))
