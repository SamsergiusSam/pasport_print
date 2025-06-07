from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from docxtpl import DocxTemplate
from docx import Document as Document_compose
from docx2pdf import convert
import fitz
import time
import win32print
import win32api
import requests
from tech_data import techData
import pythoncom
import psycopg2
from sqlalchemy import BigInteger, Column, Date, DateTime, Integer, String, Text, Boolean, create_engine, insert, select, MetaData, inspect, text, Table
from sqlalchemy.schema import MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from json.decoder import JSONDecodeError
from datetime import date
import base64
import io


import pythoncom


from psi_creation import main as psiCreation
from app_init import engine, conn, si_table


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://samsam:Cfv240185@pm-production-samsergius.db-msk0.amvera.tech/pm_production"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '1234567890'
db = SQLAlchemy(app)


class Si_list(db.Model):
    __tablename__ = db.metadata.tables['si_table']


@app.route("/")
def home_page():
    return render_template("home.html")


@app.route("/pasport_print_page")
def pasport_print_page():
    return render_template("pasport_print.html")


@app.route("/pasport_print", methods=["POST", "GET"])
def pasport_print():
    pythoncom.CoInitialize()
    if request.method == "POST":
        start_number = int(request.form["start_number"])
        finish_number = int(request.form["finish_number"])
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
                url = 'https://neo-manager.ru/passport/meters/' + \
                    str(serialNumber)
                headers = {
                    'Api-Key': 'IYYrqffqeWF9esyMvTrF586OqqywN2Dd3xk6L8vUjtUZDN46ocBM5K5TXrG4Cd58'}
                response = requests.get(url, headers=headers)
                api_info = response.json()
                apiInfos.append(api_info)

            return apiInfos

        numbers = list()
        for i in range(start_number, finish_number+1):
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
        result.save(
            r'C:\Users\мвидео\python\pasport_print\static\pdf\result.pdf')

        print('passport creation completed\n')
        print((time.time()-startTime))
        psiCreation(start_number, finish_number)

        return redirect("/pasport_preview")

    else:
        return render_template('pasport_print.html')


@app.route("/pasport_preview")
def passport_prerview():
    return render_template("pasport_preview.html")


@app.route("/si_creation_page")
def si_creation_page():
    return render_template("si_creation.html")


@app.route("/si_creation", methods=["POST", "GET"])
def si_creation():

    if request.method == "POST":
        name = request.form["name"]
        type_name = request.form["type_name"]
        serial_number = request.form["serial_number"]
        inventory_number = request.form["inventory_number"]
        production_year = request.form["production_year"]
        produser = request.form["produser"]
        verification_link = request.form["verification_link"]
        next_verification_date = request.form["next_verification_date"]
        group = request.form["group"]

        inputs = {
            'name': name,
            'type_name': type_name,
            "serial_number": serial_number,
            "produser": produser,
            "inventory_number": inventory_number,
            "production_year": production_year,
            "verification_link": verification_link,
            "next_verification_date": next_verification_date,
            "group": group,

        }
        # print(inputs)
        metadata = MetaData()

        users_table = Table(
            'si_table', metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('name', String, unique=False, nullable=False),
            Column('type_name', String, unique=False, nullable=False),
            Column('serial_number', String, unique=False, nullable=True),
            Column('produser', String, unique=False, nullable=True),
            Column('inventory_number', String, unique=True, nullable=False),
            Column('production_year', String,
                   unique=False, nullable=True),
            Column('verification_link', String, unique=False, nullable=True),
            Column('next_verification_date', Date,
                   unique=False, nullable=True),
            Column('group', String, unique=False, nullable=True),
            Column('status', Boolean, default='True')
        )
        metadata.create_all(engine)

        cursor = conn.cursor()
        keys = '", "'.join(inputs.keys())
        values = ', '.join(['%s'] * len(inputs))
        action = f'INSERT INTO si_table ("{keys}") VALUES ({values})'
        # print(action)
        input_values = list(inputs.values())
        # print(input_values)

        try:
            cursor.execute(action, input_values)
            conn.commit()

        except psycopg2.Error as e:
            print(f"Ошибка: {e}")

            conn.rollback()
        # finally:
        #     cursor.close()
        return redirect(url_for("si_view_page"))
    else:
        return render_template("si_creation.html")


@app.route("/si_view_page", methods=["GET"])
def si_view_page():
    # conn = psycopg2.connect(dbname="pm_production", host="pm-production-samsergius.db-msk0.amvera.tech",
    #                         user="samsam", password="Cfv240185", port="5432")
    # cursor = conn.cursor()
    # action = 'SELECT * FROM si_table'
    # cursor.execute(action)
    # results = cursor.fetchall()
    # print(results)
    results = si_table.query.all()
    return render_template("si_list.html", results=results)


@app.route("/si/<int:si_id>")
def si_individual(si_id):
    cursor = conn.cursor()
    action = 'SELECT * FROM si_table WHERE (id='+str(si_id)+')'
    cursor.execute(action)
    result = cursor.fetchall()
    print(result)
    return (result)


@app.route("/si_verification_list")
def si_verification_list():
    year = date.today().year
    cursor = conn.cursor()
    action = 'SELECT * FROM si_table WHERE EXTRACT(YEAR FROM next_verification_date) = '+str(
        year)
    cursor.execute(action)
    results = cursor.fetchall()
    print(year)
    print(results)
    # return redirect("/")
    return render_template("si_verification_list.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)
