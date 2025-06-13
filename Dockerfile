# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the default port (it's good practice to expose the default even if configurable)
EXPOSE 8080

# Define environment variables (only FLASK_APP and FLASK_RUN_HOST needed now)
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the Flask application. It will pick up the PORT env var.
CMD ["flask", "run", "--port", "8080"]
