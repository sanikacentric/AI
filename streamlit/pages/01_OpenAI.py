import streamlit as st
import openai
import os
from openai import OpenAI


st.title("NexGen OpenAI")

client = OpenAI(api_key ="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",

)

# User input
user_input = st.text_input("Enter your prompt for openAI:")

if user_input:
    st.write(f"You entered:{user_input}")
    #if user_input
    #send user input to openAI GPT 3.5 model
    chat_completion= client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system","content":"You are helpful assistant." },
            {"role":"user","content":user_input},
        ],
    )
    st.write("Post response")
    #Display the response
    st.write(chat_completion.choices[0].message.content)