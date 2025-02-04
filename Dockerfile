# Use Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . .

# Expose the application port (if it's a web app or similar)
EXPOSE 80

# Command to run the app
CMD ["python", "app.py"]
