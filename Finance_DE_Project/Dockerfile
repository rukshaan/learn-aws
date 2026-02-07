# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN pip install boto3 requests

# Copy scripts
COPY spark_scripts.py /app/spark_scripts.py
COPY transform_scripts.py /app/transform_data.py

# Run the main script
CMD ["sh", "-c", "python spark_scripts.py && python transform_data.py"]