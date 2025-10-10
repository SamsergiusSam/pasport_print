from flask import Flask, session
from flask_migrate import Migrate
from sqlalchemy import create_engine, MetaData, Table
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from flask_login import LoginManager, UserMixin, current_user, login_user
from flask_apscheduler import APScheduler
from flask_mail import Mail
# from flask_mailman import Mail


engine = create_engine(
    "postgresql+psycopg2://samsam:Cfv240185@pm-production-samsergius.db-msk0.amvera.tech/pm_production", echo=False)

conn = psycopg2.connect(dbname="pm_production", host="pm-production-samsergius.db-msk0.amvera.tech",
                        user="samsam", password="Cfv240185", port="5432")

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://samsam:Cfv240185@pm-production-samsergius.db-msk0.amvera.tech/pm_production"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:xf8fEl_2dI@89.109.5.208:61110/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '1234567890'


db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

migrate = Migrate(app, db)

scheduler = APScheduler()
scheduler.init_app(app)

Base = db.Model


class si_table(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=False, nullable=False)
    type_name = db.Column(db.String, unique=False, nullable=False)
    serial_number = db.Column(db.String, unique=False, nullable=True)
    produser = db.Column(db.String, unique=False, nullable=True)
    inventory_number = db.Column(db.String, unique=True, nullable=False)
    production_year = db.Column(db.String, unique=False, nullable=True)
    verification_link = db.Column(db.String, unique=False, nullable=True)
    next_verification_date = db.Column(db.Date, unique=False, nullable=True)
    group = db.Column(db.String, unique=False, nullable=True)
    status = db.Column(db.Boolean, default=True)


class inc_insp_list(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    part_name = db.Column(db.String, unique=False, nullable=False)
    drawing_number = db.Column(db.String, unique=False, nullable=True)
    for_product = db.Column(db.String, unique=False, nullable=False)
    param_to_control = db.Column(db.String, unique=False, nullable=False)
    per_cent_of_control = db.Column(db.String, unique=False, nullable=False)
    type_of_control = db.Column(db.String, unique=False, nullable=False)
    used_si_to_control = db.Column(db.String, unique=False, nullable=False)
    department = db.Column(db.String, unique=False, nullable=False)
    place_of_control = db.Column(db.String, unique=False, nullable=False)
    action_after_control = db.Column(db.String, unique=False, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Climat(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    day = db.Column(db.Date, unique=False, nullable=False)
    time = db.Column(db.Time, unique=False, nullable=False)
    temperature = db.Column(db.String, unique=False, nullable=False)
    humidity = db.Column(db.String, unique=False, nullable=False)
    place = db.Column(db.String(50), unique=False, nullable=False)


class FlowDirect(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    serial_number = db.Column(db.Integer, unique=True, nullable=False)
    flow_direction = db.Column(db.Integer, unique=False, nullable=False)
    distr_to_sell_id = db.Column(db.Integer, nullable=True)
    meterVersion = db.Column(db.Integer)


class Regions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    region_name = db.Column(db.String(100), unique=True, nullable=False)


class Supplier_password(db.Model):
    __tablename__ = 'supplier_password'
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String)
    distributer = db.relationship(
        'Distributer',  # Используем точное имя класса
        back_populates='supplier_password',
        uselist=False
    )


class Distributer(db.Model):
    __tablename__ = 'distributer'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    inn = db.Column(db.String(12), nullable=False)
    regions = db.Column(db.JSON, nullable=True)  # Массив регионов
    address = db.Column(db.String(1000), nullable=False)
    email = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    contact_person = db.Column(db.String(200))

    supplier_password_id = db.Column(
        db.Integer, db.ForeignKey('supplier_password.id'), unique=True)
    supplier_password = db.relationship(
        'Supplier_password',
        back_populates='distributer',
        uselist=False
    )


class psi(db.Model):
    psiNumber = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.Integer, nullable=False)
    imei = db.Column(db.BigInteger, unique=True, nullable=False)
    meterNum = db.Column(db.BigInteger, unique=True, nullable=False)
    meterSize = db.Column(db.Integer, nullable=False)
    plombNum = db.Column(db.BigInteger, nullable=False)
    psiPerson = db.Column(db.String(100))
    psiDate = db.Column(db.Date)
    atmPresType = db.Column(db.SmallInteger)
    atmPresTypePasport = db.Column(db.String(10))

    verification_done = db.Column(db.Boolean, default=False, nullable=True)
    verification_date = db.Column(db.Date, nullable=True)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # password_to_add = generate_password_hash('Xnl83DoY')
        # add = User(
        #     username="Корякин А.С.",
        #     email="sales@pro-metrica.ru",
        #     password_hash=password_to_add
        # )
        # db.session.add(add)
        # db.session.commit()
