DROP KEYSPACE IF EXISTS heartDisease;

CREATE KEYSPACE heartDisease WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };

USE heartDisease;

CREATE TABLE features (HeartDisease varchar, BMI DOUBLE, Smoking varchar, AlcoholDrinking varchar, Stroke varchar, PhysicalHealth DOUBLE, MentalHealth DOUBLE, DiffWalking varchar, Sex varchar, AgeCategory varchar, Race varchar, Diabetic varchar, PhysicalActivity varchar, GenHealth varchar, SleepTime DOUBLE, Asthma varchar, KidneyDisease varchar, SkinCancer varchar, id varchar PRIMARY KEY);

SHOW HOST;

exit;