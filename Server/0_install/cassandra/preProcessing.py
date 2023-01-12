import pkg_resources
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import col,isnan,when,count,explode,array,lit,monotonically_increasing_id

# Creating spark session and context
spark=SparkSession.builder.appName('HeartDiseaseDataPreProcessing').getOrCreate()
sc = spark.sparkContext

# Creating spark dataframe of input csv file
df = spark.read.csv('hdfs://localhost:9000/Input/input.csv', inferSchema = True, header = True)

# Adding UUID column 'id'
output = df.withColumn("id", monotonically_increasing_id())

# Ordering columns
output_arr = output.select("id", "agecategory", "alcoholdrinking", "asthma", "bmi", "diabetic", "diffwalking", "genhealth", "heartdisease", "kidneydisease", "mentalhealth", "physicalactivity", "physicalhealth", "race", "sex", "skincancer", "sleeptime", "smoking", "stroke")

# Saving data in Cassandra db
output_arr.write.format("org.apache.spark.sql.cassandra").mode('append').options(table="features", keyspace="heartdisease").save()

# Stopping spark
sc.stop()
