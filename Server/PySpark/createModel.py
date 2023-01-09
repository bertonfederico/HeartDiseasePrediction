import pkg_resources
#pkg_resources.require("pyspark==3.1.3")
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
# Splitting columns in categorical and continuous
continuousFeatures = ['BMI', 'PhysicalHealth', 'MentalHealth', 'Age', 'SleepTime']
categoricalFeatures = ['Smoking', 'AlcoholDrinking', 'Stroke', 'DiffWalking', 'Sex', 'Race', 'Diabetic', 'PhysicalActivity', 'GenHealth', 'Asthma', 'KidneyDisease', 'SkinCancer']

# Replace age-range with its avg
decodeAgeMap = {'55-59':'57', '80 or older':'80', '65-69':'67', '75-79':'77','40-44':'42','70-74':'72','60-64':'62', '50-54':'52','45-49':'47','18-24':'21','35-39':'37', '30-34':'32','25-29':'27'}
df_chart = df_unbalanced.replace(decodeAgeMap, subset=['AgeCategory'])
df_chart = df_chart.withColumnRenamed("AgeCategory","Age")
df_chart = df_chart.withColumn("Age", col("Age").cast("integer"))
df_pd = df_chart.toPandas()

# Setting Seaborn features
sns.set(font_scale=2)
sns.set_style("darkgrid")

# Continuous features charts
def plotContinuousChart(xLabel):
    fig, ax = plt.subplots(figsize = (18,9))
    sns.kdeplot(df_pd[df_pd["HeartDisease"]=='No'][xLabel], alpha=0.5,fill = True, color="#4285f4", label="No HeartDisease", ax = ax)
    sns.kdeplot(df_pd[df_pd["HeartDisease"]=='Yes'][xLabel], alpha=0.5,fill = True, color="#ea4335", label="HeartDisease", ax = ax)
    ax.set_xlabel(xLabel)
    ax.set_ylabel("Frequency")
    ax.legend(loc='best')
    plt.savefig('../OutputImg/' + xLabel + '.png')
for contFeat in continuousFeatures:
    plotContinuousChart(contFeat)

# Categorical geatures charts
def plotCategoricalChart(xLabel):
    fig, ax = plt.subplots(figsize = (18,9))
    sns.countplot(data=df_pd, y=xLabel, hue="HeartDisease", palette=['#ea4335',"#4285f4"])
    ax.set_xlabel("Count")
    ax.set_ylabel(xLabel)
    ax.legend(['No HeartDisease', 'HeartDisease'], loc='best')
    sns.despine(left=True, bottom=True)
    plt.savefig('../OutputImg/' + xLabel + '.png')
for catFeat in categoricalFeatures:
    plotCategoricalChart(catFeat)

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
for catFeat in categoricalFeatures:
    df_chart = df_chart.withColumn(catFeat + "_dec", col(catFeat).cast("float")).drop(catFeat).withColumnRenamed(catFeat + "_dec", catFeat)
df_pd = df_chart.toPandas()

# Correlation heatmmap
plt.figure(figsize=(18,18))
cor = df_pd.corr()
sns.heatmap(cor, annot=True, cmap=plt.cm.Reds, fmt='.2f')
plt.savefig('../OutputImg/correlation.png')



############################################
###### Balancing unbalanced dataset ########
############ with oversampling #############
############################################
df_size = df_unbalanced.count()

# Undersampling dataframe portion with "HeartDisease" = "Yes"
minor_df = df_unbalanced.filter(col("HeartDisease") == 'Yes')
minor_df_size = minor_df.count()
print(minor_df_size)
minor_ratio = int((df_size/2)/minor_df_size)
a = range(minor_ratio)
oversampled_df = minor_df.withColumn("dummy", explode(array([lit(x) for x in a]))).drop('dummy')

#Oversampling dataframe portion with "HeartDisease" = "No"
major_df = df_unbalanced.filter(col("HeartDisease") == 'No')
major_df_size = df_size-minor_df_size
major_ratio = int(major_df_size/(df_unbalanced.count()/2))
undersampled_df = major_df.sample(False, 1/major_ratio)

unbalancing_ratio = major_df_size/minor_df_size
df = oversampled_df.unionAll(undersampled_df)


############################################
######### Creating ML pipeline #############
############################################
continuousFeatures = ['BMI', 'PhysicalHealth', 'MentalHealth', 'SleepTime']
categoricalFeatures = ['AgeCategory', 'Smoking', 'AlcoholDrinking', 'Stroke', 'DiffWalking', 'Sex', 'Race', 'Diabetic', 'PhysicalActivity', 'GenHealth', 'Asthma', 'KidneyDisease', 'SkinCancer']

diseaseEncoder = StringIndexer(inputCol = "HeartDisease", outputCol = "HeartDisease_encoded")

# Assembler for continuous features: all the continuous features have to be assembled as a vector in the same column to be scaled
continuousAssembler = VectorAssembler(inputCols = continuousFeatures, outputCol = "assembledFeatures")

# SCaler: scales all continuous features (assembled in column 'assembledFeatures') to be in the range [0,1]
continuousScaler = MinMaxScaler(inputCol = "assembledFeatures", outputCol = "normalizedFeatures")

# Indexer and encoder: numerical encoder for categorical features and goal column
categoricalIndexer = [StringIndexer(inputCol = column, outputCol = column + "_indexed").fit(df) for column in categoricalFeatures]
categoricalEncoder = OneHotEncoder(inputCols = [col + '_indexed' for col in categoricalFeatures], outputCols=[col + '_encoded' for col in categoricalFeatures])

# Assembler for all features: all the features are assembled in the 'final_features' column
input = [col + '_encoded' for col in categoricalFeatures]
input.append('normalizedFeatures')
totalAssembler = VectorAssembler(inputCols = input, outputCol = "final_features")

# Logistic regression: suitable for categorical and noncontinuous decisions
regressor = LogisticRegression(featuresCol = "final_features", labelCol = "HeartDisease_encoded")

# Inizializing pipeline ('categoricalIndexer' is already a list, so it must be concatenated with the list of remaining stages)
stages = categoricalIndexer + [diseaseEncoder, categoricalEncoder, continuousAssembler, continuousScaler, totalAssembler, regressor]
pipeline = Pipeline(stages = stages)



############################################
########## training pipeline model #########
############################################
# Splitting dataset into traing and set datasets
train_set, test_set = df.randomSplit([0.7,0.3])

# Model training
pipeline_model = pipeline.fit(train_set)

# Making predictions
predictions = pipeline_model.transform(test_set)

# Accuracy computation
eval = MulticlassClassificationEvaluator(labelCol="HeartDisease_encoded", predictionCol="prediction", metricName="accuracy")
accuracy = eval.evaluate(predictions)

# Training pipeline model with entire dataset
pipeline_model = pipeline.fit(df)



############################################
####### exporting pmml pipeline model ######
############################################
PMMLBuilder(sc, df, pipeline_model).buildFile("HeartDisease.pmml")
os = Openscoring("http://localhost:8080/openscoring")

# Shall be available at http://localhost:8080/openscoring/model/HeartDisease
os.deployFile("HeartDisease", "HeartDisease.pmml")



############################################
############### stopping Spark #############
############################################
sc.stop()



############################################
###### opening statistics client page ######
############################################
webbrowser.open_new_tab('../../Client/homePage.html')



############################################
######## printing info in consolle #########
############################################
print('')
print('')
print('####################################################################################################')
print('####################################################################################################')
print('####################################################################################################')
print('########  --> Unbalancing ratio: %.3f                                                   ##########' %unbalancing_ratio)
print('########  --> Balanced by by keeping the same size of original input dataset              ##########')
print('########  --> Estimator: logistic regression                                              ##########')
print('########  --> Evaluator: MulticlassClassificationEvaluator                                ##########')
print('########  --> Prediction accurancy: %.3f                                                 ##########' %accuracy)
print('########  --> Prediction served on: http://localhost:8080/openscoring/model/HeartDisease  ##########')
print('########  --> Client page: ../../Client/homePage.html                                     ##########')
print('####################################################################################################')
print('####################################################################################################')
print('####################################################################################################')
print('')
print('')