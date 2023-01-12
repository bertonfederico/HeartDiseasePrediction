#!/bin/bash

# INSTALLING HADOOP 3.3.4
HADOOP_PATH = "/home/bigdata2022"
wget https://downloads.apache.org/hadoop/common/hadoop-3.3.4/hadoop-3.3.4.tar.gz
tar xzf hadoop-*
mv hadoop-3.3.4 HADOOP_PATH

# INSTALLING SPARK 3.2.3
SPARK_PATH = "/home/bigdata2022"
wget https://downloads.apache.org/spark/spark-3.2.3/spark-3.2.3-bin-hadoop3.2.tgz
tar xvf spark-*
mv spark-3.0.1-bin-hadoop2.7 SPARK_PATH

# INSTALLING PYTHON MODULES
pip install pyspark==3.1.3
pip install matplotlib
pip install pandas
pip install seaborn
pip install pyspark2pmml
pip install --upgrade openscoring
pip install -U scikit-learn
pip install Flask
pip install datetime
pip install cassandra.cluster