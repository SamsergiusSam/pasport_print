apiInfos = [
    {'type': 'G4', 'serial_number': 10240080, 'el_sealing': 12345678},
    {'type': 'G4', 'serial_number': 10240081, 'el_sealing': 87654321},
    {'type': 'G6', 'serial_number': 10240082, 'el_sealing': 87654322},
    {'type': 'G25', 'serial_number': 10240083, 'el_sealing': 87654323},
    {'type': 'G16', 'serial_number': 10240084, 'el_sealing': 87654324},
    {'type': 'G25', 'serial_number': 10240085, 'el_sealing': 87654325},
    {'type': 'G10', 'serial_number': 10240086, 'el_sealing': 87654326},
    {'type': 'G25', 'serial_number': 10240087, 'el_sealing': 87654327},
    {'type': 'G25', 'serial_number': 10240088, 'el_sealing': 87654328},
]

techData = {
    'G4': {'A': 214, 'B': 304, 'C': 504},
    'G6': {'A': 216, 'B': 306, 'C': 506},
    'G10': {'A': 210, 'B': 300, 'C': 500},
    'G16': {'A': 226, 'B': 326, 'C': 526},
    'G25': {'A': 225, 'B': 325, 'C': 525}
}

infos = list()
for apiInfo in apiInfos:
    meterType = apiInfo['type']
    completeInfo = {**apiInfo, **techData[meterType]}
    infos.append(completeInfo)
print(infos)
