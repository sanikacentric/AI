import streamlit as st
import openai

# Function to handle assistant response using the vector store for file search and threads
def handle_assistant_response_with_thread(client, vector_store_id, user_input, file_index):
    """
    This function handles the assistant response using threading for querying the vector store and answering user queries.
    """
    try:
        # Create the assistant with file search capabilities and the vector store attached
        assistant = client.beta.assistants.create(
            instructions="You are a helpful assistant that answers questions based on the cXML data.",
            model="gpt-4o-mini",
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store_id]  # Attach vector store ID
                }
            }
        )
        st.write("Assistant created successfully with the vector store attached!")

        # Ensure that file_index is passed as a string
        file_index_str = str(file_index)

        # Modify the query to explicitly mention the file index in the user query
        user_query = f"Provide insights from File {file_index_str}. {user_input}"

        # Create a thread for handling the user's query
        thread = client.beta.threads.create(
            messages=[{
                "role": "user",
                "content": user_query,  # Use the modified query that includes the file reference
            }],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store_id]  # Attach vector store for file search
                }
            }
        )

        # Poll the run to completion and retrieve the messages
        run = client.beta.threads.runs.create_and_poll(thread_id=thread.id, assistant_id=assistant.id)
        st.write("run")
        st.write(run)
        messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
        st.write("messages")
        st.write(messages)
        # Display the assistant's response
        if messages:
            message_content = messages[0].content[0].text
            st.write(f"**Assistant's Answer:** {message_content}")
        else:
            st.error("No relevant data found for this query in the vector store.")
    
    except Exception as e:
        st.error(f"An error occurred while handling the assistant response: {e}")
