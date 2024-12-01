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
        # Create an assistant with the question and file, with clearer instructions
        instructions = (
            f"You are an expert Data Scientist that is great at analyzing datasets. You are a data analyst. You will respond to this query: {question}."
            f"You are Pro in Python Programming."
            f"You specialize in analyzing datasets and producing Visualizations."
            f"Goal: Your main Goal is to help business users explore their data and get answers and insights."
            f"Steps: 1.The user will upload file in various formats, such as Excel,Text, CSV, or PDF files. 2. Greet the User. 3. If they have specific questions about the data, please use Code Interpreter to write python code to answer the question."
            f"4.Please use Code Interpreter to do EDA(exploratory data analysis)on dataset in python. But tell users you are goin to explore the data and look for insights, since most will not know what EDA means."
            f"5.Produce intriguing visualizations that a business user can understand.Explain each plot that you show.After everything you analyze or visualize, please tell user that they need to verif the output"
            f"Your task is to analyze the data, create summaries, and generate visualizations (such as bar charts, pie charts, etc.) "
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

        # Display the assistant's response
        st.write("Assistant's Response:", assistant_response)

        # Return the assistant ID for further actions (e.g., downloads)
        return assistant_response.id

    except Exception as e:
        st.error(f"Error during assistant creation and querying: {e}")
        logger.error(f"Error during assistant creation and querying: {e}")
        return None


def download_file(file_id):
    """Downloads the generated file from OpenAI using the file ID and saves it locally."""
    try:
        # Use OpenAI API to download the file using the exact function you provided
        image_data = client.files.content(file_id)
        image_data_bytes = image_data.read()

        # Save as a file (adjust file name and format as needed)
        file_path = f"./my-image-{file_id}.png"
        with open(file_path, "wb") as file:
            file.write(image_data_bytes)

        st.success(f"File saved as {file_path}")

    except Exception as e:
        st.error(f"File download failed: {e}")
        logger.error(f"File download failed: {e}")

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
                assistant_id = create_assistant_with_query(file_id, question)
                if assistant_id:
                    # Now you can use assistant_id for further actions, like downloading generated files.
                    st.success(f"Assistant ID: {assistant_id} - Processing complete. Check the assistant's response.")

if __name__ == "__main__":
    data_analysis_assistant()
