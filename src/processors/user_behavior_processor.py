# src/processors/user_behavior_processor.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

def process_user_behavior():
    spark = create_spark_session()
    
    # Define schema for e-commerce data
    schema = StructType([
        StructField("user_id", IntegerType(), True),
        StructField("event_type", StringType(), True),
        StructField("product_id", IntegerType(), True),
        StructField("category", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("session_id", StringType(), True),
        StructField("value", FloatType(), True)
    ])
    
    # Read from Kafka
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "ecommerce") \
        .load()
    
    # Parse JSON data
    parsed_df = df.select(
        from_json(col("value").cast("string"), schema).alias("data")
    ).select("data.*")
    
    # Process user behavior
    processed_df = parsed_df \
        .withWatermark("timestamp", "1 minute") \
        .groupBy(
            window("timestamp", "1 minute"),
            "event_type",
            "category"
        ) \
        .agg(
            count("*").alias("event_count"),
            sum("value").alias("total_value"),
            approx_count_distinct("user_id").alias("unique_users")
        )
    
    # Write to MongoDB
    query = processed_df \
        .writeStream \
        .outputMode("append") \
        .foreachBatch(lambda df, epoch_id: df.write \
            .format("mongo") \
            .option("uri", "mongodb://localhost:27017/streaming_db.user_behavior") \
            .mode("append") \
            .save()) \
        .start()
    
    return query