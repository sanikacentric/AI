import json
import streamlit as st
import openai

def create_vector_store_and_store_cxml_data(parsed_data, client):
    global vector_store_id  # Reference the global variable to store the vector store ID
    try:
        cxml_data_list = []

        for idx, data in enumerate(parsed_data):
            cxml_data_list.append({
                "file_index": str(idx + 1),  # Store file index as a string
                "content": f"File {idx + 1}: {json.dumps(data)}"  # Combine file index with the data
            })

        # Debugging parsed data before storing it
        st.write(f"Storing the following cXML data in the vector store: {json.dumps(cxml_data_list, indent=2)}")

        # Save cXML JSON data to a file
        with open("/tmp/cxml_data.json", "w") as f:
            json.dump(cxml_data_list, f)

        # Upload the file to the assistant (OpenAI or whichever API is used)
        upload_response = client.files.create(
            purpose='assistants',
            file=open("/tmp/cxml_data.json", "rb")
        )
        file_id = upload_response.id  # Get the file ID from the upload response

        # Display file ID to confirm upload
        st.write(f"File uploaded with ID: {file_id}")

        # Create a vector store using the uploaded cXML file ID
        vector_store = client.beta.vector_stores.create(
            name="cXML Data Vector Store",
            file_ids=[file_id]  # Associate the vector store with the uploaded file
        )
        vector_store_id = vector_store.id

        # Confirm vector store creation
        st.write(f"Vector store created successfully with ID: {vector_store_id}")
                
    except Exception as e:
        st.error(f"Failed to create vector store: {e}")
        return None

    return vector_store_id
