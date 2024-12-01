# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables to prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy the .env file into the container
COPY .env .

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    graphviz \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port that Streamlit uses
EXPOSE 8501

# Define default environment variables (can be overridden at runtime)
# It's recommended to pass sensitive keys like API keys via Docker run commands or secrets
# Example: --env OPENAI_API_KEY=your_key
ENV OPENAI_API_KEY=your_openai_api_key

# Run the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
