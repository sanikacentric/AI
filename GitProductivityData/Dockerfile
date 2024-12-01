FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application into the container
COPY . .

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Define environment variables

ENV GITHUB_TOKEN=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
ENV OPENAI_API_KEY=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


# Run the application
CMD ["streamlit", "run", "app.py"]
