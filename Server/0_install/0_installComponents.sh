#!/bin/bash

# INSTALLING JAVA 8
sudo apt-get install openjdk-8-jdk
sudo update-alternatives --set java /usr/lib/jvm/jdk1.8.0_version/bin/jav

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

# INSTALLING CASSANDRA
apt-get install gnupg2 wget curl unzip apt-transport-https -y
wget -q -O - https://www.apache.org/dist/cassandra/KEYS | apt-key add -
sh -c 'echo "deb http://www.apache.org/dist/cassandra/debian 311x main" > /etc/apt/sources.list.d/cassandra.list'
apt-get update -y
apt-get install cassandra -y

# INSTALLING PYTHON MODULES
pip install pyspark==3.1.3
pip install matplotlib
pip install pandas
pip install seaborn
pip install pyspark2pmml
pip install --upgrade openscoring
pip install -U scikit-learn
pip install flask
pip install datetime
pip install cassandra.driver