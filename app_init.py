from flask import Flask, session
from sqlalchemy import create_engine, MetaData, Table
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from flask_login import LoginManager, UserMixin, current_user, login_user


engine = create_engine(
    "postgresql+psycopg2://samsam:Cfv240185@pm-production-samsergius.db-msk0.amvera.tech/pm_production", echo=False)

conn = psycopg2.connect(dbname="pm_production", host="pm-production-samsergius.db-msk0.amvera.tech",
                        user="samsam", password="Cfv240185", port="5432")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://samsam:Cfv240185@pm-production-samsergius.db-msk0.amvera.tech/pm_production"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '1234567890'


db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'


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


if __name__ == "__main__":
    with app.app_context():
        # db.create_all()
        password_to_add = generate_password_hash('Xnl83DoY')
        add = User(
            username="Корякин А.С.",
            email="sales@pro-metrica.ru",
            password_hash=password_to_add
        )
        db.session.add(add)
        db.session.commit()
