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
from sklearn import metrics

############################################
# Inizializing Spark context and Dataframe #
############################################
# Creating spark session and context
spark=SparkSession.builder.appName('HeartDiseasePrediction').getOrCreate()
sc = spark.sparkContext

# Creating spark dataframe from Cassandra db
df_unbalanced = spark.read.format("org.apache.spark.sql.cassandra").options(table="features", keyspace="heartdisease").load()
df_unbalanced = df_unbalanced.drop("id")



############################################
###### Anlizing dataset with charts ########
############################################
# Setting Seaborn features
sns.set(font_scale=2)
sns.set_style("darkgrid")

# Replace age-range with its avg
decodeageMap = {'55-59':'57', '80 or older':'80', '65-69':'67', '75-79':'77','40-44':'42','70-74':'72','60-64':'62', '50-54':'52','45-49':'47','18-24':'21','35-39':'37', '30-34':'32','25-29':'27'}
df_chart = df_unbalanced.replace(decodeageMap, subset=['agecategory'])
df_chart = df_chart.withColumnRenamed("agecategory","age")
df_chart = df_chart.withColumn("age", col("age").cast("integer"))
df_pd = df_chart.toPandas()

# Splitting columns in categorical and continuous
continuousFeatures = ['bmi', 'physicalhealth', 'mentalhealth', 'age', 'sleeptime']
categoricalFeatures = ['smoking', 'alcoholdrinking', 'stroke', 'diffwalking', 'sex', 'physicalactivity', 'genhealth', 'asthma', 'kidneydisease', 'skincancer']
categoricalFeaturesToChange = ['race', 'diabetic']

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
    plt.savefig('../outputImg/pIe/' + name_feature + '.png', transparent=True)
for catFeat in (categoricalFeatures + ['heartdisease']):
    plotDistributionCategoricalChart(catFeat, [], [])
plotDistributionCategoricalChart('race', [3], ['Indian/Alaskan'])
plotDistributionCategoricalChart('diabetic', [2, 3], ['Borderline', 'Pregnancy'])

# Continuous features charts
def plotContinuousChart(xLabel):
    fig, ax = plt.subplots(figsize = (25,9))
    sns.kdeplot(df_pd[df_pd["heartdisease"]=='No'][xLabel], alpha=0.5,fill = True, color="#4285f4", label="No HeartDisease", ax = ax)
    sns.kdeplot(df_pd[df_pd["heartdisease"]=='Yes'][xLabel], alpha=0.5,fill = True, color="#ea4335", label="HeartDisease", ax = ax)
    sns.kdeplot(df_pd[xLabel], alpha=0.5,fill = True, color="#008000", label="Total", ax = ax)
    ax.set_xlabel(xLabel)
    ax.set_ylabel("Number among respondents")
    ax.legend(loc='best')
    plt.savefig('../outputImg/rel/' + xLabel + '.png', transparent=True)
for contFeat in continuousFeatures:
    plotContinuousChart(contFeat)

# Categorical features charts
def plotCategoricalChart(xLabel, indexesToChange, labelsToChange):
    fig, ax = plt.subplots(figsize = (20,9))
    sns.countplot(data=df_pd, y=xLabel, hue="heartdisease", palette=['#ea4335',"#4285f4"])
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
    plt.savefig('../outputImg/rel/' + xLabel + '.png', transparent=True)
for catFeat in categoricalFeatures:
    plotCategoricalChart(catFeat, [], [])
plotCategoricalChart('race', [3], ['Indian/Alaskan'])
plotCategoricalChart('diabetic', [2, 3], ['Borderline', 'Pregnancy'])

# Changing all categorial features to continuous for correlation heatmmap
decodeYesNoMap = {'Yes': '1', 'No': '0'}
decodegenhealthMap = {'Excellent': '1', 'Fair': '0.25', 'Good': '0.5', 'Poor': '0', 'Very good': '0.75'}
decodeDiabeticMap = {'No, borderline diabetes': '0.5', 'Yes (during pregnancy)': '0.5'}
decodesexMap = {'Female': '1', 'Male': '0'}
decodeRaceMap = {'American Indian/Alaskan Native': '0.17', 'Asian': '0.34', 'Black': '0.5', 'Hispanic': '0.67', 'Other': '0.84', 'White': '1'}
totalDecodeMap = decodeYesNoMap
totalDecodeMap.update(decodegenhealthMap)
totalDecodeMap.update(decodeDiabeticMap)
totalDecodeMap.update(decodesexMap)
totalDecodeMap.update(decodeRaceMap)
df_chart = df_chart.replace(totalDecodeMap)
for catFeat in (categoricalFeatures + ['heartdisease'] + categoricalFeaturesToChange):
    df_chart = df_chart.withColumn(catFeat + "_dec", col(catFeat).cast("float")).drop(catFeat).withColumnRenamed(catFeat + "_dec", catFeat)
df_pd = df_chart.toPandas()

# Correlation heatmmap
plt.figure(figsize=(25,18))
cor = df_pd.corr()
chart = sns.heatmap(cor, annot=True, cmap=plt.cm.Reds, fmt='.2f')
chart.set_xticklabels(chart.get_xticklabels(), rotation=45, horizontalalignment='right')
chart.set_yticklabels(chart.get_yticklabels(), rotation=45, verticalalignment='top')
plt.subplots_adjust(left=0.12, right=0.98, top=0.95, bottom=0.15)
plt.savefig('../outputImg/correlation.png', transparent=True)



############################################
###### Balancing unbalanced dataset ########
############################################
df_size = df_unbalanced.count()

# Undersampling dataframe portion with "heartdisease" = "Yes"
minor_df = df_unbalanced.filter(col("heartdisease") == 'Yes')
minor_df_size = minor_df.count()
print(minor_df_size)
minor_ratio = int((df_size/2)/minor_df_size)
a = range(minor_ratio)
oversampled_df = minor_df.withColumn("dummy", explode(array([lit(x) for x in a]))).drop('dummy')

# Oversampling dataframe portion with "heartdisease" = "No"
major_df = df_unbalanced.filter(col("heartdisease") == 'No')
major_df_size = df_size-minor_df_size
major_ratio = int(major_df_size/(df_unbalanced.count()/2))
undersampled_df = major_df.sample(False, 1/major_ratio)

# Merging undersampled and oversampled dataframe
unbalancing_ratio = major_df_size/minor_df_size
df = oversampled_df.unionAll(undersampled_df)


############################################
######### Creating ML pipeline #############
############################################
continuousFeatures = ['bmi', 'physicalhealth', 'mentalhealth', 'sleeptime']
categoricalFeatures = ['agecategory', 'smoking', 'alcoholdrinking', 'stroke', 'diffwalking', 'sex', 'race', 'diabetic', 'physicalactivity', 'genhealth', 'asthma', 'kidneydisease', 'skincancer']

# Indexer to change heartdisease column type from string to numerical
diseaseEncoder = StringIndexer(inputCol = "heartdisease", outputCol = "heartdisease_encoded")

# Assembler for continuous features: all the continuous features have to be assembled as a vector in the same column to be scaled
continuousAssembler = VectorAssembler(inputCols = continuousFeatures, outputCol = "assembledFeatures")

# Scaler: scales all continuous features (assembled in column 'assembledFeatures') to be in the range [0,1]
continuousScaler = MinMaxScaler(inputCol = "assembledFeatures", outputCol = "normalizedFeatures")

# Indexer and encoder: numerical encoder for categorical features and goal column
categoricalIndexer = [StringIndexer(inputCol = column, outputCol = column + "_indexed").fit(df) for column in categoricalFeatures]
categoricalEncoder = OneHotEncoder(inputCols = [col + '_indexed' for col in categoricalFeatures], outputCols=[col + '_encoded' for col in categoricalFeatures])

# Assembler for all features: all the features are assembled in the 'final_features' column
input = [col + '_encoded' for col in categoricalFeatures]
input.append('normalizedFeatures')
totalAssembler = VectorAssembler(inputCols = input, outputCol = "final_features")

# Logistic regression: suitable for categorical and noncontinuous decisions
regressor = LogisticRegression(featuresCol = "final_features", labelCol = "heartdisease_encoded")

# Inizializing pipeline ('categoricalIndexer' is already a list, so it must be concatenated with the list of remaining stages)
stages = categoricalIndexer + [diseaseEncoder, categoricalEncoder, continuousAssembler, continuousScaler, totalAssembler, regressor]
pipeline = Pipeline(stages = stages)



############################################
########## training pipeline model #########
############################################
# Splitting dataset into traing and set datasets
train_set_un, test_set_un = df.randomSplit([0.7,0.3])
df_persist = df.persist()
train_set = train_set_un.persist()
test_set = train_set_un.persist()

# Model training
pipeline_model = pipeline.fit(train_set)

# Making predictions
predictions = pipeline_model.transform(test_set)

# Printing confusion matrix
sns.set(font_scale=3)
y_true = predictions.select(['heartdisease_encoded']).collect()
y_pred = predictions.select(['prediction']).collect()
confusion_matrix = metrics.confusion_matrix(y_true, y_pred)
plt.figure(figsize=(15, 10))
sns.heatmap(confusion_matrix, xticklabels=['No', 'Yes'], yticklabels=['No', 'Yes'], annot=True, cmap=plt.cm.Blues, fmt='d')
plt.xlabel('Predicted values')
plt.ylabel('Real values')
plt.subplots_adjust(top=0.96, bottom=0.15)
plt.savefig('../outputImg/confusion.png', transparent=True)

# Accuracy computation
eval = MulticlassClassificationEvaluator(labelCol="heartdisease_encoded", predictionCol="prediction", metricName="accuracy")
accuracy = eval.evaluate(predictions)

# Training pipeline model with entire dataset
pipeline_model = pipeline.fit(df_persist)



############################################
####### exporting pmml pipeline model ######
############################################
PMMLBuilder(sc, df_persist, pipeline_model).buildFile("../outputModel/HeartDisease.pmml")
os = Openscoring("http://localhost:8080/openscoring")

# Shall be available at http://localhost:8080/openscoring/model/HeartDisease
os.deployFile("HeartDisease", "../outputModel/HeartDisease.pmml")



############################################
############### stopping Spark #############
############################################
sc.stop()



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
