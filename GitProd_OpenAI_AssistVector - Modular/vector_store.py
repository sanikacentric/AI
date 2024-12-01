import streamlit as st
import json
import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('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'))


# Global variable to store the vector store ID
vector_store_id = None

# Function to create vector store and store GitHub data (mocked for now)
def create_vector_store_and_store_github_data(developer_df):
    """
    This function creates a vector store and stores the GitHub developer data.
    :param developer_df: DataFrame containing the developer productivity data
    :return: vector_store_id (str)
    """
    global vector_store_id  # Reference the global variable to store the ID
    try:
        # Convert the dataframe to a list of dicts, one for each row (useful for embeddings)
        developer_data_list = developer_df.to_dict(orient="records")

        # Debugging: Print developer data to be stored in vector store
        st.write(f"Storing the following data in the vector store: {json.dumps(developer_data_list, indent=2)}")

        # Save JSON data to a file
        with open("/tmp/developer_data.json", "w") as f:
            json.dump(developer_data_list, f)

        # Upload the file to OpenAI
        upload_response = client.files.create(
            purpose='user_data',  # Adjust the purpose if needed
            file=open("/tmp/developer_data.json", "rb")
        )
        file_id = upload_response.id  # Get file ID

        # Debugging: Confirm the file was uploaded successfully
        st.write(f"File uploaded with ID: {file_id}")

        # Create a vector store using the uploaded file ID
        vector_store = client.beta.vector_stores.create(
            name="GitHub Data Vector Store",
            file_ids=[file_id],
            # embeddings_model="text-embedding-ada-002"  # Ensure embeddings are created properly
        )
        vector_store_id = vector_store.id  # Set global vector_store_id
        
        # Debugging: Confirm the vector store ID
        st.write(f"Vector store created successfully with ID: {vector_store_id}")
            
    except Exception as e:
        st.error(f"Failed to create vector store: {e}")
        return None
    
    return vector_store_id

# Function to handle assistant and vector store querying with threads
def handle_assistant_response_with_thread(vector_store_id, user_input2):
    """
    This function handles the assistant response using threading for querying the vector store and answering user queries.
    """
    try:
        # Create the assistant first with the vector store attached
        assistant = client.beta.assistants.create(
            instructions="You are a helpful assistant that answers questions based on the GitHub developer productivity data.",
            model="gpt-4o",
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
            messages=[{"role": "user", "content": f"Here is some developer data: {user_input2}. Please provide a detailed response to the following question: {user_input2}. \
                Please structure your answer in the following format:\n\n \
                1. **Summary**: Give a brief overview of the answer.\n\n \
                2. **Details**: Provide a more in-depth analysis.\n\n \
                3. **Developer-Specific Insights**: Highlight the developers involved.\n\n \
                4. **Correct Answer**: Clearly answer the question.\n\n \
                5. **PR Information**: Provide details on pull requests (created, merged, closed, and reviewed) for each developer, along with their involvement in the pull request process (e.g., as authors or reviewers).\n\n \
                6. **Commit Merge Information**: Provide detailed insights about commit merges, including the number of commits merged, the type of merge (e.g., fast-forward or non-fast-forward), and which developers are involved in merging branches.\n\n \
                7. **Analysis**: Analyze how active the developer is based on their commits, PRs, and code reviews.\n\n \
                8. **Overall Comparison**: Compare the developers' overall code contributions (commits, PRs, issues resolved).\n\n \
                9. **Repositories**: Mention the repository names where the code changes were made.\n\n \
                10. **Brief Summary**: Summarize the overall findings in detail, providing insights on the most and least active developers and their contributions across repositories.\n\n \
                11. **Conclusion**: Provide a conclusion summarizing the findings and any takeaways."}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store_id]
                }
            }
        )

        # Poll the run to completion and retrieve the messages
        run = client.beta.threads.runs.create_and_poll(thread_id=thread.id, assistant_id=assistant.id)

        messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

        # Assuming messages are returned with content
        if messages:
            message_content = messages[0].content[0].text
            st.write(f"**Assistant's Answer:** {message_content}")
        else:
            st.error("No relevant data found for this query in the vector store.")
    
    except Exception as e:
        st.error(f"An error occurred while handling the assistant response: {e}")

# Main logic for handling user interaction
#st.subheader("Developer Productivity Bot")
#user_input2 = st.text_input("Ask a question about the developer productivity data:")


