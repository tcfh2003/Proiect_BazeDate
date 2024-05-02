from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'proiect_bd'

mysql = MySQL(app)

if mysql.connection() is None:
    print("MySQL connection object is None")

print(mysql)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM User WHERE Username = %s", (username,))
    result = cursor.fetchall()
    if result[1] == 0:
        return render_template("login.html", login_info = "User does not exist")
    else:
        cursor.execute("SELECT Password FROM User WHERE Username = %s", (username,))
        result = cursor.fetchall()
        if result[1] != hash(password):
            return render_template("login.html", login_info = "Invalid password")
        else:
            cursor.execute("SELECT * FROM Routines")
            return render_template("home.html", username = username)


@app.route('/routine/<string:routine_name>')
def routine_details(routine_name):
    cursor = mysql.connection.cursor()
    cursor.execute()