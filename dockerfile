FROM python:3.11-slim

WORKDIR /app

# Copy all files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir pandas boto3

# Default command runs both scripts
CMD ["sh", "-c", "python simulate_trip_a.py && python compare_trips.py"]
