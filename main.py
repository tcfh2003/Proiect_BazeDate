from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'sudoroot1234'
app.config['MYSQL_DB'] = 'proiect_bd'

mysql = MySQL(app)

if mysql.connection() is None:
    print("MySQL connection object is None")

print(mysql)


# global variables go here
username = ""


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    global username
    username = request.form.get('username')
    password = request.form.get('password')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM User WHERE Username = %s", (username,))
    result = cursor.fetchall()
    if result == 0:
        cursor.close()
        return render_template("login.html", login_info = "User does not exist")
    else:
        cursor.execute("SELECT Password FROM User WHERE Username = %s", (username,))
        result = cursor.fetchall()
        cursor.close()
        if result[1] != hash(password):
            return render_template("login.html", login_info = "Invalid password")
        else:
            return redirect(url_for("home.html"))


@app.route('/home')
def home():
    global username
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Routine")
    routines = cursor.fetchall()
    cursor.close()
    return render_template("home.html", routines = routines , username = username)


@app.route('add_routine', methods=['POST'])
def add_routine():
    if request.method == 'POST':
        routine_name = request.form['routine_name']
        routine_runtime = request.form['routine_runtime']
        start_time = request.form['start_time']
        stop_time = request.form['stop_time']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO Routine (RoutineName, RoutineRuntime, StartTime, StopTime) VALUES (%s, %s, %s, %s)",
                       (routine_name, routine_runtime, start_time, stop_time))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('home'))


@app.route('/routine/<string:routine_name>')
def routine_details(routine_name):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Sensors WHERE SensorID IN (SELECT SensorID FROM SensorList WHERE RoutineID IN (SELECT RoutineID FROM Routine))")
    sensors = cursor.fetchall()
    cursor.execute("SELECT * FROM Effectors WHERE EffectorID IN (SELECT EffectorID FROM EffectorList WHERE RoutineID IN (SELECT RoutineID FROM Routine))")
    effectors = cursor.fetchall()
    cursor.execute("SELECT RoutineID FROM Routine WHERE RoutineName = %s", (routine_name,))
    routine_id = cursor.fetchone()
    cursor.execute("SELECT RoutineRuntime FROM Routine WHERE RoutineID = %s", (routine_id,))
    routine_runtime = cursor.fetchone()

    if routine_runtime == 'Continuous':
        activation_state = 'Active'
    elif routine_runtime == 'TimeWindow':
        cursor.execute("SELECT IsActiveNow((SELECT StartTime FROM Routine WHERE RoutineID = %s) , (SELECT Stop_Time FROM Routine WHERE RoutineID))", (routine_id,))


@app.route('/sensors')
def sensors():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Sensors AS s LEFT JOIN IPAddressSpace AS ip ON s.IP_Address = ip.IP_Address")
    sensors = cursor.fetchall()
    cursor.execute("SELECT * FROM SensorType")
    sensorTypes = cursor.fetchall()
    cursor.close()
    return render_template("sensors.html", sensors = sensors , sensorTypes = sensorTypes)


@app.route('/add_sensor', methods=['POST'])
def add_sensor():
    if request.method == 'POST':
        sensor_name = request.form['sensor_name']
        sensor_type = request.form['sensor_type']
        ip_address = request.form['ip_address']
        protocol = request.form['protocol']
        subnet = request.form['subnet']
        gateway = request.form['gateway']

        cursor = mysql.connection.cursor()
        cursor.execute("CALL AddSensor(%s %s %s %s %s %s)", (sensor_name, sensor_type, ip_address, protocol, subnet, gateway))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("sensors"))


@app.route('/remove_sensor', methods=['POST'])
def remove_sensor():
    if request.method == 'POST':
        sensor_name = request.form['sensor_name']

        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Sensors WHERE sensor_name = %s", (sensor_name,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("sensors"))


@app.route('/effectors')
def effectors():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Effectors AS e LEFT JOIN IPAddressSpace AS ip ON e.IP_Address = ip.IP_Address")
    effectors = cursor.fetchall()
    cursor.execute("SELECT * FROM EffectorType")
    effectorTypes = cursor.fetchall()
    cursor.close()
    return render_template("effectors.html", effectors = effectors , effectorTypes = effectorTypes)


@app.route('/add_effector', methods=['POST'])
def add_effector():
    if request.method == 'POST':
        effector_name = request.form['effector_name']
        effector_type = request.form['effector_type']
        ip_address = request.form['ip_address']
        protocol = request.form['protocol']
        subnet = request.form['subnet']
        gateway = request.form['gateway']

        cursor = mysql.connection.cursor()
        cursor.execute("CALL AddEffector(%s %s %s %s %s %s)", (effector_name, effector_type, ip_address, protocol, subnet, gateway))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("effectors"))


@app.route('/remove_effector', methods=['POST'])
def remove_effector():
    if request.method == 'POST':
        effector_name = request.form['effector_name']

        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Effectors WHERE effector_name = %s", (effector_name,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("effectors"))




