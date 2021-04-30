from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY']='76a917afec96d4d780e4a32b758fe027'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test.db'
# app.config['SQLALCHEMY_DATABASE_URI']='mysql+mysqlconnector://<user>:<password>@<host>[:<port>]/<dbname>'
# app.config['SQLALCHEMY_DATABASE_URI']='engine = create_engine("mariadb+pymysql://user:pass@some_mariadb/dbname?charset=utf8mb4")'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

from es_natin import routes