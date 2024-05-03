CREATE DATABASE proiect_bd;

USE proiect_bd;

CREATE TABLE UserPrivilages ( 
	UserPrivilages VARCHAR (40) NOT NULL PRIMARY KEY
);

CREATE TABLE User ( 
	UserId INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
    Username VARCHAR(40) NOT NULL,
    Password BIGINT,
    User_Privilages VARCHAR(40) NOT NULL,   
    FOREIGN KEY  (User_Privilages) REFERENCES UserPrivilages (UserPrivilages) 
    );

CREATE TABLE SensorType ( 
	SensorType VARCHAR (40) NOT NULL PRIMARY KEY 
    );

CREATE TABLE Sensors (  
	SensorID INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
    Sensor_Name VARCHAR (40) NOT NULL, 
    Sensor_Type VARCHAR (40) NOT NULL,
    FOREIGN KEY  (Sensor_Type) REFERENCES SensorType (SensorType) 
    );

CREATE TABLE EffectorType ( 
	EffectorType VARCHAR(40) NOT NULL PRIMARY KEY 
    );

CREATE TABLE Effectors ( 
	EffectorID INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
    Effector_Name VARCHAR (40) NOT NULL, 
    Effector_Type VARCHAR (40) NOT NULL,
	FOREIGN KEY  (Effector_Type) REFERENCES EffectorType (EffectorType) 
    );

CREATE TABLE RoutineRunTimes ( 
	RoutineRunTimes INT NOT NULL PRIMARY KEY 
    );

CREATE TABLE Routine ( 
	RoutineID INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
    RoutineName VARCHAR(40) NOT NULL , 
    SensorID INT , 
    EffectorID INT , 
    Start_Time VARCHAR (20), 
    Stop_Time VARCHAR(20), 
    Routine_RunTime INT NOT NULL,
    FOREIGN KEY  (Routine_RunTime) REFERENCES RoutineRunTimes (RoutineRunTimes),
    FOREIGN KEY  (SensorID) REFERENCES Sensors (SensorID),
    FOREIGN KEY  (EffectorID) REFERENCES Effectors (EffectorID)
    
    ); 


CREATE TABLE IPAdressSpace ( 
	IP_Adress INT NOT NULL PRIMARY KEY, 
    Protocol VARCHAR (20) NOT NULL , 
    Subnet VARCHAR (20) NOT NULL, 
    Gateway VARCHAR (20) NOT NULL, 
    SensorID INT UNIQUE , 
    EffectorID INT UNIQUE,
	FOREIGN KEY (SensorID) REFERENCES Sensors(SensorID),
	FOREIGN KEY (EffectorID) REFERENCES Effectors(EffectorID)
	
    );
