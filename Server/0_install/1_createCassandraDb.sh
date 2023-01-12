#!/bin/bash

#EXPORTING PYTHON, HADOOP AND SPARK DIR VARIABLES
export PYSPARK_PYTHON=python3
export PYSPARK_DRIVER_PYTHON=python3
export HADOOP_DIR=/home/bigdata2022/hadoop-3.3.4
export SPARK_HOME=/home/bigdata2022/spark-3.2.3
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin:$HADOOP_DIR/bin:$HADOOP_DIR/sbin

#STOPPING HADOOP
$HADOOP_DIR/sbin/stop-dfs.sh
$HADOOP_DIR/sbin/stop-yarn.sh

#RUNNING HADOOP
$HADOOP_DIR/sbin/start-dfs.sh
$HADOOP_DIR/sbin/start-yarn.sh
jps
$HADOOP_DIR/bin/hdfs dfsadmin -safemode leave


#DELETING INPUT IN HDFS
$HADOOP_DIR/bin/hdfs dfs -rm -r /Input/input.csv

#LOADING INPUT IN HDFS
$HADOOP_DIR/bin/hdfs dfs -put ./cassandra/Input /

#STARTING CASSANDRA SERVICE
sudo service cassandra start

#CREATING DB AND TABLE
cqlsh < ./cassandra/cqlscript.cql

#PRE-PROCESSING DATASET AND INSERTING IN TABLE
$SPARK_HOME/bin/spark-submit --packages com.datastax.spark:spark-cassandra-connector_2.12:3.2.0 --deploy-mode client  --driver-memory 3g  --executor-memory 3g  --executor-cores 2  --queue default ./cassandra/preProcessing.py

#STARTING CASSANDRA SERVICE
sudo service cassandra stop

#STOPPING HADOOP
$HADOOP_DIR/sbin/stop-dfs.sh
$HADOOP_DIR/sbin/stop-yarn.sh