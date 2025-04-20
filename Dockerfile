# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that might be needed (optional, but sometimes helpful)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Copy only requirements.txt first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
# This includes main.py, the app/ directory, and the src/ directory
COPY . .

# Expose the port the app runs on
# This should match the port uvicorn is configured to use in main.py
EXPOSE 8000

# Define the command to run the application
# Use uvicorn directly. Ensure host is 0.0.0.0 to accept connections from outside the container.
# Use the app object from main.py directly
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
