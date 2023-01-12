from flask import Flask
from flask import request
import pyspark
from pyspark.sql.functions import col,isnan,when,count,explode,array,lit
import json
from datetime import datetime
from cassandra.cluster import Cluster

app = Flask(__name__)
cluster = Cluster()
session = cluster.connect('heartdisease', wait_for_all_pools=True)

@app.route('/insert', methods=['POST'])
def add_income():
    paramList = request.get_json()
    arg = [i for i in paramList['arguments'].values()]
    print(arg)
    query = "INSERT INTO features (id, bmi, smoking, alcoholdrinking, stroke, physicalhealth, mentalhealth, diffwalking, sex, agecategory, race, diabetic, physicalactivity, genhealth, sleeptime, asthma, kidneydisease, skincancer, heartdisease) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    session.execute(query, arg)
    return '', 204

app.run()