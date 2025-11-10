import subprocess
from docxtpl import DocxTemplate
import fitz
import requests
from datetime import datetime

from app_init import app, db, passport_version, psi


def doc_creation(input_information):
    result = fitz.open()
    template_name = db.session.query(passport_version).filter(
        passport_version.actual_template == True).first()
    for info in input_information:
        full_tempalate_path = f'D:\python_projects\python\pasport_print\{template_name.file_name}'
        doc = DocxTemplate(full_tempalate_path)

        doc.render(info)
        doc.save(r'D:\python_projects\python\pasport_print\to_add.docx')

        path_of = r'C:\Program Files\LibreOffice\program\soffice.exe'
        subprocess.run([
            path_of,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", "./",
            "to_add.docx"
        ])

        with fitz.open(r'D:\python_projects\python\pasport_print\to_add.pdf') as mfile:
            result.insert_pdf(mfile)
    result.save(
        r'D:\python_projects\python\pasport_print\static\pdf\result.pdf')

    return


def add_image_watermark(input_pdf, output_pdf, image_path):
    doc = fitz.open(input_pdf)

    # Загружаем изображение
    img = fitz.open(image_path)
    img_bytes = img.get_page_pict(0).image_bytes

    for page_num in range(len(doc)):
        page = doc[page_num]
        # Определяем позицию (например, центр)
        rect = fitz.Rect(100, 100, 500, 500)  # x0,y0,x1,y1
        # Добавляем изображение
        page.insert_image(rect, stream=img_bytes)

    doc.save(output_pdf)
    doc.close()


def verification_actual_date():
    serial_number_list = list()
    all_data = db.session.query(psi).order_by(psi.meterNum).all()
    for data in all_data:
        serial_number_list.append(data.meterNum)

    for serial_number in serial_number_list:

        url = f'https://fgis.gost.ru/fundmetrology/eapi/vri?rows=100&mit_number=92260-24&mi_number={serial_number}'
        print(url)
        # time.sleep(2)
        data = requests.get(url)
        end_data_1 = data.json()
        if end_data_1.get('result').get('count') == 0:
            print('Нет данных')
            pass
        else:
            actual_date = end_data_1.get('result').get(
                'items')[0].get("verification_date")
            actual_date = datetime.strptime(actual_date, "%d.%m.%Y").date()
            print(actual_date)

        first_verification_date = db.session.query(psi).filter(
            psi.meterNum == serial_number).first().verification_date
        actual_verification_date = db.session.query(psi).filter(
            psi.meterNum == serial_number).first().verification_date_actual
        if first_verification_date == None:
            print("Прибор не поверялся")
            pass
        else:
            if actual_verification_date == actual_date:
                print("Дата поверки не изменилась")
                pass
            else:
                db.session.query(psi).filter(psi.meterNum == serial_number).update(
                    {psi.verification_date_actual: actual_date})
                number_of_verifications = db.session.query(psi).filter(
                    psi.meterNum == serial_number).first().number_of_verifications
                if number_of_verifications == None:
                    number_of_verifications = 0
                number_of_verifications += 1
                db.session.query(psi).filter(psi.meterNum == serial_number).update(
                    {psi.number_of_verifications: number_of_verifications})
                db.session.commit()
                print(
                    f'дата поерки изменилась {actual_date}. Количество поверок {number_of_verifications}')

    return


def parse_number_input(input_str):
    """
    Парсит строку с номерами. Поддерживает:
    - Отдельные: 1,2,3
    - Диапазоны: 5-10
    - Комбинации: 1,3-5,7,9-12
    Возвращает отсортированный список уникальных номеров.
    """
    if not input_str or not input_str.strip():
        return []

    numbers = set()
    parts = input_str.strip().split(',')

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Проверка формата диапазона: например, "3-7"
        if '-' in part:
            range_parts = part.split('-')
            if len(range_parts) != 2:
                raise ValueError(f"Неверный формат диапазона: {part}")

            try:
                start = int(range_parts[0].strip())
                end = int(range_parts[1].strip())
                if start >= end:
                    raise ValueError(
                        f"Некорректный диапазон: {start}-{end}. Начало должно быть меньше конца.")
                numbers.update(range(start, end + 1))
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError(f"Ожидались числа, получено: {part}")
                else:
                    raise

        else:
            # Одиночное число
            try:
                num = int(part)
                numbers.add(num)
            except ValueError:
                raise ValueError(
                    f"Невалидное значение: {part}. Должно быть число или диапазон.")

    return sorted(numbers)


if __name__ == '__main__':
    with app.app_context():
        verification_actual_date()
