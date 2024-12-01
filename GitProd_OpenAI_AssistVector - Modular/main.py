import os
import streamlit as st
from github import Github
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import pytz
import altair as alt
import json
import openai

from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI


#######################
# Page configuration
st.set_page_config(
    page_title="GitHub Developer Productivity AI",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)


from github_data import fetch_repo, fetch_issues, fetch_pull_requests, fetch_commits, process_issues, process_commits, process_pull_requests, create_developer_df

#from vector_store import create_vector_store_and_store_github_data, handle_assistant_response_with_thread
from plotting import plot_commit_charts, plot_heatmap, plot_scatter, plot_altair_charts, plot_line_chart, plot_bar_chart

from developer_performance import display_performance_data

# Import vector store functions from vector_store.py
from vector_store import create_vector_store_and_store_github_data, handle_assistant_response_with_thread


# Global variable to store the vector store ID
vector_store_id = None
# GitHub Token Environment Variable
os.environ['GITHUB_TOKEN'] = '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'
token = os.getenv('GITHUB_TOKEN')

if not token:
    raise Exception("GitHub token not found. Please set the GITHUB_TOKEN environment variable.")
g = Github(token)

# Initialize OpenAI components using LangChain
llm = ChatOpenAI(openai_api_key='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', model="gpt-4o-mini")
embedding_model = OpenAIEmbeddings(openai_api_key='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')
client = openai.Client(api_key="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")

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
st.title("GitHub Developer Productivity AI")


#######################
# Dashboard Main Panel
col = st.columns((2, 4, 2), gap='medium')

# Dropdown for Organization Selection
org_name = st.sidebar.text_input("Enter Organization Name:", value="sanikacentric")
repo_name = st.sidebar.text_input("Enter Repository Name:", value="streamlit")

# Date Range
days = st.sidebar.slider("Select the number of days:", min_value=1, max_value=365, value=30)
start_date = datetime.now() - timedelta(days=days)
end_date = datetime.now()

# Set the timezone to EST (New York)
est = pytz.timezone('America/New_York')
start_date = est.localize(start_date)
end_date = est.localize(end_date)




# Fetch Repository Data
repo = g.get_repo(f"{org_name}/{repo_name}")
total_repos = g.get_user().get_repos().totalCount


# Fetch GitHub data
with st.spinner("Fetching GitHub data..."):
    repo, total_repos = fetch_repo(org_name, repo_name)
    issues = fetch_issues(repo, start_date, end_date)
    pulls = fetch_pull_requests(repo, start_date, end_date)
    commits = fetch_commits(repo, start_date, end_date)

# Initialize developer data
developer_data = {}

# Process GitHub data
process_issues(issues, developer_data)
process_pull_requests(pulls, developer_data)
developer_texts = process_commits(commits, developer_data, repo_name, days)

# Convert developer data into a DataFrame
developer_df = create_developer_df(developer_data)


# Inside your col[0] in the main script
with col[0]:
    display_performance_data(developer_df, developer_data, total_repos)

with col[1]:

    # Vector Store and Assistant Interaction
    st.subheader("Developer Productivity Bot")
    user_input2 = st.text_input("Ask a question about the developer productivity data:")

    if st.button("Ask Assistant"):
        if user_input2:
            st.write(f"You entered: {user_input2}")
            try:
                # Ensure vector_store_id is properly set
                if vector_store_id is None:
                    vector_store_id = create_vector_store_and_store_github_data(developer_df)
                    st.success("Vector store is initialized.")
                else:
                    st.warning("Vector store is already initialized.")

                # Handle assistant response using threads
                handle_assistant_response_with_thread(vector_store_id, user_input2)

            except Exception as e:
                # Handle any error that occurs during the process
                st.error(f"An error occurred: {e}")
        else:
            st.error("Please enter a question before clicking the button.")

with col[2]:
    show_charts = st.checkbox('Enable/Disable All Charts', value=True)
    if show_charts:
        plot_heatmap(developer_data)
        plot_scatter(developer_data)
        plot_altair_charts(developer_data)
        plot_line_chart(developer_data)
        plot_bar_chart(developer_data)

