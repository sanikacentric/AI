import os
import streamlit as st
from github import Github
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import openai
import faiss
import numpy as np
from openai import OpenAI



# GitHub Token Environment Variable
os.environ['GITHUB_TOKEN'] = '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'
token = os.getenv('GITHUB_TOKEN')

if not token:
    raise Exception("GitHub token not found. Please set the GITHUB_TOKEN environment variable.")
g = Github(token)

# OpenAI API Key
openai.api_key = os.getenv('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')


# Initialize OpenAI client
client = OpenAI()

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

# Streamlit App Title
st.title("GitHub Developer Productivity AI")

# Dropdown for Organization and Repository Selection
org_name = st.sidebar.text_input("Enter Organization Name:", value="sanikacentric")
repo_name = st.sidebar.text_input("Enter Repository Name:", value="streamlit")

# Date Range
days = st.sidebar.slider("Select the number of days:", min_value=1, max_value=365, value=30)
start_date = datetime.now() - timedelta(days=days)
end_date = datetime.now()

# Fetch Repository Data
repo = g.get_repo(f"{org_name}/{repo_name}")

# Initialize Data Collection
developer_data = {}
developer_texts = []

# Iterate Over Commits
for commit in repo.get_commits(since=start_date, until=end_date):
    author = commit.author.login if commit.author else 'Unknown'
    additions = commit.stats.additions
    deletions = commit.stats.deletions
    total_changes = additions + deletions
    if author not in developer_data:
        developer_data[author] = {'commits': 0, 'additions': 0, 'deletions': 0, 'total_changes': 0}
    developer_data[author]['commits'] += 1
    developer_data[author]['additions'] += additions
    developer_data[author]['deletions'] += deletions
    developer_data[author]['total_changes'] += total_changes
    developer_texts.append(f"{author}: {commit.commit.message}")

# Convert developer data into vectors using the get_embedding function
texts = [f"{dev}: {data['commits']} commits, {data['additions']} additions, {data['deletions']} deletions" for dev, data in developer_data.items()]
text_vectors = np.array([get_embedding(text) for text in texts])

# Initialize FAISS index
index = faiss.IndexFlatL2(len(text_vectors[0]))
index.add(text_vectors)

# Function to query the vector store (FAISS index) and generate a response
def query_openai_with_faiss(prompt):
    query_vector = np.array(get_embedding(prompt)).astype('float32')
    D, I = index.search(np.array([query_vector]), k=1)
    result_text = texts[I[0][0]]  # Get the closest matching text from the FAISS index

    # Generate a response using GPT-4 based on the closest matching text
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Given the following information:\n\n{result_text}\n\nAnswer the following question: {prompt}"}
        ]
    )
    message = response.choices[0].message.content
    return message.strip()

# Print Developer Productivity Report
st.subheader(f"Developer Productivity Report (Last {days} Days)")
for developer, data in developer_data.items():
    st.write(f"{developer}: {data['commits']} commits, {data['additions']} additions, {data['deletions']} deletions")

# Plot Data
developers = list(developer_data.keys())
commits = [developer_data[dev]['commits'] for dev in developers]
additions = [developer_data[dev]['additions'] for dev in developers]
deletions = [developer_data[dev]['deletions'] for dev in developers]

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(developers, commits, color='blue', alpha=0.6, label='Commits')
ax.bar(developers, additions, color='green', alpha=0.6, label='Additions')
ax.bar(developers, deletions, color='red', alpha=0.6, label='Deletions')
ax.set_xlabel('Developers')
ax.set_ylabel('Count')
ax.set_title('Developer Productivity Report')
ax.legend()
ax.set_xticklabels(developers, rotation=45)
plt.tight_layout()

# Show the plot
st.pyplot(fig)

# Streamlit Input for User Query
user_query = st.text_input("Ask a question about the developer productivity data:")
if user_query:
    answer = query_openai_with_faiss(user_query)
    st.write(f"Answer: {answer}")
