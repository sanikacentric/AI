import streamlit as st
import openai
import anthropic
from openai import OpenAI
from langchain_anthropic import ChatAnthropic

# Set up the title
st.title("NexGen AI Model Selector")

# Dropdown to select the AI provider
provider = st.selectbox("Select AI Provider", ["OpenAI", "Anthropic"])

# Dropdown to select the model based on the provider
if provider == "OpenAI":
    model = st.selectbox("Select OpenAI Model", ["gpt-3.5-turbo", "gpt-4"])
    openai.api_key = "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"
    client = openai
elif provider == "Anthropic":
    model = st.selectbox("Select Anthropic Model", ["claude-v1", "claude-instant-v1"])
    anthropic_api_key = "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"
    client = anthropic.Client(api_key=anthropic_api_key)
    #model = ChatAnthropic(model='claude-3-opus-20240229')

# User input
user_inpu3 = st.text_input(f"Enter your prompt for {provider}:")

if user_inpu3:
    st.write(f"You entered: {user_inpu3}")
    
    if provider == "OpenAI":
        # Send user input to OpenAI GPT model
        chat_completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_inpu3},
            ],
        )
        response = chat_completion.choices[0].message.content
    
    elif provider == "Anthropic":
        # Send user input to Anthropic model
        response = client.completions.create(
            model=model,
            prompt=f"\n\nHuman: {user_inpu3}\n\nAssistant:",
            max_tokens_to_sample=300,
            stop_sequences=["\n\nHuman:"],
        )
        #response = response['completion']
    
        

    
    # Display the response
    st.write("Response:")
    st.write(response)
