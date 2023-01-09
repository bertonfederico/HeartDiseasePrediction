import pyspark
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import webbrowser
from pyspark.sql import SparkSession
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.sql.functions import col,isnan,when,count,explode,array,lit
from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression, GBTClassifier
from pyspark.ml.feature import VectorAssembler, MinMaxScaler, StringIndexer, OneHotEncoder
from pyspark2pmml import PMMLBuilder
from openscoring import Openscoring


spark = (
    SparkSession.builder.appName("spark_test")
    .config("spark.jars.packages", "org.jpmml:pmml-sparkml:2.2.0")
    .getOrCreate()
)
javaPmmlBuilderClass = spark.sparkContext._jvm.org.jpmml.sparkml.PMMLBuilder