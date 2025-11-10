from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime
import time
import requests
from sqlalchemy import extract
from sqlalchemy.ext.declarative import declarative_base
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd


from techData.tech_data import techData
from psi_creation_new import main as psiCreation
from app_init import si_table, app, db, User, scheduler, FlowDirect, psi
from neo_param.neo_param import neo_param
from qa.qa import qa
from production.production import production
from climat import climat_load
from send_attached_file import send_email
from functions import doc_creation, verification_actual_date, parse_number_input


scheduler.start()


@scheduler.task('cron', id='climat_load', hour='9,14', minute=22)
# @scheduler.task('interval', id='climat_load', minutes=60)
def my_scheduled_job():
    climat_load()
    print('Загрузка климатических параметров выполнена')


@scheduler.task('cron', id='verification_load', hour=14, minute=30)
def my_scheduled_job_verification():
    verification_actual_date()
    print('Обновленние данных о поверках выполнено')


app.register_blueprint(neo_param, url_prefix="/neo_param")
app.register_blueprint(qa, url_prefix="/qa")
app.register_blueprint(production, url_prefix="/production")


def role_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role not in roles:
                flash("У вас недостаточно прав для доступа к этой странице.", "danger")
                return redirect(url_for('home_page'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper


@app.context_processor
def inject_user():
    return {'current_user': current_user}


@app.route("/")
@login_required
def home_page():
    return render_template("home.html")


@app.route("/pasport_print", methods=["POST", "GET"])
@login_required
@role_required('quality', 'management')
def pasport_print():

    if request.method == "POST":
        raw_input = request.form.get('numbers_input', '').strip()

        number_list = parse_number_input(raw_input)
        print(number_list)
        print(type(number_list))

        if not number_list:
            flash("Не указано ни одного корректного номера.", "danger")
            return render_template('pasport_print.html'), 400
        startTime = time.time()

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
        for i in number_list:
            numbers.append(i)
            apiInfos = api_requst(numbers)

        # формируем обощенные данные для заполнения паспорта
        infos = list()
        for apiInfo in apiInfos:
            meterType = str(apiInfo['meterSize'])
            flow_direction = FlowDirect.query.filter_by(
                serial_number=apiInfo["meterNum"]).first()

            if flow_direction.flow_direction == 1:
                flow_direction_id = {"flowDirection": "Л"}
            else:
                flow_direction_id = {"flowDirection": "П"}

            if apiInfo["atmPresType"] == 1:
                atm_press = {"atmPress": "P"}
            else:
                atm_press = {"atmPress": "*"}

            meter_version = {"meterVersion": flow_direction.meterVersion}
            completeInfo = {**apiInfo, **
                            techData[meterType], **flow_direction_id, **atm_press, **meter_version}
            infos.append(completeInfo)
        print(f"Данные для печати паспорта {infos}")
        print('Information to print passports are created.\n')
        print('Total number of passports to print', len(infos))

        doc_creation(infos)

        print('passport creation completed\n')
        print((time.time()-startTime))
        psiCreation(number_list)

        return redirect("/pasport_preview")

    else:
        return render_template('pasport_print.html')


@app.route("/pasport_preview")
@login_required
@role_required('quality', 'management')
def passport_prerview():
    return render_template("pasport_preview.html")


@app.route("/si_creation", methods=["POST", "GET"])
@login_required
@role_required('metrology', 'management')
def si_creation():

    def inventory_number_creation():
        current_year = str(datetime.now().year)[2:]
        counter = str(si_table.query.count()+1).zfill(2)
        inventory_number = f'ПМ-{counter}-{current_year}'
        return inventory_number

    if request.method == "POST":
        add = si_table(
            name=request.form["name"],
            type_name=request.form["type_name"],
            serial_number=request.form["serial_number"],
            inventory_number=inventory_number_creation(),
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
@role_required('metrology', 'management')
def si_view_page():
    results = si_table.query.all()
    return render_template("si_list.html", results=results)


@app.route("/si/<int:si_id>")
@login_required
@role_required('metrology', 'management')
def si_individual(si_id):

    result = si_table.query.filter_by(id=si_id).first()
    return (result.name)


@app.route("/si_verification_list")
@login_required
@role_required('metrology', 'management')
def si_verification_list():
    year = date.today().year
    results = si_table.query.filter(
        extract('year', si_table.next_verification_date) == year).all()
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

        login_user(user, remember=True)  # или permanent=True
        session.permanent = True  # Это активирует PERMANENT_SESSION_LIFETIME
        return redirect('/')

    return render_template('login_page.html')


@app.route('/logout')
def logout():
    logout_user()  # Завершает сессию пользователя
    flash("Вы успешно вышли из системы", "info")
    return redirect(url_for('login'))  # Перенаправление на страницу входа


@app.route('/production')
@role_required('production', 'management')
def production_page():
    return render_template('production.html')


@app.route('/for_verification')
@role_required('production', 'quality', 'management')
def for_verification_list():
    unverify_meters = psi.query.filter_by(verification_done=False).all()
    print(unverify_meters)
    return render_template("for_verification.html", unverify_meters=unverify_meters)


@app.route('/for_verification/send', methods=["GET", "POST"])
@role_required('production', 'quality', 'management')
def for_verification_send():
    serial_number_list = []
    meter_size_type_list = []
    atm_pressure_type_list = []
    verification_date_list = []

    total_number_str = request.form.get('total_number', '').strip()
    print(total_number_str)
    if not total_number_str.isdigit():
        return "Ошибка: не указано количество приборов", 400
    total_number_of_meters = int(total_number_str)

    number_to_send = 0
    for i in range(1, total_number_of_meters+1):
        to_verification_status = request.form.get(f'checkbox_{i}')
        if to_verification_status == 'on':
            number_to_send = number_to_send + 1
            serial_number = request.form.get(f'meterNum_{i}')
            meter_size = request.form.get(f'meterSize_{i}')
            meter_size_type = techData[str(meter_size)]['type']
            atm_pressure_type = request.form.get(f'atmPresTypePasport_{i}')
            verification_date = str(request.form.get(f'date_{i}'))
            print(verification_date)
            serial_number_list.append(serial_number)
            meter_size_type_list.append(meter_size_type)
            atm_pressure_type_list.append(atm_pressure_type)
            verification_date_list.append(verification_date)
    total_data_dict = dict()
    total_data_dict = {"Date": verification_date_list, "Serial_number": serial_number_list,
                       "Size": meter_size_type_list, "Version": atm_pressure_type_list}
    df = pd.DataFrame(total_data_dict)
    now = datetime.now().date()
    name = f'for_verification_{now}_{number_to_send}'
    path = f'files_for_verification/{name}.xlsx'
    df.to_excel(path, index=False, engine='openpyxl')

    send_email(path)

    for number in serial_number_list:
        meter = psi.query.filter_by(meterNum=number).first()
        meter.verification_done = True
        meter.verification_date = verification_date
        db.session.commit()

    return "File has been sent"


if __name__ == "__main__":
    app.run(debug=True)
