# Start from Python base image for AMD64
FROM --platform=linux/amd64 python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy only requirements first for faster rebuilds
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project into container
COPY . .

# Run the processing script on container start
CMD ["python", "main.py"]