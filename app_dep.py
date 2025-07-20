from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_required, login_user, logout_user
from docxtpl import DocxTemplate
from docx import Document as Document_compose
from docx2pdf import convert
import fitz
import time

import requests
from tech_data import techData
# import pythoncom

from sqlalchemy import BigInteger, Column, Date, DateTime, Integer, String, Text, Boolean, create_engine, insert, select, MetaData, inspect, text, Table, extract
from sqlalchemy.schema import MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from json.decoder import JSONDecodeError
from datetime import date

from werkzeug.security import generate_password_hash, check_password_hash


from psi_creation_dep import main as psiCreation
from app_init import engine, conn, si_table, app, db, User, login_manager
from neo_param.neo_param import neo_param
from qa.qa import qa

app.register_blueprint(neo_param, url_prefix="/neo_param")
app.register_blueprint(qa, url_prefix="/qa")


@app.route("/")
@login_required
def home_page():
    return render_template("home.html")


# @app.route("/pasport_print_page")
# @login_required
# def pasport_print_page():
#     return render_template("pasport_print.html")


@app.route("/pasport_print", methods=["POST", "GET"])
@login_required
def pasport_print():
    # pythoncom.CoInitialize()
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
@login_required
def passport_prerview():
    return render_template("pasport_preview.html")


# @app.route("/si_creation_page")
# @login_required
# def si_creation_page():
#     return render_template("si_creation.html")


@app.route("/si_creation", methods=["POST", "GET"])
@login_required
def si_creation():

    if request.method == "POST":
        add = si_table(
            name=request.form["name"],
            type_name=request.form["type_name"],
            serial_number=request.form["serial_number"],
            inventory_number=request.form["inventory_number"],
            production_year=request.form["production_year"],
            produser=request.form["produser"],
            verification_link=request.form["verification_link"],
            next_verification_date=request.form["next_verification_date"],
            group=request.form["group"]
        )
        db.session.add(add)
        db.session.commit()

        return redirect(url_for("si_view_page"))
    else:
        return render_template("si_creation.html")


@app.route("/si_view_page", methods=["GET"])
@login_required
def si_view_page():

    results = si_table.query.all()
    return render_template("si_list.html", results=results)


@app.route("/si/<int:si_id>")
@login_required
def si_individual(si_id):

    result = si_table.query.filter_by(id=si_id).first()
    return (result.name)


@app.route("/si_verification_list")
@login_required
def si_verification_list():
    year = date.today().year
    results = si_table.query.filter(
        extract('year', si_table.next_verification_date) == year).all()
    return render_template("si_verification_list.html", results=results)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, str(password)):
            flash('Please check your login details and try again.')
            return redirect(url_for('login_page'))

        login_user(user)
        return redirect('/')

    return render_template('login_page.html')


@app.route('/production')
def production_page():
    return render_template('production.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8080')
