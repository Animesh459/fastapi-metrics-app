# app/Dockerfile
# (This file is is located at Metrics-Monitoring-System/app/Dockerfile on your host)

# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster


# Set the working directory in the container to the root directory.
# This is crucial because your 'app' package will be a subdirectory of this WORKDIR,
# allowing Python to find 'app' on its sys.path.
WORKDIR /

# Copy requirements.txt from the build context (which is your host's ./app directory)
# to the root directory in the container.
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy the rest of the application code from the build context (your host's ./app directory)
# into the /app directory inside the container.
# This means:
# - /app/main.py
# - /app/config.py
# - /app/__init__.py (making '/app' a Python package)
# - /app/metrics/, /app/middleware/, /app/routers/
# will all be correctly placed.
COPY . /app

# Expose port 8000 for the FastAPI application
EXPOSE 8000

# Command to run the application.
# Since the WORKDIR is now '/', and your 'app' package is at '/app',
# 'app.main:app' is the correct and explicit way to reference your FastAPI application.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]