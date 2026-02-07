# ================= LOAD ENV VARIABLES =================
from dotenv import load_dotenv
load_dotenv()

import boto3
import json
import os
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError


# ================= READ LATEST JSON FILE FROM S3 =================
def read_from_s3(bucket_name, prefix):
    try:
        s3 = boto3.client("s3")
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        # Check if files exist
        if "Contents" not in response:
            print(f"❌ No files found in bucket '{bucket_name}' with prefix '{prefix}'")
            return None

        # Filter only JSON files (ignore folders like raw/)
        json_files = [obj for obj in response["Contents"] if obj["Key"].endswith(".json")]

        if not json_files:
            print("❌ No JSON files found in raw folder")
            return None

        # Get latest file
        latest_file = sorted(json_files, key=lambda x: x["LastModified"], reverse=True)[0]["Key"]
        print(f"Latest file found: {latest_file}")

        # Read file content
        file_obj = s3.get_object(Bucket=bucket_name, Key=latest_file)
        file_content = file_obj["Body"].read().decode("utf-8")

        return json.loads(file_content)

    except Exception as e:
        print(f"Error reading from S3: {e}")
        return None


# ================= TRANSFORM DATA =================
def transform_data(data):
    transformed_data = []

    # Validate input
    if not data or "quoteResponse" not in data:
        print("❌ Invalid or empty data received")
        return transformed_data

    for stock in data["quoteResponse"]["result"]:
        transformed_stock = {
            "company_id": stock.get("symbol"),
            "company_name": stock.get("longName"),
            "currency": stock.get("currency"),
            "current_price": stock.get("regularMarketPrice"),
            "day_low": stock.get("regularMarketDayLow"),
            "day_high": stock.get("regularMarketDayHigh"),
        }
        transformed_data.append(transformed_stock)

    print(f"✅ Transformed {len(transformed_data)} records")
    return transformed_data


# ================= WRITE TRANSFORMED DATA TO S3 =================
def write_to_s3(bucket_name, data, key_prefix):
    try:
        s3 = boto3.client("s3")

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        key = f"{key_prefix}/{timestamp}.json"

        s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=json.dumps(data, indent=4),
            ContentType="application/json"
        )

        print(f"✅ Data written to s3://{bucket_name}/{key}")

    except Exception as e:
        print(f"❌ Error writing to S3: {e}")
        raise


# ================= MAIN EXECUTION =================
if __name__ == "__main__":
    # Load environment variables
    RAW_BUCKET = os.getenv("RAW_BUCKET_NAME")
    TRANSFORMED_BUCKET = os.getenv("TRANSFORMED_BUCKET_NAME")
    RAW_PREFIX = os.getenv("RAW_PREFIX", "raw/")
    TRANSFORMED_PREFIX = os.getenv("TRANSFORMED_PREFIX", "transformed/")

    try:
        print("🚀 Starting ETL Pipeline...")

        # Step 1: Read raw data
        raw_data = read_from_s3(RAW_BUCKET, RAW_PREFIX)
        if not raw_data:
            raise ValueError("No raw data found in S3.")

        # Step 2: Transform data
        transformed_data = transform_data(raw_data)
        if not transformed_data:
            raise ValueError("Transformation returned empty data.")

        # Step 3: Write transformed data
        write_to_s3(TRANSFORMED_BUCKET, transformed_data, TRANSFORMED_PREFIX)

        print("🎉 ETL Pipeline Completed Successfully!")

    except NoCredentialsError:
        print("❌ AWS credentials not found.")
    except ClientError as e:
        print(f"❌ AWS Client Error: {e}")
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
