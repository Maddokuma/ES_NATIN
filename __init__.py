from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import pymysql
pymysql.install_as_MySQLdb()
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY']='76a917afec96d4d780e4a32b758fe027'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@127.0.0.1:3306/esnatin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db_connection = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database = "esnatin.db"
)
print(db_connection)
# app.config['SQLALCHEMY_DATABASE_URI']='mysql+mysqlconnector://root:''@localhost/esnatin.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/esnatin.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql:///username:password@localhost/db_name'
# app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test.db'
# app.config['SQLALCHEMY_DATABASE_URI']='mysql+mysqlconnector://<user>:<password>@<host>[:<port>]/<dbname>'
# app.config['SQLALCHEMY_DATABASE_URI']='engine = create_engine("mariadb+pymysql://user:pass@some_mariadb/dbname?charset=utf8mb4")'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

from es_natin import routes