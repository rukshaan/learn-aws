import os
import json
import time
import boto3
import requests
from datetime import datetime
from dotenv import load_dotenv
from pyspark.sql import SparkSession

# Load .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")
print("API_KEY =", API_KEY)
# ================= Spark Session =================
spark = SparkSession.builder.appName("Finance Ingestion Job").getOrCreate()

# ================= AWS Credentials from .env =================
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")


RAW_BUCKET = os.getenv("RAW_BUCKET_NAME")
RAW_PREFIX = os.getenv("RAW_PREFIX")

# Set AWS creds for Spark + boto3
os.environ["AWS_ACCESS_KEY_ID"] = AWS_ACCESS_KEY
os.environ["AWS_SECRET_ACCESS_KEY"] = AWS_SECRET_KEY
os.environ["AWS_DEFAULT_REGION"] = AWS_REGION


# ================= Fetch API Data =================
def fetch_data_from_api(symbols, api_key, retries=3):
    url = f"https://yfapi.net/v6/finance/quote?region=US&lang=en&symbols={','.join(symbols)}"
    headers = {"accept": "application/json", "X-API-KEY": api_key}

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            print("API Status:", response.status_code)

            if response.status_code == 429:
                time.sleep(2 ** attempt)
                continue

            response.raise_for_status()
            return response.json()

        except Exception as e:
            print("API error:", e)

    return None


# ================= Write Spark Data to S3 =================
def write_to_s3_spark(df, bucket, prefix):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = f"s3a://{bucket}/{prefix}/{timestamp}"

    df.write.mode("overwrite").parquet(path)
    print(f"✅ Data written to {path}")


# ================= MAIN =================
if __name__ == "__main__":

    SYMBOLS = ["AAPL", "MSFT", "GOOGL"]

    if not API_KEY:
        raise Exception("API_KEY missing in .env")

    data = fetch_data_from_api(SYMBOLS, API_KEY)

    if data:
        records = data["quoteResponse"]["result"]
        df = spark.createDataFrame(records)

        df.show()
        df.printSchema()

        write_to_s3_spark(df, RAW_BUCKET, RAW_PREFIX)
