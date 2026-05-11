FROM python:3.11-slim

# Install Java (required for PySpark)
RUN apt-get update && apt-get install -y \
    default-jdk \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/default-java

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY extraction/   ./extraction/
COPY transformation/ ./transformation/
COPY sql/          ./sql/
COPY tests/        ./tests/
COPY dags/         ./dags/

CMD ["python", "transformation/transform_spark.py"]
