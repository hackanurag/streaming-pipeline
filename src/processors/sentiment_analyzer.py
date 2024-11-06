# src/processors/sentiment_analyzer.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from textblob import TextBlob

def create_spark_session():
    return SparkSession.builder \
        .appName("SentimentAnalysis") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0") \
        .getOrCreate()

def process_social_media_stream():
    spark = create_spark_session()
    
    # Define schema for social media data
    schema = StructType([
        StructField("platform", StringType(), True),
        StructField("user_id", IntegerType(), True),
        StructField("text", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("engagement", IntegerType(), True),
        StructField("sentiment_score", FloatType(), True)
    ])
    
    # Read from Kafka
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "social_media") \
        .load()
    
    # Parse JSON data
    parsed_df = df.select(
        from_json(col("value").cast("string"), schema).alias("data")
    ).select("data.*")
    
    # Process and analyze sentiment
    processed_df = parsed_df \
        .withWatermark("timestamp", "1 minute") \
        .groupBy(
            window("timestamp", "1 minute"),
            "platform"
        ) \
        .agg(
            avg("sentiment_score").alias("avg_sentiment"),
            count("*").alias("post_count")
        )
    
    # Write to PostgreSQL
    query = processed_df \
        .writeStream \
        .outputMode("append") \
        .foreachBatch(lambda df, epoch_id: df.write \
            .format("jdbc") \
            .option("url", "jdbc:postgresql://localhost:5432/streaming_db") \
            .option("dbtable", "sentiment_analysis") \
            .option("user", "admin") \
            .option("password", "admin123") \
            .mode("append") \
            .save()) \
        .start()
    
    return query