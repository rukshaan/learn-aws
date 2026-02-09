FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir boto3 requests

# Copy scripts
COPY spark_script.py /app/spark_script.py
COPY transform_scripts.py /app/transform_data.py

# Run the main script
CMD ["sh", "-c", "python spark_script.py && python transform_data.py"]
