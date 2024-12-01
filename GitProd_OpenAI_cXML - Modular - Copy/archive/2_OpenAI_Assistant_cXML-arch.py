import os
import streamlit as st
import xml.etree.ElementTree as ET
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
import openai
import json
import xml.etree.ElementTree as ET
import streamlit as st
import re



#######################
# Page configuration
st.set_page_config(
    page_title="cXML Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded")


# Initialize OpenAI components using LangChain
openai_api_key = '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'
openai.api_key = openai_api_key
client = openai

# Initialize OpenAI components using LangChain
#llm = ChatOpenAI(openai_api_key='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', model="gpt-4o-mini")
#embedding_model = OpenAIEmbeddings(openai_api_key='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')


# Custom CSS to center the title
st.markdown("""
<style>
.reportview-container .main .block-container{
    padding-top: 2rem;
}
h1 {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# Streamlit App Title
st.title("Chat with cXML using AI")

# Columns Setup
#col = st.columns((2, 4, 2), gap='medium')

# Upload multiple cXML files
uploaded_files = st.file_uploader("Upload cXML files", type="xml", accept_multiple_files=True)

# Function to sanitize and clean JSON content
def sanitize_json_string(json_string):
    # Replace unescaped newlines or other control characters
    sanitized_string = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_string)
    return sanitized_string

# Function to recursively parse an XML element, capturing attributes, text, and children
def recursive_parse_xml(element):
    parsed_dict = {}

    # Capture the element's attributes, if any
    if element.attrib:
        parsed_dict['@attributes'] = element.attrib

    # Capture the element's text content, if any
    if element.text and element.text.strip():
        parsed_dict['#text'] = element.text.strip()

    # Recursively process child elements
    for child in element:
        child_parsed = recursive_parse_xml(child)
        # If the child tag already exists, make it a list (to handle multiple same tags)
        if child.tag in parsed_dict:
            if isinstance(parsed_dict[child.tag], list):
                parsed_dict[child.tag].append(child_parsed)
            else:
                parsed_dict[child.tag] = [parsed_dict[child.tag], child_parsed]
        else:
            parsed_dict[child.tag] = child_parsed

    return parsed_dict

# Function to parse and extract cXML data and other payload fields
def parse_cxml(file):
    try:
        # Read the file content
        file_content = file.read().decode('utf-8')

        # Sanitize the JSON string to remove invalid control characters
        sanitized_content = sanitize_json_string(file_content)

        # Parse the sanitized JSON content
        json_data = json.loads(sanitized_content)

        # Create a dictionary to store the parsed data
        parsed_data = {}

        # First, extract the outer JSON fields (e.g., messageId, timestamp, etc.)
        parsed_data['messageId'] = json_data.get('messageId', None)
        parsed_data['timestamp'] = json_data.get('timestamp', None)
        parsed_data['eventType'] = json_data.get('eventType', None)
        parsed_data['correlationId'] = json_data.get('correlationId', None)
        parsed_data['clientId'] = json_data.get('clientId', None)
        parsed_data['version'] = json_data.get('version', None)
        parsed_data['supplierId'] = json_data.get('supplierId', None)
        parsed_data['buyerId'] = json_data.get('buyerId', None)
        parsed_data['origin'] = json_data.get('origin', None)

        # Extract the fields from the payload
        payload_data = json_data.get('payload', {})
        parsed_data['transactionId'] = payload_data.get('transactionId', None)
        parsed_data['documentNumber'] = payload_data.get('documentNumber', None)
        parsed_data['documentType'] = payload_data.get('documentType', None)
        parsed_data['s3Bucket'] = payload_data.get('s3Bucket', None)
        parsed_data['s3Key'] = payload_data.get('s3Key', None)

         # Extract and parse the attachments field from the payload
        attachments = payload_data.get('attachments', [])
        parsed_data['attachments'] = [{"Id": attachment.get('Id', None), "Url": attachment.get('Url', None)} for attachment in attachments]


        # Extract the cXML field from the payload
        cxml_string = payload_data.get('cxml', None)

        if cxml_string:
            # Parse the cXML string using xml.etree.ElementTree
            root = ET.fromstring(cxml_string)

            # Recursively parse the XML structure and add it to the parsed data
            parsed_data['cXML'] = recursive_parse_xml(root)

        else:
            st.error("No 'cxml' field found in the JSON payload.")
            return None

        return parsed_data

    except ET.ParseError as e:
        st.error(f"Error parsing cXML: {e}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        return None

# Main section: if files are uploaded, parse each cXML file
parsed_data = []
if uploaded_files:
    st.write("Parsing uploaded cXML files...")
    for file in uploaded_files:
        data = parse_cxml(file)
        if data:
            parsed_data.append(data)

    # Display the parsed data
    for idx, data in enumerate(parsed_data):
        st.subheader(f"Parsed Data from File {idx + 1}")
        st.json(data)


# Function to create vector store and store cXML data
def create_vector_store_and_store_cxml_data(parsed_data):
    global vector_store_id  # Reference the global variable to store the ID
    try:
        # Convert the parsed data to a list of dicts
        cxml_data_list = parsed_data

        # Save JSON data to a file
        with open("/tmp/cxml_data.json", "w") as f:
            json.dump(cxml_data_list, f)

        # Upload the file to OpenAI
        upload_response = client.files.create(
            purpose='assistants',
            file=open("/tmp/cxml_data.json", "rb")
        )

        # Access the file ID properly
        file_id = upload_response.id  # Retrieve the file ID from the response object

        st.write(f"File uploaded with ID: {file_id}")

        # Directly return the file ID
        return file_id

    except Exception as e:
        st.error(f"Failed to create vector store: {e}")
        return None

# Function to handle assistant response
def handle_assistant_response_with_thread(file_id, user_input):
    try:
        # Create the assistant first (you can adjust the model as needed)
        assistant = client.beta.assistants.create(
            instructions="You are a helpful assistant that answers questions based on the cXML data.",
            model="gpt-4"
        )
        st.write("Assistant created successfully!")

        # Create a thread for handling the user's query, attaching the file
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Please provide insights based on this query: {user_input}",
                    "attachments": [
                        {
                            "file_id": file_id,
                            "tools": [{"type": "file_search"}]
                        }
                    ]
                }
            ]
        )

        # Poll the run to completion and retrieve the messages
        run = client.beta.threads.runs.create_and_poll(thread_id=thread.id, assistant_id=assistant.id)
        messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

        # Display the assistant's response
        if messages:
            message_content = messages[0].content[0].text
            st.write(f"**Assistant's Answer:** {message_content}")
        else:
            st.error("No relevant data found for this query in the vector store.")

    except Exception as e:
        st.error(f"An error occurred while handling the assistant response: {e}")

# User input
user_question = st.text_input("Ask a question about the cXML files:")

# Main logic for handling user interaction
if st.button("Ask Assistant"):
    if user_question:
        st.write(f"You entered: {user_question}")

        try:
            # Ensure file_id is properly set
            file_id = create_vector_store_and_store_cxml_data(parsed_data)
            if file_id:
                st.success("Vector store is initialized.")
                # Handle assistant response using threads
                handle_assistant_response_with_thread(file_id, user_question)
            else:
                st.error("File upload failed, unable to initialize vector store.")

        except Exception as e:
            # Handle any error that occurs during the process
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter a question before clicking the button.")
