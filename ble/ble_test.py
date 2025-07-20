import asyncio
from bleak import BleakScanner, BleakClient

# Функция для сканирования устройств


async def scan_devices():
    print("Сканирование BLE устройств...")
    devices = await BleakScanner.discover()
    for d in devices:
        print(f"Найдено устройство: {d})")

# Функция для подключения к устройству


async def connect_to_device(address):
    async with BleakClient(address) as client:
        if client.is_connected:
            print(f"Подключено к устройству {address}")
            # Здесь можно добавить работу с характеристиками устройства
            await client.disconnect()
        else:
            print("Подключение не удалось")

# Запуск сканирования
asyncio.run(scan_devices())

# from PyQt5.QBluetooth import *
# devices = bluetooth.discover_devices(duration=5, lookup_names=True)
# for addr, name in devices:
#   print(f"Found {name} - {addr}")
