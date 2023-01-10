import pkg_resources
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

############################################
# Inizializing Spark context and Dataframe #
############################################
# Creating spark session and context
spark=SparkSession.builder.appName('HeartDiseasePrediction').getOrCreate()
sc = spark.sparkContext

# Creating spark dataframe of input csv file
df_unbalanced = spark.read.csv('hdfs://localhost:9000/Input/input.csv', inferSchema = True, header = True)



############################################
###### Anlizing dataset with charts ########
############################################
# Setting Seaborn features
sns.set(font_scale=2)
sns.set_style("darkgrid")

# Replace age-range with its avg
decodeAgeMap = {'55-59':'57', '80 or older':'80', '65-69':'67', '75-79':'77','40-44':'42','70-74':'72','60-64':'62', '50-54':'52','45-49':'47','18-24':'21','35-39':'37', '30-34':'32','25-29':'27'}
df_chart = df_unbalanced.replace(decodeAgeMap, subset=['AgeCategory'])
df_chart = df_chart.withColumnRenamed("AgeCategory","Age")
df_chart = df_chart.withColumn("Age", col("Age").cast("integer"))
df_pd = df_chart.toPandas()

# Splitting columns in categorical and continuous
continuousFeatures = ['BMI', 'PhysicalHealth', 'MentalHealth', 'Age', 'SleepTime']
categoricalFeatures = ['Smoking', 'AlcoholDrinking', 'Stroke', 'DiffWalking', 'Sex', 'PhysicalActivity', 'GenHealth', 'Asthma', 'KidneyDisease', 'SkinCancer']
categoricalFeaturesToChange = ['Race', 'Diabetic']

# Percentage pie charts
def plotDistributionCategoricalChart(name_feature, indexesToChange, labelsToChange):
    fig,ax = plt.subplots(figsize=(8,8))
    labels = df_pd[name_feature].unique()
    ax.pie(df_pd[name_feature].value_counts(), autopct='%1.1f%%', startangle=90)
    plt.title("Distribution of " + name_feature + " responsese")
    i = 0
    for index in indexesToChange:
        labels[index] = labelsToChange[i]
        i = i+1
    plt.legend(labels, loc="best")
    plt.tight_layout()
    plt.savefig('../OutputImg/Pie/' + name_feature + '.png', transparent=True)
for catFeat in (categoricalFeatures + ['HeartDisease']):
    plotDistributionCategoricalChart(catFeat, [], [])
plotDistributionCategoricalChart('Race', [3], ['Indian/Alaskan'])
plotDistributionCategoricalChart('Diabetic', [2, 3], ['Borderline', 'Pregnancy'])

# Continuous features charts
def plotContinuousChart(xLabel):
    fig, ax = plt.subplots(figsize = (25,9))
    sns.kdeplot(df_pd[df_pd["HeartDisease"]=='No'][xLabel], alpha=0.5,fill = True, color="#4285f4", label="No HeartDisease", ax = ax)
    sns.kdeplot(df_pd[df_pd["HeartDisease"]=='Yes'][xLabel], alpha=0.5,fill = True, color="#ea4335", label="HeartDisease", ax = ax)
    sns.kdeplot(df_pd[xLabel], alpha=0.5,fill = True, color="#008000", label="Total", ax = ax)
    ax.set_xlabel(xLabel)
    ax.set_ylabel("Number among respondents")
    ax.legend(loc='best')
    plt.savefig('../OutputImg/Rel/' + xLabel + '.png', transparent=True)
for contFeat in continuousFeatures:
    plotContinuousChart(contFeat)

# Categorical geatures charts
def plotCategoricalChart(xLabel, indexesToChange, labelsToChange):
    fig, ax = plt.subplots(figsize = (20,9))
    sns.countplot(data=df_pd, y=xLabel, hue="HeartDisease", palette=['#ea4335',"#4285f4"])
    ax.set_xlabel("Number among respondents")
    ax.legend(['No HeartDisease', 'HeartDisease'], loc='best')
    sns.despine(left=True, bottom=True)
    labels = [item.get_text() for item in ax.get_yticklabels()]
    i = 0
    for index in indexesToChange:
        labels[index] = labelsToChange[i]
        i = i+1
    ax.set_yticklabels(labels)
    plt.title("Number of 'Heart disease'and 'No heart disease' for each category")
    plt.subplots_adjust(left=0.12, right=0.98, top=0.9, bottom=0.1)
    plt.savefig('../OutputImg/Rel/' + xLabel + '.png', transparent=True)
for catFeat in categoricalFeatures:
    plotCategoricalChart(catFeat, [], [])
plotCategoricalChart('Race', [3], ['Indian/Alaskan'])
plotCategoricalChart('Diabetic', [2, 3], ['Borderline', 'Pregnancy'])

# Changing all categorial features to continuous for correlation heatmmap
decodeYesNoMap = {'Yes': '1', 'No': '0'}
decodeGenHealthMap = {'Excellent': '1', 'Fair': '0.25', 'Good': '0.5', 'Poor': '0', 'Very good': '0.75'}
decodeDiabeticMap = {'No, borderline diabetes': '0.5', 'Yes (during pregnancy)': '0.5'}
decodeSexMap = {'Female': '1', 'Male': '0'}
decodeRaceMap = {'American Indian/Alaskan Native': '0.17', 'Asian': '0.34', 'Black': '0.5', 'Hispanic': '0.67', 'Other': '0.84', 'White': '1'}
totalDecodeMap = decodeYesNoMap
totalDecodeMap.update(decodeGenHealthMap)
totalDecodeMap.update(decodeDiabeticMap)
totalDecodeMap.update(decodeSexMap)
totalDecodeMap.update(decodeRaceMap)
df_chart = df_chart.replace(totalDecodeMap)
for catFeat in (categoricalFeatures + ['HeartDisease'] + categoricalFeaturesToChange):
    df_chart = df_chart.withColumn(catFeat + "_dec", col(catFeat).cast("float")).drop(catFeat).withColumnRenamed(catFeat + "_dec", catFeat)
df_pd = df_chart.toPandas()
df_chart.show(10)

# Correlation heatmmap
plt.figure(figsize=(25,18))
cor = df_pd.corr()
chart = sns.heatmap(cor, annot=True, cmap=plt.cm.Reds, fmt='.2f')
chart.set_xticklabels(chart.get_xticklabels(), rotation=45, horizontalalignment='right')
chart.set_yticklabels(chart.get_yticklabels(), rotation=45, verticalalignment='top')
plt.subplots_adjust(left=0.12, right=0.98, top=0.95, bottom=0.15)
plt.savefig('../OutputImg/correlation.png', transparent=True)



############################################
############### stopping Spark #############
############################################
sc.stop()

