import streamlit as st
import logging
from openai import OpenAI

# Replace 'your-api-key-here' with your actual OpenAI API key
client = OpenAI(api_key='sk')  # Replace with your actual key
logger = logging.getLogger(__name__)

def create_assistant(instructions, model="gpt-4o-mini"):
    """Create an assistant for chatting."""
    try:
        logger.info("Assistant initialized successfully.")
        return True  # Just returning True to indicate success
    except Exception as e:
        logger.error(f"Failed to initialize assistant: {e}")
        st.error(f"Failed to initialize assistant: {e}")
        return None

def send_message(message):
    """Send a message to the assistant and get a response."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",#gpt-4o-mini
            messages=[
                {"role": "system", "content": "You are a helpful everyday assistant."},
                {"role": "user", "content": message}
            ]
        )
        logger.info("Assistant responded successfully.")
         # Correct way to access the content of the assistant's response
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        st.error(f"Failed to send message: {e}")
        return None

def everyday_chat_assistant():
    """Renders the Everyday Chat Assistant UI."""
    st.title("Everyday Chat Assistant")
    
    # User input for the message
    user_input = st.text_input("Enter your message:")
    
    # Button to send the message
    if st.button("Ask Assistant"):
        if user_input:
            try:
                # Create the assistant if not already created (for now, this is a placeholder)
                if 'chat_assistant_initialized' not in st.session_state:
                    st.session_state.chat_assistant_initialized = create_assistant(
                        instructions="You are a helpful everyday assistant.",
                        model="gpt-4o-mini"
                    )
                    if st.session_state.chat_assistant_initialized:
                        st.success("Chat Assistant created successfully!")

                # Send the message if the assistant was initialized
                if st.session_state.chat_assistant_initialized:
                    response = send_message(user_input)
                    if response:
                        st.write(response)

            except Exception as e:
                logger.error(f"Error during chat: {e}")
                st.error(f"Error during chat: {e}")
        else:
            st.warning("Please enter a message to ask the assistant.")

def main():
    """Main function to display the assistant options."""
    st.markdown("<h1 style='text-align: center;'>NexGen AI Hub! Please select an Assistant.</h1>", unsafe_allow_html=True)

    # Add button for Everyday Chat Assistant
    if st.button("🤖 Everyday Chat Assistant"):
        everyday_chat_assistant()  # Show the chat assistant UI when the button is clicked

if __name__ == "__main__":
    main()
