CREATE DATABASE proiect_bd;
USE proiect_bd;

CREATE TABLE UserPrivileges (
	UserPrivileges VARCHAR(40) NOT NULL PRIMARY KEY
);

CREATE TABLE User (
	UserID INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(40) NOT NULL,
    Password VARCHAR(255) NOT NULL,
    User_Privileges VARCHAR(40) NOT NULL,
    FOREIGN KEY (User_Privileges) REFERENCES UserPrivileges (UserPrivileges)
);

CREATE TABLE SensorType ( 
	SensorType VARCHAR(40) NOT NULL PRIMARY KEY 
);

CREATE TABLE IPAddressSpace (
	IP_Address VARCHAR(40) NOT NULL PRIMARY KEY,
    Protocol VARCHAR(40) NOT NULL,
    Subnet VARCHAR(40) NOT NULL,
    Gateway VARCHAR(40) NOT NULL
);

CREATE TABLE Sensors (  
	SensorID INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
    Sensor_Name VARCHAR(40) NOT NULL, 
    Sensor_Type VARCHAR(40) NOT NULL,
    IP_Address VARCHAR(40) NOT NULL, 
    FOREIGN KEY (Sensor_Type) REFERENCES SensorType (SensorType),
    FOREIGN KEY (IP_Address) REFERENCES IPAddressSpace (IP_Address)
);

CREATE TABLE EffectorType (
	EffectorType VARCHAR(40) NOT NULL PRIMARY KEY
);

CREATE TABLE Effectors ( 
	EffectorID INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
    Effector_Name VARCHAR (40) NOT NULL, 
    Effector_Type VARCHAR (40) NOT NULL,
    IP_Address VARCHAR(40) NOT NULL,
	FOREIGN KEY (Effector_Type) REFERENCES EffectorType (EffectorType),
    FOREIGN KEY (IP_Address) REFERENCES IPAddressSpace (IP_Address)
);

CREATE TABLE RoutineRunTimes ( 
	RoutineRunTimes VARCHAR(40) NOT NULL PRIMARY KEY 
);

CREATE TABLE Routine ( 
	RoutineID INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    RoutineName VARCHAR(40) NOT NULL , 
    Start_Time TIME, 
    Stop_Time TIME, 
    Routine_RunTime VARCHAR(40) NOT NULL,
    FOREIGN KEY  (Routine_RunTime) REFERENCES RoutineRunTimes (RoutineRunTimes)
);

CREATE TABLE SensorList (
	SensorID INT NOT NULL,
    RoutineID INT NOT NULL,
    PRIMARY KEY (SensorID, RoutineID),
    FOREIGN KEY (SensorID) REFERENCES Sensors (SensorID),
    FOREIGN KEY (RoutineID) REFERENCES Routine (RoutineID)
);

CREATE TABLE EffectorList (
	EffectorID INT NOT NULL,
    RoutineID INT NOT NULL,
    PRIMARY KEY (EffectorID, RoutineID),
    FOREIGN KEY (EffectorID) REFERENCES Effectors (EffectorID),
    FOREIGN KEY (RoutineID) REFERENCES Routine (RoutineID)
);

-- ------------------------------
DROP PROCEDURE IF EXISTS AddSensor;
DELIMITER $$
CREATE PROCEDURE AddSensor (IN SensorName VARCHAR(40) , IN SensorType VARCHAR(40) , 
							IN IP_Address VARCHAR(40) , IN Protocol VARCHAR(40) , IN Subnet VARCHAR(40) , IN Gateway VARCHAR(40))
BEGIN
	IF (SELECT COUNT(*) FROM IPAddressSpace WHERE IPAddressSpace.IP_Address = IP_Address) != 0 THEN
		UPDATE IPAddressSpace AS i SET i.Protocol = Protocol , i.Subnet = Subnet , i.Gateway = Gateway WHERE i.IP_Address = IP_Address;
	ELSE
		INSERT INTO IPAddressSpace (Ip_Address , Protocol, Subnet , Gateway) VALUES (Ip_Address , Protocol, Subnet , Gateway);
	END IF;
    
    INSERT INTO Sensors (Sensor_Name, Sensor_Type, IP_Address) VALUES (SensorName, SensorType, IP_Address);
END $$
DELIMITER ;



DROP PROCEDURE IF EXISTS AddEffector;
DELIMITER $$
CREATE PROCEDURE AddEffector (IN EffectorName VARCHAR(40) , IN EffectorType VARCHAR(40) , 
							IN IP_Address VARCHAR(40) , IN Protocol VARCHAR(40) , IN Subnet VARCHAR(40) , IN Gateway VARCHAR(40))
BEGIN
	IF (SELECT COUNT(*) FROM IPAddressSpace WHERE IPAddressSpace.IP_Address = IP_Address) != 0 THEN
		UPDATE IPAddressSpace AS i SET i.Protocol = Protocol , i.Subnet = Subnet , i.Gateway = Gateway WHERE i.IP_Address = IP_Address;
	ELSE
		INSERT INTO IPAddressSpace (Ip_Address , Protocol, Subnet , Gateway) VALUES (Ip_Address , Protocol, Subnet , Gateway);
	END IF;
    
    INSERT INTO Effectors (Effector_Name, Effector_Type, IP_Address) VALUES (EffectorName, EffectorType, IP_Address);
END $$
DELIMITER ;


DROP FUNCTION IF EXISTS IsActiveNow;
DELIMITER $$
CREATE FUNCTION IsActiveNow(start_time TIME, stop_time TIME) RETURNS BOOL
DETERMINISTIC
CONTAINS SQL
BEGIN
	DECLARE time_now TIME;
    SET time_now = TIME(NOW());
    
    IF(start_time <= stop_time) THEN
		IF(time_now >= start_time AND time_now < stop_time) THEN
			RETURN TRUE;
		ELSE
			RETURN FALSE;
		END IF;
	ELSE
		IF(time_now >= start_time OR time_now < stop_time) THEN
			RETURN TRUE;
		ELSE
			RETURN FALSE;
		END IF;
	END IF;
END $$
DELIMITER ;

-- ------------------------------------------------------------------------------------------------------

INSERT INTO UserPrivileges VALUES ('Read_Data') , ('Read/Write_Data');
INSERT INTO User(Username, Password, User_Privileges) VALUES 
	('Admin', '4813494d137e1631bba301d5acab6e7bb7aa74ce1185d456565ef51d737677b2', 'Read/Write_Data'),			-- pw = root
    ('Andrei', '65bb1cc2fd5feddea98e1d9e3ec89fae2a3f50ed42d6fb96962ef8cd0e2cfcb7', 'Read_Data'),				-- pw = parola1
    ('Theo', '102c304fa0934097958dfb45fec492d8a4f1610c33211944a5a1eeefa4c93de5', 'Read_Data'),					-- pw = parola2
    ('Emi', '8e1f27aaf4f508836284575560431e21f1990ee35909c0233c747d8ba82e82b8', 'Read_Data');					-- pw = parola3

INSERT INTO SensorType VALUES ('MovementSensor') , ('TemperatureSensor') , ('HumiditySensor') , ('LightSensor');
INSERT INTO EffectorType VALUES ('Lightbulb') , ('AirConditioner') , ('Heater');

INSERT INTO IPAddressSpace VALUES
	('192.168.2.100' , 'TCP/IP' , '255.255.255.0' , '192.168.2.0'),
    ('192.168.2.101' , 'TCP/IP' , '255.255.255.0' , '192.168.2.0'),
    ('192.168.2.102' , 'TCP/IP' , '255.255.255.0' , '192.168.2.0'),
    ('192.168.2.103' , 'TCP/IP' , '255.255.255.0' , '192.168.2.0'),
    ('192.168.2.104' , 'TCP/IP' , '255.255.255.0' , '192.168.2.0'),
    ('192.168.2.105' , 'TCP/IP' , '255.255.255.0' , '192.168.2.0');
    
INSERT INTO RoutineRunTimes VALUES ('Continuous') , ('TimeWindow');
INSERT INTO Routine VALUES
	(1 , 'Lights On When People Present', NULL, NULL, 'Continuous'),
    (2 , 'Lights Off When NightTime', '21:00' , '06:00', 'TimeWindow');
    
INSERT INTO Sensors VALUES
	(1 , 'Hallway Movement Sensor', 'MovementSensor', '192.168.2.100');
    
INSERT INTO Effectors VALUES
	(1 , 'Hallway Light 1' , 'Lightbulb' , '192.168.2.101'),
    (2 , 'Hallway Light 2' , 'Lightbulb' , '192.168.2.102');
    
INSERT INTO SensorList (SensorID , RoutineID) VALUES (1 , 1);
INSERT INTO EffectorList (EffectorID , RoutineID) VALUES (1 , 1), (2 , 1) , (1 , 2) , (2 , 2);

SELECT * FROM Effectors AS e LEFT JOIN IPAddressSpace AS ip ON e.IP_Address = ip.IP_Address;
SELECT * FROM EffectorType;

CALL AddSensor('TestSensor' , 'TemperatureSensor' , '192.168.2.150' , 'TCP/IP', '255.255.255.0' , '192.168.2.0');
DELETE FROM Sensors WHERE SensorId = 2;
DELETE FROM IPAddressSpace WHERE IP_Address = '192.168.2.150';

SELECT * FROM Sensors WHERE SensorID IN (SELECT SensorID FROM SensorList WHERE RoutineID IN (SELECT RoutineID FROM Routine));
SELECT * FROM Effectors WHERE EffectorID IN (SELECT EffectorID FROM EffectorList WHERE RoutineID IN (SELECT RoutineID FROM Routine));



SELECT @time_now := TIME(NOW());
SELECT Start_Time, Stop_Time INTO @start_time, @stop_time FROM Routine AS r WHERE r.RoutineID = 5;
SELECT @time_now, @start_time, @stop_time;

SELECT (@start_time <= @stop_time);
SELECT (@time_now >= @start_time AND @time_now < @stop_time);

SELECT TIME(NOW());
SELECT IsActiveNow(@stop_time, @start_time);