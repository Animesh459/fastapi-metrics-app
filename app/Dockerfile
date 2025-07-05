# app/Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
# Copy only requirements.txt first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 8000 for the FastAPI application
EXPOSE 8000

# Command to run the application
# --host 0.0.0.0 makes the server accessible from outside the container
# --port 8000 specifies the port
# --reload enables auto-reloading on code changes (useful for development)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
