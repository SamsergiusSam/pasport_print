from docxtpl import DocxTemplate
# from docxcompose.composer import Composer
from docx import Document as Document_compose
# from pypdf import PdfWriter
from docx2pdf import convert
import fitz
import time
import win32print
import win32api
import requests

from tech_data import techData

startNumber = int(input('Input the start serial number '))
finishNumber = int(input('Input the last serial number '))
startTime = time.time()
# загружаем шаблон паспорта
doc = DocxTemplate(
    r'C:\Users\мвидео\python\pasport_print\passport_template.docx')

##############################################################################
# данные для внесения в паспорт
##############################################################################

# данные о типе, серийном номере и электронной пломбе. будем получать по api с сервера


def api_requst(serialNumbers):

    apiInfos = list()
    for serialNumber in serialNumbers:
        url = 'https://neo-manager.ru/passport/meters/' + str(serialNumber)
        headers = {
            'Api-Key': 'IYYrqffqeWF9esyMvTrF586OqqywN2Dd3xk6L8vUjtUZDN46ocBM5K5TXrG4Cd58'}
        response = requests.get(url, headers=headers)
        api_info = response.json()
        apiInfos.append(api_info)

    return apiInfos


# startNumber = 10240035
# finishNumber = 10240041
numbers = list()
for i in range(startNumber, finishNumber+1):
    numbers.append(i)
    apiInfos = api_requst(numbers)


# формируем обощенные данные для заполнения паспорта
infos = list()
for apiInfo in apiInfos:
    meterType = str(apiInfo['meterSize'])
    completeInfo = {**apiInfo, **techData[meterType]}
    infos.append(completeInfo)
print('Information to print passports are created.\n')
print('Total number of passports to print', len(infos))

# создаем новый документ для слияния
newDoc = Document_compose()
newDoc.save(r'C:\Users\мвидео\python\pasport_print\final_to_print.docx')

# создаем новый документ для записи собранного pdf файла
result = fitz.open()

for info in infos:
    doc.render(info)
    doc.save(r'C:\Users\мвидео\python\pasport_print\to_add.docx')
    convert(r"C:\Users\мвидео\python\pasport_print\to_add.docx",
            r'C:\Users\мвидео\python\pasport_print\to_add.pdf')

    with fitz.open(r'C:\Users\мвидео\python\pasport_print\to_add.pdf') as mfile:
        result.insert_pdf(mfile)
result.save(r'C:\Users\мвидео\python\pasport_print\result.pdf')

print('passport creation completed\n')
print((time.time()-startTime))

####################################################################################
# печать сформированного документа
