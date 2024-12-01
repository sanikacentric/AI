import streamlit as st
import openai
import logging
import pandas as pd
import time
import io

# Initialize the OpenAI API client
from openai import OpenAI

client = OpenAI()
logger = logging.getLogger(__name__)

# Supported file types
SUPPORTED_FILE_TYPES = {
    'csv': 'application/csv',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'json': 'application/json',
    'txt': 'text/plain',
    'pdf': 'application/pdf',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    # Add other supported file types here
}

def read_file(uploaded_file, file_extension):
    """Read and process uploaded files based on their extension."""
    file_processors = {
        'csv': lambda f: pd.read_csv(f),
        'xlsx': lambda f: pd.read_excel(f),
        'json': lambda f: pd.read_json(f),
        'txt': lambda f: f.read().decode('utf-8'),
        # Add more file processing functions here
    }

    # Call the appropriate processing function based on the file extension
    return file_processors.get(file_extension, lambda f: None)(uploaded_file)

def upload_file_to_openai(file_content, file_extension):
    """Uploads the file content to OpenAI and returns the file ID."""
    
    if isinstance(file_content, pd.DataFrame):
        buffer = io.StringIO()
        file_content.to_csv(buffer, index=False)
        buffer.seek(0)
        file_content = buffer.getvalue()

    try:
        # OpenAI expects a binary file-like object, so we convert it here
        file_bytes = io.BytesIO(file_content.encode('utf-8'))
        
        # Upload the file to OpenAI
        uploaded_file = client.files.create(file=file_bytes, purpose='assistants')
        st.success(f"File uploaded to OpenAI with ID: {uploaded_file.id}")
        return uploaded_file.id

    except Exception as e:
        st.error(f"File upload failed: {e}")
        logger.error(f"File upload failed: {e}")
        return None

def create_thread_with_file(file_id, question):
    """Creates a thread in OpenAI with the uploaded file and a question."""
    try:
        # Create a thread and pass the file along with the user message
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": question,
                    "attachments": [
                        {
                            "file_id": file_id,
                            "tools": [{"type": "code_interpreter"}]
                        }
                    ]
                }
            ]
        )

        # Display the raw response for inspection
        st.write("Thread created successfully:", thread)
        
        # Return the thread object
        return thread

    except Exception as e:
        st.error(f"Error during thread creation: {e}")
        logger.error(f"Error during thread creation: {e}")
        return None

def poll_for_thread_results(thread_id):
    """Polls the OpenAI API to check if the thread has completed and retrieves the results."""
    try:
        # Simulate polling by checking for thread updates
        while True:
            runs = client.beta.threads.runs.list(thread_id=thread_id)
            
            # Check if any run has completed
            if runs and len(runs.data) > 0:
                for run in runs.data:
                    if run.status == 'completed':
                        st.write("Assistant's Response is ready.")
                        return run.id
            
            # Wait a few seconds before polling again
            time.sleep(5)
    
    except Exception as e:
        st.error(f"Error while polling for thread results: {e}")
        logger.error(f"Error while polling for thread results: {e}")
        return None

def get_code_interpreter_logs(thread_id, run_id):
    """Fetches the input and output logs of the code interpreter from the run steps."""
    try:
        # List the steps of the run that was executed by the code interpreter
        run_steps = client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run_id)
        
        # Display the logs of the code interpreter
        st.write("Code Interpreter Logs:")
        for step in run_steps:
            st.write(f"Step Input: {step.input}")
            st.write(f"Step Output: {step.output}")
    
    except Exception as e:
        st.error(f"Error while fetching code interpreter logs: {e}")
        logger.error(f"Error while fetching code interpreter logs: {e}")

def data_analysis_assistant():
    st.title("Data Analysis Assistant")

    # File upload widget, supporting various file formats
    uploaded_file = st.file_uploader("Upload your file", type=list(SUPPORTED_FILE_TYPES.keys()))

    if uploaded_file is not None:
        file_name = uploaded_file.name
        file_extension = file_name.split('.')[-1]

        file_content = read_file(uploaded_file, file_extension)
        
        # Display file content or DataFrame directly
        if isinstance(file_content, pd.DataFrame):
            st.dataframe(file_content)
        else:
            st.text_area("File Content", file_content)

        # User input to ask questions about the data
        question = st.text_input("Ask a question about the data:")

        if st.button("Analyze and Download Results"):
            # Upload the file to OpenAI and get the file ID
            file_id = upload_file_to_openai(file_content, file_extension)
            if file_id:
                # Create the thread with the file and question
                thread = create_thread_with_file(file_id, question)
                if thread:
                    # Poll for the results of the thread and get the run_id
                    run_id = poll_for_thread_results(thread.id)
                    
                    # Fetch the Code Interpreter input/output logs
                    if run_id:
                        get_code_interpreter_logs(thread.id, run_id)

if __name__ == "__main__":
    data_analysis_assistant()
