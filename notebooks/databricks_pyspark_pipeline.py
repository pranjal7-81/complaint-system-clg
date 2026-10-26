# Databricks notebook source
# MAGIC %md
# MAGIC # Customer Complaint Intelligence System - Cloud Big Data Pipeline
# MAGIC ### Distributed Data Ingestion, PySpark NLP Feature Engineering & Multi-Model MLlib Classification
# MAGIC 
# MAGIC **Technologies Integrated:**
# MAGIC * **Apache Spark / PySpark (MLlib)**: Distributed Pipeline, Tokenizer, StopWordsRemover, HashingTF, IDF, VectorAssembler
# MAGIC * **Databricks Cloud Platform**: Distributed cluster orchestration & Delta Lake integration
# MAGIC * **5 PySpark MLlib Classifiers**: LogisticRegression, NaiveBayes, RandomForestClassifier, DecisionTreeClassifier, GBT/OneVsRest
# MAGIC * **Spark SQL & Hive Warehouse**: OLAP aggregations, window functions, and analytics

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. SparkSession Initialization & Data Ingestion

# COMMAND ----------
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, regexp_replace, length, count, when, avg, round
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF, StringIndexer
from pyspark.ml.classification import (
    LogisticRegression,
    NaiveBayes,
    RandomForestClassifier,
    DecisionTreeClassifier,
    OneVsRest
)
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

# Initialize SparkSession with Delta Lake & Hive support
spark = SparkSession.builder \
    .appName("ComplaintIntelligence_Databricks_Pipeline") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

print(f"Spark Version: {spark.version}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Load Complaint Dataset into Spark DataFrame

# COMMAND ----------
# In Databricks, read from DBFS or Cloud Object Storage (S3 / Azure ADLS / GCS)
raw_df = spark.read.csv("data/processed/cleaned_complaints.csv", header=True, inferSchema=True)
raw_df.printSchema()
raw_df.show(5, truncate=50)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Distributed PySpark NLP Preprocessing & Feature Engineering Pipeline

# COMMAND ----------
# Text normalization in PySpark
cleaned_spark_df = raw_df \
    .withColumn("clean_text", lower(col("text"))) \
    .withColumn("clean_text", regexp_replace(col("clean_text"), "[^a-zA-Z0-9\\s]", " ")) \
    .filter(length(col("clean_text")) > 5)

# 1. Label Indexing: Map text categories to numeric labels
label_indexer = StringIndexer(inputCol="category", outputCol="label", handleInvalid="skip")

# 2. Tokenizer: Split complaint text into words
tokenizer = Tokenizer(inputCol="clean_text", outputCol="words")

# 3. StopWordsRemover: Filter common English stop words
stopwords_remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")

# 4. HashingTF: Term frequency feature mapping
hashing_tf = HashingTF(inputCol="filtered_words", outputCol="raw_features", numFeatures=5000)

# 5. IDF: Inverse Document Frequency weighting
idf = IDF(inputCol="raw_features", outputCol="features")

# Compose Feature Engineering Pipeline
feature_pipeline = Pipeline(stages=[label_indexer, tokenizer, stopwords_remover, hashing_tf, idf])
feature_model = feature_pipeline.fit(cleaned_spark_df)
dataset_vectorized = feature_model.transform(cleaned_spark_df)

# Train/Test 80/20 Split
train_spark, test_spark = dataset_vectorized.randomSplit([0.8, 0.2], seed=42)
print(f"Train samples: {train_spark.count()} | Test samples: {test_spark.count()}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. PySpark MLlib Multi-Model Training & Evaluation (5 Models)

# COMMAND ----------
evaluator_acc = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
evaluator_f1 = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="f1")
evaluator_prec = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="weightedPrecision")
evaluator_rec = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="weightedRecall")

models = {
    "PySpark Logistic Regression": LogisticRegression(featuresCol="features", labelCol="label", maxIter=50),
    "PySpark Naive Bayes": NaiveBayes(featuresCol="features", labelCol="label", modelType="multinomial"),
    "PySpark Random Forest": RandomForestClassifier(featuresCol="features", labelCol="label", numTrees=30, maxDepth=10),
    "PySpark Decision Tree": DecisionTreeClassifier(featuresCol="features", labelCol="label", maxDepth=12),
}

results = []
for name, clf in models.items():
    print(f"Training {name}...")
    model_fit = clf.fit(train_spark)
    preds = model_fit.transform(test_spark)
    
    acc = evaluator_acc.evaluate(preds)
    f1 = evaluator_f1.evaluate(preds)
    prec = evaluator_prec.evaluate(preds)
    rec = evaluator_rec.evaluate(preds)
    
    results.append({
        "Model": name,
        "Accuracy": round(acc * 100, 2),
        "Weighted F1": round(f1, 4),
        "Precision": round(prec, 4),
        "Recall": round(rec, 4)
    })
    print(f"  -> Accuracy: {acc*100:.2f}% | F1: {f1:.4f}")

# Convert results to Spark DataFrame for display
spark.createDataFrame(results).show(truncate=False)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5. Spark SQL Analytics & Delta Lake Storage

# COMMAND ----------
# Register temporary view for Spark SQL OLAP queries
cleaned_spark_df.createOrReplaceTempView("complaints_lake")

# High-priority escalation query
spark.sql("""
    SELECT 
        department,
        priority,
        COUNT(*) AS total_tickets
    FROM complaints_lake
    GROUP BY department, priority
    ORDER BY total_tickets DESC
""").show(10)
