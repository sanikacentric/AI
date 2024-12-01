import streamlit as st
import openai
import os
#from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
#load_dotenv()

# Set your OpenAI API key from the environment variable
#openai.api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key ="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",

)

# User input
user_input = st.text_input("Enter your prompt for ChatGPT:")

def get_gpt_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

# Streamlit app
st.title("NexGen OpenAI")


# Button to submit the input
if st.button("Submit"):
    if user_input:
        # Get the response from GPT
        response = get_gpt_response(user_input)
        # Display the response
        st.write("ChatGPT Response:")
        st.write(response)
    else:
        st.write("Please enter a prompt.")
