#!/bin/bash 

export PYSPARK_PYTHON=python3
export PYSPARK_DRIVER_PYTHON=python3
export SPARK_HOME=/home/bigdata2022/spark-3.2.3
export PATH=:/home/bigdata2022/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/snap/bin:/home/bigdata2022/spark-3.2.3/bin:/home/bigdata2022/spark-3.2.3/sbin:/home/bigdata2022/.local/bin

#STOPPING HADOOP
$HADOOP_DIR/sbin/stop-dfs.sh
$HADOOP_DIR/sbin/stop-yarn.sh

#RUNNING HADOOP
$HADOOP_DIR/sbin/start-dfs.sh
$HADOOP_DIR/sbin/start-yarn.sh
jps

#DELETING INPUT/OUTPUT DIRECTORY IN HDFS AND LOCAL
rm -r ../OutputImg/Pie/*
rm -r ../OutputImg/Rel/*
rm -r ../OutputImg/correlation.png
$HADOOP_DIR/bin/hdfs dfsadmin -safemode leave
$HADOOP_DIR/bin/hdfs dfs -rm -r /Input

#LOADING INPUT IN HDFS
$HADOOP_DIR/bin/hdfs dfs -put ../Input /

#INSTALLING PYTHON MODULES
pip install pyspark==3.1.3
pip install matplotlib
pip install pandas
pip install seaborn
pip install pyspark2pmml
pip install --upgrade openscoring

#LAUNCHING THE OPENSCORING SERVER ON http://localhost:8080/openscoring
java -jar ../lib/openscoring-server-executable-2.1.1.jar &

#DISABLING CHROME SECURITY
google-chrome --disable-web-security

#SETTING SPARK AND CREATE PREDICTION MODEL
$SPARK_HOME/bin/spark-submit --packages org.jpmml:pmml-sparkml:2.2.0,org.jpmml:pmml-sparkml-lightgbm:2.2.0,org.jpmml:pmml-sparkml-xgboost:2.2.0  --master yarn  --deploy-mode client  --driver-memory 3g  --executor-memory 3g  --executor-cores 2  --queue default ../PySpark/createModel.py