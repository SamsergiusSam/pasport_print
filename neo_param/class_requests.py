import struct
import serial
import time
import sys
import serial.tools.list_ports
from decimal import Decimal, getcontext
import json

with open(r'neo_param\register_type.json', 'r') as file:
    type_value = json.load(file)


class Request_write:

    def __init__(self, register):
        self.register = register
        self.type_value = type_value[str(self.register)]

    @staticmethod
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

    @staticmethod
    def swap_16bit_words(hex_str):
        # Проверяем, что длина строки кратна 4
        if len(hex_str) % 4 != 0:
            raise ValueError("Длина строки должна быть кратна 4")

        # Разбиваем строку на 16-битные слова
        words = [hex_str[i:i+4] for i in range(0, len(hex_str), 4)]

        # Переставляем байты в каждом слове
        swapped_words = [word[2:] + word[:2] for word in words]

        # Объединяем результат
        return ''.join(swapped_words)

    def write_uint16(self, value):
        register_hex = hex(int(self.register))[2:]
        value_hex = hex(int(value))[2:]
        if len(value_hex) < 2:
            value_hex = '0'+str(value_hex)
        print('Registr value (dec)', self.register)
        print('Regist value (hex): ', register_hex)
        print('Value value (dec)', value)
        print('Value value (hex): ', value_hex)
        if len(value_hex) < 3:
            value_hex = '00'+str(value_hex)
        elif len(value_hex) < 4:
            value_hex = '0'+str(value_hex)
        print('Value value (dec)', value)
        print('Value value (hex): ', value_hex)
        to_lrc_calc = '0106'+str(register_hex)+str(value_hex)
        print('For lrc calc ', to_lrc_calc)
        lrc = self.calculate_lrc(to_lrc_calc)
        print('lrc: ', lrc)
        action = str(to_lrc_calc)+str(lrc)
        print('Action ', action)
        action_bytes = bytes(':'+str(action)+'\r\n', 'utf-8')
        print('Action in bytes ', action_bytes)
        return action_bytes

    def write_uint32(self, value):
        register_hex = hex(int(self.register))[2:].zfill(4)
        value_hex = hex(int(value))[2:].zfill(8)
        print('Значение в шестнадцатеричной системе:', value_hex)

        words = [value_hex[i:i+8] for i in range(0, len(value_hex), 8)]

# Переставляем байты в каждом слове
        swapped_words = [word[4:] + word[:4] for word in words]
        swapped_value = ' '.join(swapped_words)

        print('Registr value (dec)', self.register)
        print('Regist value (hex): ', register_hex)
        print('Value value (dec)', value)
        print('Value value (hex): ', value_hex)
        print('Value value (hex): ', swapped_value)

        to_lrc_calc = '0110'+str(register_hex)+'0002'+'04'+str(swapped_value)
        print('For lrc calc ', to_lrc_calc)
        lrc = self.calculate_lrc(to_lrc_calc)
        print('lrc: ', lrc)
        action = str(to_lrc_calc)+str(lrc)
        print('Action ', action)
        action_bytes = bytes(':'+str(action)+'\r\n', 'utf-8')
        print('Action in bytes ', action_bytes)
        return action_bytes

    def write_uint16_swap(self, value):
        register_hex = hex(int(self.register))[2:]
        value_hex = hex(int(value))[2:].zfill(4)
        # if len(value_hex) < 2:
        #     value_hex = '0'+str(self.value_hex)
        print('Registr value (dec)', self.register)
        print('Regist value (hex): ', register_hex)
        print('Value value (dec)', value)
        print('Value value (hex): ', value_hex)
        # if len(value_hex) < 3:
        #     value_hex = '00'+str(value_hex)
        # elif len(value_hex) < 4:
        #     value_hex = '0'+str(value_hex)
        print('Value value (dec)', value)
        print('Value value (hex): ', value_hex)
        to_lrc_calc = '0106'+str(register_hex)+str(value_hex)
        print('For lrc calc ', to_lrc_calc)
        lrc = self.calculate_lrc(to_lrc_calc)
        print('lrc: ', lrc)
        action = str(to_lrc_calc)+str(lrc)
        print('Action ', action)
        action_bytes = bytes(':'+str(action)+'\r\n', 'utf-8')
        print('Action in bytes ', action_bytes)
        return action_bytes

    def write_int16(self, value):
        register_hex = hex(int(self.register))[2:]
        value_hex = struct.pack('>h', int(value)).hex().zfill(2)
        # if len(value_hex) < 2:
        #     value_hex = '0'+str(self.value_hex)
        print('Registr value (dec)', self.register)
        print('Regist value (hex): ', register_hex)
        print('Value value (dec)', value)
        print('Value value (hex): ', value_hex)
        to_lrc_calc = '0106'+str(register_hex)+str(value_hex)
        print('For lrc calc ', to_lrc_calc)
        lrc = self.calculate_lrc(to_lrc_calc)
        print('lrc: ', lrc)
        action = str(to_lrc_calc)+str(lrc)
        print('Action ', action)
        action_bytes = bytes(':'+str(action)+'\r\n', 'utf-8')
        print('Action in bytes ', action_bytes)
        return action_bytes

    def write_coil(self, value):
        register_hex = hex(int(self.register))[2:].zfill(4)
        # if len(register_hex) < 4:
        #     register_hex = '0'+str(register_hex)
        print('Registr value (dec)', self.register)
        print('Regist value (hex): ', register_hex)
        if value == 'true':
            value_hex = 'FF00'
        else:
            value_hex = '0000'
        to_lrc_calc = '0105'+str(register_hex)+str(value_hex)
        print('For lrc calc ', to_lrc_calc)
        lrc = self.calculate_lrc(to_lrc_calc)
        print('lrc: ', lrc)
        action = str(to_lrc_calc)+str(lrc)
        print('Action: ', action)
        action_bytes = bytes(':'+str(action)+'\r\n', 'utf-8')
        print('Action in bytes: ', action_bytes)
        return action_bytes

    def write_float32(self, value):
        register_hex = hex(int(self.register))[2:]
        value_hex = hex(struct.unpack(
            '<I', struct.pack('<f', float(value)))[0])[2:]
        swapped_words = value_hex[4:]+value_hex[:4]
        print('Registr value (dec)', self.register)
        print('Regist value (hex): ', register_hex)
        print('Value value (dec)', value)
        print('Value value (hex): ', value_hex)
        print('Swapped value (hex): ', swapped_words)
        to_lrc_calc = '0110'+str(register_hex)+'0002'+'04'+str(swapped_words)
        print('For lrc calc ', to_lrc_calc)
        lrc = self.calculate_lrc(to_lrc_calc)
        print('lrc: ', lrc)
        action = str(to_lrc_calc)+str(lrc)
        print('Action ', action)
        action_bytes = bytes(':'+str(action)+'\r\n', 'utf-8')
        print('Action in bytes ', action_bytes)
        return action_bytes

    def multi_register_write(self, value, number_of_registers):
        register_hex = hex(int(self.register))[2:]
        print('Количество регистров (hex) ', register_hex)
        value_hex = self.swap_16bit_words(value)
        print('Значение с перестановкой байтов: ', value_hex)
        number_of_registers_hex = hex(number_of_registers)[2:].zfill(4)
        print('Количество регистров (hex): ', number_of_registers_hex)
        number_of_bytes = hex(number_of_registers*2)[2:]
        print('Количество байт (hex): ', number_of_bytes)
        to_lrc_calc = '0110'+str(register_hex) + \
            str(number_of_registers_hex) + \
            str(number_of_bytes)+'0010'+str(value_hex)+'0001'
        print('For lrc calc ', to_lrc_calc)
        lrc = self.calculate_lrc(to_lrc_calc)
        print('lrc: ', lrc)
        action = str(to_lrc_calc)+str(lrc)
        print('Action ', action)
        action_bytes = bytes(':'+str(action)+'\r\n', 'utf-8')
        print('Action in bytes ', action_bytes)
        return action_bytes

    # def input_float_32(self, value):
    #     number_of_registers=2
    #     register_hex = hex(int(self.register))[2:]
    #     print('Количество регистров (hex) ', register_hex)
    #     value_hex = self.swap_16bit_words(value)
    #     print('Значение с перестановкой байтов: ', value_hex)
    #     number_of_registers_hex = hex(number_of_registers)[2:].zfill(4)
    #     print('Количество регистров (hex): ', number_of_registers_hex)
    #     number_of_bytes = hex(number_of_registers*2)[2:]
    #     print('Количество байт (hex): ', number_of_bytes)
    #     to_lrc_calc = '0110'+str(register_hex) + \
    #         str(number_of_registers_hex) + \
    #         str(number_of_bytes)+'0010'+str(value_hex)
    #     print('For lrc calc ', to_lrc_calc)
    #     lrc = self.calculate_lrc(to_lrc_calc)
    #     print('lrc: ', lrc)
    #     action = str(to_lrc_calc)+str(lrc)
    #     print('Action ', action)
    #     action_bytes = bytes(':'+str(action)+'\r\n', 'utf-8')
    #     print('Action in bytes ', action_bytes)
    #     return action_bytes

    def write_string(self, value):
        register_hex = hex(int(self.register))[2:].zfill(2)
        print('Registr value (dec)', self.register)
        print('Regist value (hex): ', register_hex)
        value_hex = value.encode('utf-8').hex()
        print('Value value (dec)', value)
        print('Value value (hex): ', value_hex)
        to_lrc_calc = '0171'+str(register_hex)+str(value_hex)
        print('For lrc calc ', to_lrc_calc)
        lrc = self.calculate_lrc(to_lrc_calc)
        print('lrc: ', lrc)
        action = str(to_lrc_calc)+str(lrc)
        print('Action ', action)
        action_bytes = bytes(':'+str(action)+'\r\n', 'utf-8')
        print('Action in bytes ', action_bytes)
        return action_bytes

    def execute(self, value, number_of_registers):
        if self.type_value == 'uint16':
            print("Run uint16 class method")
            result = self.write_uint16(value)
        elif self.type_value == 'int16':
            result = self.write_int16(value)
        elif self.type_value == 'coil':
            result = self.write_coil(value)
        elif self.type_value == 'multi':
            print('Run "multi" class method')
            result = self.multi_register_write(value, number_of_registers)
        elif self.type_value == 'uint32':
            result = self.write_uint32(value)
        elif self.type_value == 'string':
            result = self.write_string(value)
        elif self.type_value == 'input_float32' or self.type_value == 'float32':
            result = self.write_float32(value)
        else:
            result = 'Нет такого типа регистра'
        return result


class Request_read(Request_write):
    def __init__(self, register):
        self.register = register
        self.type_value = type_value[str(self.register)]

    def read_uint16(self):
        register_hex = hex(int(self.register))[2:].zfill(4)
        print('Registr value (dec)', self.register)
        print('Regist value (hex): ', register_hex)
        to_lrc_calc = '0103'+str(register_hex)+'0001'
        print('For lrc calc ', to_lrc_calc)
        lrc = self.calculate_lrc(to_lrc_calc)
        print('lrc: ', lrc)
        action = str(to_lrc_calc)+str(lrc)
        print('Action ', action)
        action_bytes = bytes(':'+str(action)+'\r\n', 'utf-8')
        print('Action in bytes ', action_bytes)
        return action

    def read_string(self):
        register_hex = hex(int(self.register))[2:].zfill(4)
        print('Registr value (dec)', self.register)
        print('Regist value (hex): ', register_hex)
        to_lrc_calc = '0170'+str(register_hex)
        print('For lrc calc ', to_lrc_calc)
        lrc = self.calculate_lrc(to_lrc_calc)
        print('lrc: ', lrc)
        action = str(to_lrc_calc)+str(lrc)
        print('Action ', action)
        action_bytes = bytes(':'+str(action)+'\r\n', 'utf-8')
        print('Action in bytes ', action_bytes)
        return action

    def read_uint32(self):
        register_hex = hex(int(self.register))[2:].zfill(4)
        print('Registr value (dec)', self.register)
        print('Regist value (hex): ', register_hex)
        to_lrc_calc = '0103'+str(register_hex)+'0002'
        print('For lrc calc ', to_lrc_calc)
        lrc = self.calculate_lrc(to_lrc_calc)
        print('lrc: ', lrc)
        action = str(to_lrc_calc)+str(lrc)
        print('Action ', action)
        action_bytes = bytes(':'+str(action)+'\r\n', 'utf-8')
        print('Action in bytes ', action_bytes)
        return action

    def read_input16(self):
        register_hex = hex(int(self.register))[2:].zfill(4)
        print('Registr value (dec)', self.register)
        print('Regist value (hex): ', register_hex)
        to_lrc_calc = '0104'+str(register_hex)+'0001'
        print('For lrc calc ', to_lrc_calc)
        lrc = self.calculate_lrc(to_lrc_calc)
        print('lrc: ', lrc)
        action = str(to_lrc_calc)+str(lrc)
        print('Action ', action)
        action_bytes = bytes(':'+str(action)+'\r\n', 'utf-8')
        print('Action in bytes ', action_bytes)
        return action

    def read_input32(self):
        register_hex = hex(int(self.register))[2:].zfill(4)
        print('Registr value (dec)', self.register)
        print('Regist value (hex): ', register_hex)
        to_lrc_calc = '0104'+str(register_hex)+'0002'
        print('For lrc calc ', to_lrc_calc)
        lrc = self.calculate_lrc(to_lrc_calc)
        print('lrc: ', lrc)
        action = str(to_lrc_calc)+str(lrc)
        print('Action ', action)
        action_bytes = bytes(':'+str(action)+'\r\n', 'utf-8')
        print('Action in bytes ', action_bytes)
        return action

    def read_string(self):
        register_hex = hex(int(self.register))[2:].zfill(2)
        print('Registr value (dec)', self.register)
        print('Regist value (hex): ', register_hex)
        to_lrc_calc = '0170'+str(register_hex)
        print('For lrc calc ', to_lrc_calc)
        lrc = self.calculate_lrc(to_lrc_calc)
        print('lrc: ', lrc)
        action = str(to_lrc_calc)+str(lrc)
        print('Action ', action)
        action_bytes = bytes(':'+str(action)+'\r\n', 'utf-8')
        print('Action in bytes ', action_bytes)
        return action

    def read_float32(self):
        register_hex = hex(int(self.register))[2:].zfill(2)
        print('Registr value (dec)', self.register)
        print('Regist value (hex): ', register_hex)
        to_lrc_calc = '0103'+str(register_hex)+'0002'
        print('For lrc calc ', to_lrc_calc)
        lrc = self.calculate_lrc(to_lrc_calc)
        print('lrc: ', lrc)
        action = str(to_lrc_calc)+str(lrc)
        print('Action ', action)
        action_bytes = bytes(':'+str(action)+'\r\n', 'utf-8')
        print('Action in bytes ', action_bytes)
        return action

    def read_input_float32(self):
        register_hex = hex(int(self.register))[2:].zfill(2)
        print('Registr value (dec)', self.register)
        print('Regist value (hex): ', register_hex)
        to_lrc_calc = '0104'+str(register_hex)+'0002'
        print('For lrc calc ', to_lrc_calc)
        lrc = self.calculate_lrc(to_lrc_calc)
        print('lrc: ', lrc)
        action = str(to_lrc_calc)+str(lrc)
        print('Action ', action)
        action_bytes = bytes(':'+str(action)+'\r\n', 'utf-8')
        print('Action in bytes ', action_bytes)
        return action

    def execute(self):

        if self.type_value == 'uint16':
            result = self.read_uint16()
        elif self.type_value == 'uint32':
            result = self.read_uint32()
        elif self.type_value == 'int16':
            result = self.read_uint16()
        elif self.type_value == 'multi':
            result = self.read_multi()
        elif self.type_value == 'input16':
            result = self.read_input16()
        elif self.type_value == 'input32':
            result = self.read_input32()
        elif self.type_value == 'string':
            result = self.read_string()
        elif self.type_value == 'float32':
            result = self.read_float32()
        elif self.type_value == 'input_float32':
            result = self.read_input_float32()
        else:
            result = 'Нет такого типа регистра'
        return result


class Translate:
    def __init__(self, answer, register):
        self.answer = answer
        self.register = register

    def translate_uint32(self):
        hex_str = self.answer[7:15]
        # hex_str = short_answer.replace(' ', '')
        print('Короткий ответ :', hex_str)
    # Проверяем, что длина строки кратна 4
        if len(hex_str) % 8 != 0:
            raise ValueError("Длина строки должна быть кратна 8")

    # Разбиваем строку на 16-битные слова
        words = [hex_str[i:i+8] for i in range(0, len(hex_str), 8)]

    # Переставляем байты в каждом слове
        swapped_words = [word[4:] + word[:4] for word in words]
        hex_data_str = ' '.join(swapped_words)
        hex_data = bytes.fromhex(hex_data_str)
    # Разделяем байты пробелами для читаемости
        hex_string = ' '.join(f'{byte:02X}' for byte in hex_data)

        result = int(hex_string.replace(' ', ''), 16)
    # Объединяем результат
        return result

    def translate_uint16(self):
        short_answer = self.answer[7:11]
        hex_str = short_answer.replace(' ', '')
    # Проверяем, что длина строки кратна 4
        if len(hex_str) % 4 != 0:
            raise ValueError("Длина строки должна быть кратна 8")

        result = int(hex_str.replace(' ', ''), 16)
    # Объединяем результат
        return result

    def translate_int16(self):
        short_answer = self.answer[7:11]
        data = short_answer.replace(' ', '')
        data_bytes = bytes.fromhex(data)  # 256 в десятичной системе
        decimal_value = struct.unpack('>h', data_bytes)[0]
        return decimal_value

    def translate_string(self):
        data = self.answer[11:-6]
        print('Строка данных ', data)
        result = bytes.fromhex(data).decode('utf-8')
        return result

    def translate_float32(self):
        shot_answer = self.answer[7:15]
        print('Короткий ответ ', shot_answer)
        swapped_words = shot_answer[4:] + shot_answer[:4]
        print('Переставленные слова ', swapped_words)
        # Конвертация hex в float
        float_value = struct.unpack('!f', bytes.fromhex(swapped_words))[0]

        # Конвертация float в Decimal
        result = Decimal(str(float_value))

        return result

    def execute(self):
        self.type_value = type_value[str(self.register)]

        if (self.type_value == 'uint16') or (self.type_value == 'input16'):
            result = self.translate_uint16()
        elif self.type_value == 'int16':
            result = self.translate_int16()
        elif (self.type_value == 'input32') or (self.type_value == 'uint32'):
            result = self.translate_uint32()
        elif self.type_value == 'string':
            result = self.translate_string()
        elif self.type_value == 'float32' or (self.type_value == 'input_float32'):
            print('run float32 translate')
            result = self.translate_float32()
        else:
            result = 'Нет такого типа регистра'
        return result


class Com_ports:
    def __init__(self):
        pass

    @staticmethod
    def com_ports_list():
        ports = serial.tools.list_ports.comports()
        ports_list = list()
        for port in ports:
            ports_list.append(port.name)
        print('Список обнаруженных портов: ', ports_list)

        if len(ports_list) == 0:
            raise ValueError("No com port connections")
        return ports_list

    def connection(self):
        self.ports = self.com_ports_list()
        port_to_connect = self.ports[0]
        self.ser = serial.Serial(port=port_to_connect,
                                 baudrate=115200, timeout=1)
        return self.ports

    def connection_to_port(self, port):
        self.ser = serial.Serial(port=port,
                                 baudrate=115200, timeout=1)
        return

    def mac_adress_list(self):
        print('Запуск метода mac_adress_list')

        if self.ser.is_open:
            print("Порт открыт")
        self.ser.setRTS(True)  # переводим RTS в логическую 1
        self.ser.setDTR(False)  # переводим DTR  в логический 0

    # Отправляем команду AT+SCAN
        self.ser.write(b'AT+SCAN\r\n')

    # Ждем ответа (можно настроить время ожидания)
        time.sleep(5)

    # Читаем ответ
        response = self.ser.read(self.ser.in_waiting)
        answers = response.decode('utf-8').split('DEV')
        print(answers)

        mac_adresses = []

        for answer in answers:
            if 'NEO' in answer:
                # print(answer)
                if len(answer) > 6:
                    start = answer.find('=') + 1
                    end = answer.find(',')
                    mac_adress = answer[start:end]
                else:
                    mac_adress = "0"

                if mac_adress not in mac_adresses:
                    mac_adresses.append(mac_adress)

                print('Список мак адресов: ', mac_adresses)
            else:
                ['Приборы не обнаружены']
        if len(mac_adresses) == 0:
            mac_adresses = ['Приборы не обнаружены']
            # print('Приборы НЕО не найдены')
            # sys.exit(0)

        # mac_port_seq = {}
        # i = 0
        # for port in self.ports:
        #     mac_port_seq.update({mac_adresses[i]: port})
        #     i += 1
        # print('Словарь: ', mac_port_seq)
        self.ser.close()
        return mac_adresses

    def device_connection(self, com_port, mac_adress):
        print(
            f"Подключаемся к прибору с mac адресом {mac_adress} по порту {com_port}")
        self.ser_device = serial.Serial(port=com_port,
                                        baudrate=115200, timeout=1)
        answers = str()
        while 'CONNECTED' not in str(answers):
            self.ser_device.write(b'AT+DISC\r\n')
            time.sleep(5)
            action = ('AT+CONN' + mac_adress + '\r\n').encode('utf-8')
            print(action)
            self.ser_device.write(action)

        # Ждем ответа (можно настроить время ожидания)
            time.sleep(7)

        # Читаем ответ
            response = self.ser_device.read(self.ser_device.in_waiting)
            answers = response.decode('utf-8')
            print(answers)
            self.ser_device.setRTS(False)  # переводим RTS в логический 0
            self.ser_device.setDTR(False)  # переводим DTR  в логический 0
        return

    def device_write(self, action):
        self.ser_device.write(action)
        return

    def device_read(self):
        response = self.ser_device.read(self.ser_device.in_waiting)
        return response

    def set_rts(self, state):
        self.ser_device.setRTS(state)

    def set_dtr(self, state):
        self.ser_device.setDTR(state)

    def close_connection(self):
        self.ser.close()
        return


# while True:
#     what_type = input('Write(1) or Read(2) or Translate(3) ')
# #     # type = input('Insert register type ')
#     if what_type == '1':
#         register = input('Insert register value ')

#         value = input('Insert value ')
#         request_write = Request_write(register)
#         print(request_write.execute(value, 1))
#     elif what_type == '2':
#         register = input('Insert register value ')
#         request_read = Request_read(register)
#         print(request_read.execute())
#     elif what_type == '3':
#         value = input('Insert value ')
#         register = input('Insert register value ')
#         translated_answer = Translate(value, register)
#         print(translated_answer.execute())
