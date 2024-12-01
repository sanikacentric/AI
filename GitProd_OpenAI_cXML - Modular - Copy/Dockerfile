# Use the Python 3.10 slim base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the secrets.toml file into the container
COPY .streamlit/secrets.toml /app/.streamlit/secrets.toml


# Copy the entire application, including the modules folder, into the container
COPY . .

# Ensure that the modules directory and all other directories are included
RUN mkdir -p modules && touch modules/__init__.py

# Expose the default port for Streamlit
EXPOSE 8501

# Define environment variables
ENV OPENAI_API_KEY=your_openai_api_key

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
