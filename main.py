from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import hashlib

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'sudoroot1234'
app.config['MYSQL_DB'] = 'proiect_bd'

mysql = MySQL(app)

# if mysql.connection() is None:
#     print("MySQL connection object is None")
#
# print(mysql)

def hash_password(password):
    # this function generates the hash for a provided password in string format
    password = password.encode('utf-8')
    hash = hashlib.sha256(password)
    return hash.hexdigest()



# global variables go here
username = ""
sensor_add_status = ""
sensor_delete_status = ""
effector_add_status = ""
effector_delete_status = ""
modify_routine_status = ""


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login/login_form', methods=['POST'])
def login_form():
    if request.method == "POST":
        global username
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM User WHERE Username = %s", (username,))
        result = cursor.fetchall()
        if result[0][0] == 0:
            cursor.close()
            return render_template("login.html" , login_info = "User does not exist")
        else:
            cursor.execute("SELECT Password FROM User WHERE Username = %s", (username,))
            result = cursor.fetchall()
            cursor.close()
            if result[0][0] != hash_password(password):
                return render_template("login.html", login_info="Invalid password")
            else:
                return redirect(url_for("home"))


@app.route('/home')
def home():
    global username
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Routine")
    routines = cursor.fetchall()
    cursor.execute("SELECT * FROM RoutineRuntimes")
    routineRuntimes = cursor.fetchall()
    cursor.close()
    global sensor_add_status
    sensor_add_status = ""
    global sensor_delete_status
    sensor_delete_status = ""
    global effector_add_status
    effector_add_status = ""
    global effector_delete_status
    effector_delete_status = ""
    global modify_routine_status
    return render_template("home.html", routines = routines , username = username, routineRuntimes = routineRuntimes,
                           modify_routine_status = modify_routine_status)


@app.route('/add_routine', methods=['POST'])
def add_routine():
    if request.method == 'POST':
        routine_name = request.form['routine_name']
        routine_runtime = request.form['routine_runtime']
        start_time = request.form['start_time']
        stop_time = request.form['stop_time']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO Routine (RoutineName, Routine_RunTime, Start_Time, Stop_Time) VALUES (%s, %s, %s, %s)",
                       (routine_name, routine_runtime, start_time, stop_time))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('home'))


@app.route('/modify_routine', methods=['POST'])
def modify_routine():
    global modify_routine_status
    if request.method == 'POST':
        routineID = request.form['routineID']
        routine_name = request.form['routine_name']
        routine_runtime = request.form['routine_runtime']
        start_time = request.form['start_time']
        stop_time = request.form['stop_time']

        if start_time == 'NULL':
            start_time = None
        if stop_time == 'NULL':
            stop_time = None

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM Routine WHERE RoutineID = %s", (routineID,))
        result = cursor.fetchone()
        if result[0] == 1:
            cursor.execute("UPDATE Routine SET RoutineName = %s , Routine_RunTime = %s , Start_Time = %s , Stop_Time = %s WHERE RoutineID = %s",
                           (routine_name, routine_runtime, start_time, stop_time, routineID))
            cursor.connection.commit()
            cursor.close()
            modify_routine_status = ""
            return redirect(url_for('home'))
        else:
            modify_routine_status = "The Routine ID entered doesn't exist"
            return redirect(url_for('home'))


@app.route('/routine/<string:routine_name>')
def routine_details(routine_name):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT RoutineID FROM Routine WHERE RoutineName = %s", (routine_name,))
    routine_id = cursor.fetchone()
    cursor.execute("SELECT * FROM Sensors WHERE SensorID IN (SELECT SensorID FROM SensorList WHERE RoutineID = %s)", (routine_id,))
    sensors = cursor.fetchall()
    cursor.execute("SELECT * FROM Effectors WHERE EffectorID IN (SELECT EffectorID FROM EffectorList WHERE RoutineID = %s)", (routine_id,))
    effectors = cursor.fetchall()
    cursor.execute("SELECT Routine_Runtime FROM Routine WHERE RoutineID = %s", (routine_id,))
    routine_runtime = cursor.fetchone()

    if routine_runtime[0] == 'Continuous':
        activation_state = 'Active'
    elif routine_runtime[0] == 'TimeWindow':
        cursor.execute("SELECT Start_Time, Stop_Time FROM Routine WHERE RoutineID = %s", (routine_id,))
        time_window = cursor.fetchone()
        start_time = str(time_window[0])
        stop_time = str(time_window[1])
        cursor.execute("SELECT IsActiveNow(%s, %s)", (start_time, stop_time))
        activation_state = cursor.fetchone()
        if activation_state[0] == 1:
            activation_state = 'Active'
        else:
            activation_state = 'Inactive'
    else:
        activation_state = 'Unknown'

    cursor.close()
    global sensor_add_status
    global sensor_delete_status
    global effector_add_status
    global effector_delete_status
    return render_template('routine_details.html' , routine_name = routine_name , activation_state = activation_state ,
                           sensors = sensors , effectors = effectors, sensor_add_status = sensor_add_status , sensor_delete_status = sensor_delete_status,
                           effector_add_status = effector_add_status , effector_delete_status = effector_delete_status)


@app.route('/routine/<string:routine_name>/add_routine_sensor' , methods = ['POST'])
def add_routine_sensor(routine_name):
    if request.method == 'POST':
        global sensor_add_status
        sensor_name = request.form['sensor_name']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM Sensors WHERE Sensor_Name = %s", (sensor_name,))
        exists = cursor.fetchone()
        print(exists)
        if exists[0] == 1:
            cursor.execute("SELECT RoutineID FROM Routine WHERE RoutineName = %s", (routine_name,))
            routine_id = cursor.fetchone()
            cursor.execute("SELECT SensorID FROM Sensors WHERE Sensor_Name = %s", (sensor_name,))
            sensor_id = cursor.fetchone()
            cursor.execute("INSERT INTO SensorList (SensorID, RoutineID) VALUES (%s, %s)", (sensor_id, routine_id))
            cursor.connection.commit()
            cursor.close()
            sensor_add_status = ""
            return redirect(url_for('routine_details', routine_name = routine_name))
        else:
            sensor_add_status = "The sensor you have entered doesn't exist"
            cursor.close()
            return redirect(url_for('routine_details', routine_name = routine_name , sensor_add_status = sensor_add_status))


@app.route('/routine/<string:routine_name>/delete_routine_sensor' , methods = ['POST'])
def delete_routine_sensor(routine_name):
    if request.method == 'POST':
        global sensor_delete_status
        sensor_name = request.form['sensor_name']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM Sensors WHERE Sensor_Name = %s", (sensor_name,))
        exists = cursor.fetchone()
        if exists[0] == 1:
            cursor.execute("SELECT RoutineID FROM Routine WHERE RoutineName = %s", (routine_name,))
            routine_id = cursor.fetchone()
            cursor.execute("SELECT SensorID FROM Sensors WHERE Sensor_Name = %s", (sensor_name,))
            sensor_id = cursor.fetchone()
            cursor.execute("DELETE FROM SensorList WHERE SensorID = %s AND RoutineID = %s", (sensor_id, routine_id))
            mysql.connection.commit()
            cursor.close()
            sensor_delete_status = ""
            return redirect(url_for('routine_details', routine_name = routine_name))
        else:
            sensor_delete_status = "The sensor you have entered doesn't exist"
            cursor.close()
            return redirect(url_for('routine_details', routine_name = routine_name))


@app.route('/routine/<string:routine_name>/add_routine_effector' , methods = ['POST'])
def add_routine_effector(routine_name):
    if request.method == 'POST':
        global effector_add_status
        effector_name = request.form['effector_name']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM Effectors WHERE Effector_Name = %s", (effector_name,))
        exists = cursor.fetchone()
        if exists[0] == 1:
            cursor.execute("SELECT RoutineID FROM Routine WHERE RoutineName = %s", (routine_name,))
            routine_id = cursor.fetchone()
            cursor.execute("SELECT EffectorID FROM Effectors WHERE Effector_Name = %s", (effector_name,))
            effector_id = cursor.fetchone()
            cursor.execute("INSERT INTO EffectorList (EffectorID, RoutineID) VALUES (%s, %s)", (effector_id, routine_id))
            cursor.connection.commit()
            cursor.close()
            effector_add_status = ""
            return redirect(url_for('routine_details', routine_name = routine_name))
        else:
            effector_add_status = "The effector you have entered doesn't exist"
            cursor.close()
            return redirect(url_for('routine_details', routine_name = routine_name))


@app.route('/routine/<string:routine_name>/delete_routine_effector' , methods = ['POST'])
def delete_routine_effector(routine_name):
    if request.method == 'POST':
        global effector_delete_status
        effector_name = request.form['effector_name']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM Effectors WHERE Effector_Name = %s", (effector_name,))
        exists = cursor.fetchone()
        if exists[0] == 1:
            cursor.execute("SELECT RoutineID FROM Routine WHERE RoutineName = %s", (routine_name,))
            routine_id = cursor.fetchone()
            cursor.execute("SELECT EffectorId FROM Effectors WHERE Effector_Name = %s", (effector_name,))
            effector_id = cursor.fetchone()
            cursor.execute("DELETE FROM EffectorList WHERE EffectorID = %s AND RoutineID = %s", (effector_id, routine_id))
            mysql.connection.commit()
            cursor.close()
            effector_delete_status = ""
            return redirect(url_for('routine_details', routine_name = routine_name))
        else:
            effector_delete_status = "The effector you have entered doesn't exist"
            cursor.close()
            return redirect(url_for('routine_details', routine_name = routine_name))


@app.route('/routine/<string:routine_name>/delete_routine' , methods = ['POST'])
def delete_routine(routine_name):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT RoutineID FROM Routine WHERE RoutineName = %s", (routine_name,))
    routine_id = cursor.fetchone()
    cursor.execute("DELETE FROM SensorList WHERE RoutineID = %s", (routine_id,))
    cursor.connection.commit()
    cursor.execute("DELETE FROM EffectorList WHERE RoutineID = %s", (routine_id,))
    cursor.connection.commit()
    cursor.execute("DELETE FROM Routine WHERE RoutineID = %s", (routine_id,))
    cursor.connection.commit()
    cursor.close()
    return redirect(url_for('home'))


@app.route('/sensors')
def sensors():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Sensors AS s LEFT JOIN IPAddressSpace AS ip ON s.IP_Address = ip.IP_Address")
    sensors = cursor.fetchall()
    cursor.execute("SELECT * FROM SensorType")
    sensorTypes = cursor.fetchall()
    cursor.close()
    return render_template("sensors.html", sensors = sensors , sensorTypes = sensorTypes)


@app.route('/sensors/add_sensor', methods=['POST'])
def add_sensor():
    if request.method == 'POST':
        sensor_name = request.form['sensor_name']
        sensor_type = request.form['sensor_type']
        ip_address = request.form['ip_address']
        protocol = request.form['protocol']
        subnet = request.form['subnet']
        gateway = request.form['gateway']

        cursor = mysql.connection.cursor()
        cursor.execute("CALL AddSensor(%s, %s, %s, %s, %s, %s)", (sensor_name, sensor_type, ip_address, protocol, subnet, gateway))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("sensors"))


@app.route('/sensors/remove_sensor', methods=['POST'])
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


@app.route('/effectors/add_effector', methods=['POST'])
def add_effector():
    if request.method == 'POST':
        effector_name = request.form['effector_name']
        effector_type = request.form['effector_type']
        ip_address = request.form['ip_address']
        protocol = request.form['protocol']
        subnet = request.form['subnet']
        gateway = request.form['gateway']

        cursor = mysql.connection.cursor()
        cursor.execute("CALL AddEffector(%s, %s, %s, %s, %s, %s)", (effector_name, effector_type, ip_address, protocol, subnet, gateway))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("effectors"))


@app.route('/effectors/remove_effector', methods=['POST'])
def remove_effector():
    if request.method == 'POST':
        effector_name = request.form['effector_name']

        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Effectors WHERE effector_name = %s", (effector_name,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("effectors"))




if __name__ == '__main__':
    app.run(debug=True)