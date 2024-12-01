
import streamlit as st
import openai
import logging
import pandas as pd
import io

# Initialize the OpenAI API client
client = openai
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

def ask_openai_to_analyze(file_id, question):
    """Passes data to OpenAI for deeper insights and reasoning based on user query."""
    try:
        # Create an assistant with the uploaded file and user question
        assistant = client.beta.assistants.create(
            instructions=f"Analyze the dataset and answer: '{question}'",
            model="gpt-4",
            tools=[{"type": "code_interpreter"}],
            tool_resources={"code_interpreter": {"file_ids": [file_id]}}
        )

        # Get and display the response from the assistant
        #response = assistant.choices[0].message['content']
        #st.write("Assistant Response:", response)
        st.write(assistant)
        
    except Exception as e:
        st.error(f"Error during assistant response retrieval: {e}")
        logger.error(f"Error during assistant response retrieval: {e}")

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

        if st.button("Ask OpenAI"):
            # Upload the file to OpenAI and get the file ID
            file_id = upload_file_to_openai(file_content, file_extension)
            if file_id:
                ask_openai_to_analyze(file_id, question)

if __name__ == "__main__":
    data_analysis_assistant()
