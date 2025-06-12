from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required

from forms import Inc_Insp_Req
from app_init import inc_insp_list, db

qa = Blueprint('qa', __name__, url_prefix='/qa',
               static_folder='static', template_folder='templates')


@qa.route('/')
@login_required
def qa_main_page():
    return render_template('qa/quality.html')


@qa.route('/inc_insp_create')
@login_required
def inc_insp_create():
    form = Inc_Insp_Req()
    return render_template('qa/inc_insp_create.html', form=form)


@qa.route('/inc_insp_add', methods=['POST'])
@login_required
def inc_insp_add():
    form = Inc_Insp_Req()
    form_data = {field.name: getattr(form, field.name).data
                 for field in form if field.name != 'csrf_token'}
    add = inc_insp_list(**form_data)
    db.session.add(add)
    db.session.commit()
    return redirect(url_for('.inc_insp_total'))


@qa.route('/inc_insp_total', methods=['POST', 'GET'])
@login_required
def inc_insp_total():
    # for_product = request.form.get('for_product')
    filtered_data = inc_insp_list.query.all()
    # return filtered_data
    return render_template('/qa/inc_insp_total.html', results=filtered_data)
