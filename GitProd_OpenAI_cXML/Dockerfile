# Use the Python 3.10 slim base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application into the container
COPY . .

# Expose the default port for Streamlit
EXPOSE 8501

# Define environment variables
ENV OPENAI_API_KEY=your_openai_api_key

# Run the application
CMD ["streamlit", "run", "app.py"]
