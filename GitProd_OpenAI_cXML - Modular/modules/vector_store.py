import json
import streamlit as st
import openai

# Function to create vector store and store cXML data
def create_vector_store_and_store_cxml_data(parsed_data, client):
    global vector_store_id  # Reference the global variable to store the vector store ID
    try:
        # Convert parsed cXML data to a JSON format (list of dictionaries or appropriate format)
        cxml_data_list = parsed_data

        # Debugging: Print cXML data to be stored in vector store
        st.write(f"Storing the following cXML data in the vector store: {json.dumps(cxml_data_list, indent=2)}")

        # Save cXML JSON data to a file
        with open("/tmp/cxml_data.json", "w") as f:
            json.dump(cxml_data_list, f)

        # Upload the file to the assistant (OpenAI or whichever API is used)
        upload_response = client.files.create(
            purpose='assistants',  # Adjust the purpose if needed
            file=open("/tmp/cxml_data.json", "rb")
        )
        file_id = upload_response.id  # Get the file ID from the upload response

        # Debugging: Confirm the file was uploaded successfully
        st.write(f"File uploaded with ID: {file_id}")

        # Create a vector store using the uploaded cXML file ID
        vector_store = client.beta.vector_stores.create(
            name="cXML Data Vector Store",  # Give a meaningful name
            file_ids=[file_id],  # Associate the vector store with the uploaded file
            # embeddings_model="text-embedding-ada-002"  # Ensure embeddings are created properly if required
        )
        vector_store_id = vector_store.id  # Set global vector_store_id

        # Debugging: Confirm the vector store ID
        st.write(f"Vector store created successfully with ID: {vector_store_id}")
                
    except Exception as e:
        st.error(f"Failed to create vector store: {e}")
        return None

    return vector_store_id
