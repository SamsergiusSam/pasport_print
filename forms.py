from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField


class ParamForm(FlaskForm):
    serial_number = StringField("Serial Number")
    size = SelectField("Size",
                       choices=[('G1,6', '1'), ('G2,5', '2'), ('G4', '3'),
                                ('G5', '4'), ('G6', '5'), ('G10', '6'),
                                ('G16', '7'), ('G25', '8'), ('G40', '9'),
                                ('G65', '10'), ('G100', '11')
                                ],
                       default='G4')
    gsm_operator = SelectField('GSM Operator',
                               choices=[('Билайн', 'Билайн'),
                                        ('МТС', 'МТС'), ('Мегафон', 'Мегафон')],
                               default='МТС')
    neo_server_adress = StringField(
        'Neo Server Adress', default='194.87.147.191:8500')
    mqtt_server_adress = StringField('MQTT server adress')
    minimal_signal_level = StringField('Minimal signal level')
    minimal_temp_for_gps = StringField('minimal temp for gprs')
    fix_connection_attemp = SelectField('fix connection_attemp',
                                        choices=[('Yes', '1'), ('No', '0')])


class Inc_Insp_Req(FlaskForm):
    part_name = StringField('Part_name')
    drawing_number = StringField('Drawing_number')
    for_product = StringField('For_product')
    param_to_control = SelectField('Param_to_control', choices=[
                                   'внешний вид', 'мех_повреждения'])
    type_of_control = SelectField('Type_to_control', choices=[
                                  'визуальный', 'инструментальный'])
    per_cent_of_control = StringField('Процент контроля')
    used_si_to_control = StringField('Used_si_to_control')
    department = SelectField('Department', choices=[
                             'Служба качества', 'Производство'])
    place_of_control = SelectField('Place_of_control', choices=[
                                   'Склад', 'Производство'])
    action_after_control = SelectField('Action_after_control', choices=[
                                       'Разместить в зоне хранения'])


class Distrib_form(FlaskForm):
    name = StringField('Название')
    region_to_cover = IntegerField('Код региона')
    adress_index = IntegerField('Индекс')
    adress_city = StringField('Город')
    adress_street = StringField('Улица')
    adress_house = StringField('Дом')
    e_mail = StringField('Электронная почта')
    phone = StringField('Контактный телефон')
    contact_person = StringField('Контактное лицо')
