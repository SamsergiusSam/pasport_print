from datetime import date

import requests
from json.decoder import JSONDecodeError
from docxtpl import DocxTemplate

from docx import Document as Document_compose

# from docx2pdf import convert
import fitz
import requests
# import pythoncom
import subprocess


from app_init import app, db, psi, path_of


def doc_creation(info):
    # pythoncom.CoInitialize()
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
    # convert(r"D:\python_projects\python\pasport_print\psi_to_add.docx",
    #         r'D:\python_projects\python\pasport_print\psi_to_add.pdf')

    subprocess.run([
        path_of,
        "--headless",
        "--convert-to", "pdf",
        "--outdir", "./",
        "to_add.docx"
    ])

    with fitz.open(r'D:\python_projects\python\pasport_print\psi_to_add.pdf') as mfile:
        result.insert_pdf(mfile)
    result.save(
        r'D:\python_projects\python\pasport_print\ПСИ\ПСИ №'+str(info['psiNum'])+'_'+str(info['meterNum'])+'.pdf')
    return ()


# загрузка данных в базу данных
def api_requst(serialNumbers, psi_person):

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
                             'atmPresType': api_info['atmPresType'],
                             'atmPresTypePasport': atmPressPasport,
                             'verification_done': False
                             },
                            )

            exists_imei = db.session.query(db.session.query(psi).filter_by(
                imei=api_info['imei']).exists()).scalar()
            exists_meter_number = db.session.query(db.session.query(psi).filter_by(
                meterNum=api_info['meterNum']).exists()).scalar()

            if not exists_imei:

                add = psi(**api_info)
                db.session.add(add)
                db.session.commit()

            else:
                print(f"Данные по {api_info['imei']} в базе есть")
                pass

        except JSONDecodeError:
            pass
        print(api_info)

    return ()


def psi_from_db(serialNumbers):

    for serialNumber in serialNumbers:

        data_to_pasport = psi.query.filter(
            psi.meterNum == serialNumber).first()

        date = data_to_pasport.psiDate.strftime('%Y-%m-%d')
        to_doc = {'psiNum': data_to_pasport.psiNumber,
                  'meterNum': data_to_pasport.meterNum,
                  'psiPerson': data_to_pasport.psiPerson,
                  'psiDate': date
                  }

        doc_creation(to_doc)


def main(serial_numbers):

    # numbers = list()
    # for i in serial_numbers:
    #     numbers.append(i)

    api_requst(serial_numbers, "Усков С.В.")
    psi_from_db(serial_numbers)


if __name__ == '__main__':
    with app.app_context():
        startNumber = int(input("Start number: "))
        finishNumber = int(input("Finish number: "))
        numbers = list()
        for i in range(startNumber, finishNumber+1):
            numbers.append(i)

        api_requst(numbers, "Усков С.В.")
        psi_from_db(numbers)
