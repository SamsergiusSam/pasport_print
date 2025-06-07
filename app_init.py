from flask import Flask
from sqlalchemy import create_engine, MetaData, Table
from flask_sqlalchemy import SQLAlchemy
import psycopg2

engine = create_engine(
    "postgresql+psycopg2://samsam:Cfv240185@pm-production-samsergius.db-msk0.amvera.tech/pm_production", echo=False)

conn = psycopg2.connect(dbname="pm_production", host="pm-production-samsergius.db-msk0.amvera.tech",
                        user="samsam", password="Cfv240185", port="5432")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://samsam:Cfv240185@pm-production-samsergius.db-msk0.amvera.tech/pm_production"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '1234567890'
db = SQLAlchemy(app)


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


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)


# with app.app_context():
#     db.create_all()
