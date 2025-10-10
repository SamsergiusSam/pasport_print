<<<<<<< HEAD
from datetime import date, datetime
import psycopg2
from sqlalchemy import BigInteger, Column, Date, DateTime, Integer, String, Text, create_engine, insert, select, MetaData, inspect, text, Table
from sqlalchemy.schema import MetaData
import pandas as pd
import requests
from json.decoder import JSONDecodeError
from docxtpl import DocxTemplate

from docx import Document as Document_compose

from docx2pdf import convert
import fitz
import time
import requests
import pythoncom


def api_requst(serialNumbers, psi_person):
    conn = psycopg2.connect(dbname="pm_production", host="pm-production-samsergius.db-msk0.amvera.tech",
                            user="samsam", password="Cfv240185", port="5432")
    cursor = conn.cursor()
    # apiInfos = list()
    for serialNumber in serialNumbers:
        try:
            api_info = dict()
            url = 'https://neo-manager.ru/passport/meters/' + str(serialNumber)
            headers = {
                'Api-Key': 'IYYrqffqeWF9esyMvTrF586OqqywN2Dd3xk6L8vUjtUZDN46ocBM5K5TXrG4Cd58'}
            response = requests.get(url, headers=headers)
            api_info = response.json()
            print(f"Статус контроля давления {api_info['atmPresType']}")
            if api_info['atmPresType'] == 1:
                atmPressPasport = "P"
            else:
                atmPressPasport = "*"

            api_info.update({'psiPerson': psi_person,
                            'psiDate': date.today(),
                             'atmPresTypePasport': atmPressPasport
                             },
                            )
            try:
                cursor.execute(
                    'INSERT INTO psi ("id", "imei", "meterNum", "meterSize", "plombNum", "psiPerson", "psiDate", "atmPresType", "atmPresTypePasport") VALUES (%(id)s, %(imei)s, %(meterNum)s,%(meterSize)s, %(plombNum)s, %(psiPerson)s, %(psiDate)s, %(atmPresType)s, %(atmPresTypePasport)s) ON CONFLICT DO NOTHING',
                    api_info
                )
                conn.commit()

            except psycopg2.errors:
                pass
            print(api_info)
        except JSONDecodeError:
            pass
        print(api_info)

    return ()


if __name__ == "__main__":
    api_requst([10250089], "Усков С.В.")
=======
from werkzeug.security import generate_password_hash
result = generate_password_hash('12345')
print(result)
>>>>>>> 50ce6fe9a97951b885ed68516bcc6a004d8a66b7
