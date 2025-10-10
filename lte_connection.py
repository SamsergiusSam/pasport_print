import requests
import hashlib
import json
import time
from urllib.parse import quote

from class_req import Com_ports, Request_read, Request_write, Translate


def md5_calc(data_to_request):
    text = f"{data_to_request[3]}-{str(data_to_request[4]).zfill(2)}-{data_to_request[5]}-neo"
    hash_object = hashlib.md5(text.encode('utf-8')).hexdigest()
    return hash_object


def md5_calc_for_licence(data_to_request):
    text = f"{data_to_request['lic_key'][0]}-{data_to_request['lic_key'][1]}-{data_to_request['lic_key'][2]}-{data_to_request['lic_key'][3]}-{data_to_request['lic_key'][4]}-{data_to_request['timestamp']}neo"
    print(f'конструкция для md5 {text}')
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


def api_request_for_licence(data_to_request, message):

    url = f"https://neo-manager.ru/api/keys.php?appId={data_to_request['app_id']}&licKey={data_to_request['lic_key'][0]}-{data_to_request['lic_key'][1]}-{data_to_request['lic_key'][2]}-{data_to_request['lic_key'][3]}-{data_to_request['lic_key'][4]}&imei={data_to_request['im']}&procId={data_to_request['proc_id'][0]}-{data_to_request['proc_id'][1]}-{data_to_request['proc_id'][2]}&deviceNum={data_to_request['dn']}&deviceType={data_to_request['dt']}&message={message}&crc={data_to_request['timestamp']}.{md5_calc_for_licence(data_to_request)}"
    print("Url for request", url)
    headers = {
        'Api-Key': 'IYYrqffqeWF9esyMvTrF586OqqywN2Dd3xk6L8vUjtUZDN46ocBM5K5TXrG4Cd58'}
    response = requests.get(url, headers=headers)
    api_answer = response.json()
    print(api_answer)
    if api_answer['error'] == 0:
        key = api_answer['key']
    else:
        print(api_answer['message'])
    return key


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
    # print(f'статус отправки данных {translated_answer}')


def read_values_for_licence(com_port, mac_adress):

    delay = 0.4
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
    encoded_result_string = quote(result_string, safe='')
    print('Данные для запроса ', result_string)
    to_html = [f'Данные для запроса:{request_data}']
    app_id = '21817-59705-19123'
    data_for_request.update({'app_id': app_id})
    timestamp = int(time.time())
    data_for_request.update({'timestamp': timestamp})
    print(f'Данные для url запроса {data_for_request}')

    return encoded_result_string, data_for_request


def download_licence(com_port, mac_adress):
    message, data_for_request = read_values_for_licence(com_port, mac_adress)
    key = api_request_for_licence(data_for_request, message)
    return key


if __name__ == "__main__":
    delay = 0.5
    com_port = "COM4"
    mac_adress = "3CA5519A6A54"
    connect_as_producer(com_port, mac_adress)

    # com = Com_ports()
    # com.connection_to_port(com_port)
    # com.close_connection()
    # # com.connection()

    # com.device_connection(com_port, mac_adress)
    # write = Request_write('4007')
    # action = write.execute('true', 1)
    # com.device_write(action)
    # time.sleep(delay)
    # time.sleep(20)
    # request_read = Request_read('30148')
    # action = request_read.execute()
    # # print('Запрос короткий: ', action)
    # action = bytes(':'+str(action)+'\r\n', 'utf-8')
    # # print('Запрос: ', action)
    # com.device_write(action)
    # time.sleep(delay)
    # response = com.device_read().decode('utf-8')
    # if len(response) < 5:
    #     com.device_write(action)
    #     time.sleep(delay)
    #     response = com.device_read().decode('utf-8')
    #     # print('Ответ: ', response)
    #     # print('Регистр для расшифровки: ', data['register'])
    # answer = Translate(response, '30148')
    # translated_answer = answer.execute()
    # print(f'статус отправки данных {translated_answer}')
    # # response = com.device_read().decode('utf-8')
    # # message, data_for_request = read_values_for_licence(com_port, mac_adress)
    # # api_request_for_licence(data_for_request, message)
