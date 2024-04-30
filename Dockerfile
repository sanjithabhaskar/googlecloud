# Use the official Python image as a base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /dash_integration

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask application code to the working directory
COPY . .

# Specify the command to run on container startup
CMD ["python", "app.py"]
