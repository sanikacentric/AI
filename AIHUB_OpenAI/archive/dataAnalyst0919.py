import streamlit as st
import openai
import logging
import pandas as pd
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

def create_assistant_with_query(file_id, question):
    """Creates an assistant in OpenAI with the uploaded file and code interpreter, processes query in one step."""
    try:
        instructions = (
            f"You are a data analyst. Please analyze the file provided and answer this query: {question}. "
            f"Make sure to run Python code using the Code Interpreter to generate the results, such as summaries, charts, and visualizations. "
            f"Do not return the instructions or code, just execute the code and display the output to the user."
        )

        assistant_response = client.beta.assistants.create(
            instructions=instructions,
            model="gpt-4",
            tools=[{"type": "code_interpreter"}],
            tool_resources={
                "code_interpreter": {
                    "file_ids": [file_id]
                }
            }
        )

        # Extract the assistant ID from the object
        assistant_id = assistant_response.id

        # Display the assistant's response
        st.write(f"Assistant created successfully with ID: {assistant_id}")
        return assistant_response

    except Exception as e:
        st.error(f"Error during assistant creation and querying: {e}")
        logger.error(f"Error during assistant creation and querying: {e}")
        return None

def display_assistant_response(assistant_id):
    """Fetches and displays the assistant's response, including any generated outputs."""
    try:
        # Retrieve the assistant's response
        response = client.beta.assistants.runs.list(assistant_id=assistant_id)

        if response and response.data:
            for run in response.data:
                # Get the results and display them on the page
                if run.status == 'completed':
                    st.write("Assistant's Result:")
                    for step in run.steps:
                        # Display each step's input and output
                        if step.output:
                            st.write(step.output)  # Display the text output
                        if step.chart:
                            st.pyplot(step.chart)  # Display the chart if available

    except Exception as e:
        st.error(f"Error while fetching the assistant's response: {e}")
        logger.error(f"Error while fetching the assistant's response: {e}")

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
                # Create the assistant with the file and code interpreter and process the query in one step
                assistant_response = create_assistant_with_query(file_id, question)
                if assistant_response:
                    # Now display the assistant's result/output
                    display_assistant_response(assistant_response.id)

if __name__ == "__main__":
    data_analysis_assistant()
