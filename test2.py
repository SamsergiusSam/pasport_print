def translate_string(answer):
    data = answer[11:]
    data_short = data[:-2]
    print('Строка данных ', data_short)
    result = bytes.fromhex(data_short).decode('ascii', errors="replace")
    return result


print(translate_string(':01700013003139342E38372E3134372E3139313A38353030A7'))
