import streamlit as st
import openai
import os
from openai import OpenAI


st.title("Reflection Agent")

client = OpenAI(api_key ="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",

)

# User input
user_input2 = st.text_input("Enter your prompt for ChatGPT:")

if user_input2:
    st.write(f"You entered:{user_input2}")
    #if user_input
    #send user input to openAI GPT 3.5 model
    chat_completion= client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system","content":"You are helpful assistant." },
            {"role":"user","content":user_input2},
        ],
    )
    st.write("Post response")
    #Display the response
    st.write(chat_completion.choices[0].message.content)

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_fireworks import ChatFireworks

# Initialize the prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an essay assistant tasked with writing excellent 5-paragraph essays."
            " Generate the best essay possible for the user's request."
            " If the user provides critique, respond with a revised version of your previous attempts.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


# Initialize the LangChain client
fireworks = ChatFireworks(api_key="7fwRDUFRAq0CeHvd4ddFxllqOM4iI3XxyB6KyOpRunsL3Q91")

# Combine the prompt with the LangChain client
generate = prompt | fireworks

# Set up the user's input request
if user_input2:
    request = HumanMessage(content=user_input2)

    # Stream the response
    essay = ""
    response = generate.stream({"messages": [request]})
    for chunk in response:
        st.write(chunk.content)
        essay += chunk.content
