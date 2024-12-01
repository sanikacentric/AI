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

# Initialize OpenAI components using LangChain
#llm = ChatOpenAI(openai_api_key='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', model="gpt-4o-mini")
#embedding_model = OpenAIEmbeddings(openai_api_key='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')


client = OpenAI(api_key ="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")


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
st.title("cXML File Assistant")

# Columns Setup
#col = st.columns((2, 4, 2), gap='medium')


# Upload multiple cXML files
uploaded_files = st.file_uploader("Upload cXML files", type="xml", accept_multiple_files=True)

# Function to sanitize and clean JSON content
def sanitize_json_string(json_string):
    # Replace unescaped newlines or other control characters
    sanitized_string = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_string)
    return sanitized_string

# Function to recursively parse an XML element and its children
def recursive_parse_xml(element, parsed_dict=None):
    if parsed_dict is None:
        parsed_dict = {}

    # Parse element's tag and text content
    parsed_dict[element.tag] = element.text

    # Recursively process child elements
    for child in element:
        # If the child has no text, recurse to get its children
        if len(child):
            parsed_dict[child.tag] = recursive_parse_xml(child)
        else:
            parsed_dict[child.tag] = child.text

    return parsed_dict

# Function to parse and extract cXML data from the JSON payload
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

        # Extract the cXML field from the payload
        cxml_string = json_data.get('payload', {}).get('cxml', None)

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


# Function to generate embeddings for each data point
def get_embedding(text, model="text-embedding-ada-002"):
    response = openai.Embedding.create(input=text, model=model)
    return response["data"][0]["embedding"]

# Function to create vector store and store cXML data
def create_vector_store_and_store_cxml_data(parsed_data):
    global vector_store_id  # Reference the global variable to store the ID
    try:
        # Convert the parsed data to a list of dicts (useful for embeddings)
        cxml_data_list = parsed_data

        # Generate embeddings for each data point
        embeddings = [get_embedding(str(data)) for data in cxml_data_list]

        # Save JSON data to a file
        with open("/tmp/cxml_data.json", "w") as f:
            json.dump(cxml_data_list, f)

        # Upload the file to OpenAI
        upload_response = client.files.create(
            purpose='user_data',
            file=open("/tmp/cxml_data.json", "rb")
        )
        file_id = upload_response['id']  # Get file ID

        st.write(f"File uploaded with ID: {file_id}")

        # Create a vector store using the uploaded file ID
        vector_store = client.beta.vector_stores.create(
            name="cXML Data Vector Store",
            file_ids=[file_id]
        )
        vector_store_id = vector_store.id

        st.write(f"Vector store created successfully with ID: {vector_store_id}")

    except Exception as e:
        st.error(f"Failed to create vector store: {e}")
        return None

    return vector_store_id

# Function to handle assistant response
def handle_assistant_response_with_thread(vector_store_id, user_input):
    try:
        # Create the assistant with the vector store attached
        assistant = client.beta.assistants.create(
            instructions="You are a helpful assistant that answers questions based on the cXML data.",
            model="gpt-4",
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store_id]
                }
            }
        )
        st.write("Assistant created successfully with the vector store attached!")

        # Create a thread for handling the user's query
        thread = client.beta.threads.create(
            messages=[{"role": "user", "content": f"Please provide insights based on this query: {user_input}"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store_id]
                }
            }
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
            # Ensure vector_store_id is properly set
            if vector_store_id is None:
                vector_store_id = create_vector_store_and_store_cxml_data(parsed_data)
                st.success("Vector store is initialized.")
            else:
                st.warning("Vector store is already initialized.")

            # Handle assistant response using threads
            handle_assistant_response_with_thread(vector_store_id, user_question)

        except Exception as e:
            # Handle any error that occurs during the process
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter a question before clicking the button.")