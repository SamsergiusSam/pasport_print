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

engine = create_engine(
    "postgresql+psycopg2://samsam:Cfv240185@pm-production-samsergius.db-msk0.amvera.tech/pm_production", echo=False)


def doc_creation(info):
    pythoncom.CoInitialize()
    # загружаем шаблон паспорта
    doc = DocxTemplate(
        r'D:\python_projects\python\pasport_print\psi_template.docx')
    # создаем новый документ для слияния
    newDoc = Document_compose()
    newDoc.save(r'D:\python_projects\python\pasport_print\psi_to_print.docx')

    # создаем новый документ для записи собранного pdf файла
    result = fitz.open()
    doc.render(info)
    doc.save(r'D:\python_projects\python\pasport_print\psi_to_add.docx')
    convert(r"D:\python_projects\python\pasport_print\psi_to_add.docx",
            r'D:\python_projects\python\pasport_print\psi_to_add.pdf')

    with fitz.open(r'D:\python_projects\python\pasport_print\psi_to_add.pdf') as mfile:
        result.insert_pdf(mfile)
    result.save(
        r'D:\python_projects\python\pasport_print\ПСИ\ПСИ №'+str(info['psiNum'])+'_'+str(info['meterNum'])+'.pdf')
    return ()

# загрузка данных в базу данных


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


def psi_from_db(serialNumbers):
    conn = psycopg2.connect(dbname="pm_production", host="pm-production-samsergius.db-msk0.amvera.tech",
                            user="samsam", password="Cfv240185", port="5432")
    cursor = conn.cursor()
    for serialNumber in serialNumbers:
        try:
            action = str(
                'SELECT "psiNumber","meterNum", "psiPerson","psiDate" FROM psi WHERE "meterNum"='+str(serialNumber))
            cursor.execute(action)
            result = cursor.fetchall()
            conn.commit()
            print(result)
            # print(result[0][0])
            # print(type(result))
            if len(result) > 0:
                data = result[0][3].strftime('%Y-%m-%d')
                to_doc = {'psiNum': result[0][0],
                          'meterNum': result[0][1],
                          'psiPerson': result[0][2],
                          'psiDate': result[0][3]
                          }
                print(to_doc)
                doc_creation(to_doc)
            else:
                pass
        except psycopg2.errors:
            pass


def main(startNumber, finishNumber):
    metadata = MetaData()

    users_table = Table(
        'psi', metadata,
        Column('psiNumber', Integer, primary_key=True, autoincrement=True),
        Column('id', Integer, nullable=False),
        Column('imei', BigInteger, unique=True, nullable=False),
        Column('meterNum', BigInteger, unique=True, nullable=False),
        Column('meterSize', Integer, unique=False, nullable=False),
        Column('plombNum', BigInteger, unique=False, nullable=True),
        Column('psiPerson', String(100), unique=False, nullable=False),
        Column('psiDate', Date, unique=False, nullable=False),
    )

    metadata.create_all(engine)

    numbers = list()
    for i in range(startNumber, finishNumber+1):
        numbers.append(i)

    api_requst(numbers, "Усков С.В.")
    psi_from_db(numbers)
