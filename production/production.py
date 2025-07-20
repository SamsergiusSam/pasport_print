from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from datetime import datetime

# from forms import climat_values
from app_init import db, Climat

production = Blueprint('production', __name__, url_prefix='/production',
                       static_folder='static', template_folder='templates')


@production.route('/climat_values', methods=["POST", "GET"])
@login_required
def climat_values():
    data = Climat.query.order_by(
        Climat.day.desc()).order_by(Climat.time.desc()).all()
    places = Climat.query.with_entities(Climat.place).distinct().all()
    return render_template('production/climat_values_list.html', forms=data, places=places)


@production.route('/climat_values/sorted', methods=['GET', 'POST'])
@login_required
def climat_values_sorted():
    places = Climat.query.with_entities(Climat.place).distinct().all()
    place = request.form.get('place')
    if not place:
        start_day = str(request.form['date_from'])
        end_day = str(request.form["date_to"])
        start_date_object = datetime.strptime(start_day, "%d.%m.%Y").date()
        end_date_object = datetime.strptime(end_day, "%d.%m.%Y").date()
        data = Climat.query.filter(Climat.day.between(start_date_object, end_date_object)).order_by(
            Climat.day.desc()).order_by(Climat.time.desc()).all()
    else:
        start_day = str(request.form['date_from'])
        end_day = str(request.form["date_to"])
        start_date_object = datetime.strptime(start_day, "%d.%m.%Y").date()
        end_date_object = datetime.strptime(end_day, "%d.%m.%Y").date()
        data = Climat.query.filter(Climat.day.between(start_date_object, end_date_object)).filter(Climat.place == place).order_by(
            Climat.day.desc()).order_by(Climat.time.desc()).all()

    return render_template('production/climat_values_list.html', forms=data, places=places)
    # print(start_day)
    # print(end_day)
    # return start_day
