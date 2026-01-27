# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# Removed software-properties-common as it's not needed for basic build tools in this base image
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Expose port 8080
EXPOSE 8080

# Make setup script executable
RUN chmod +x setup.sh

# Start using the setup script
ENTRYPOINT ["./setup.sh"]
