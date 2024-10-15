# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Flask (and any other required Python packages)
RUN pip install --no-cache-dir flask

# Expose the port that the Flask app runs on
EXPOSE 5001

# Define environment variable for Flask to run in production mode
ENV FLASK_ENV=production

# Run the app when the container launches
CMD [ "python", "app.py" , "--host", "0.0.0.0", "--port", "5001"]