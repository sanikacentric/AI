import os
import streamlit as st
from github import Github
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytz
import weaviate
from sentence_transformers import SentenceTransformer
import altair as alt
import base64

#######################
# Page configuration
st.set_page_config(
    page_title="GitHub Developer Productivity AI",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# GitHub Token Environment Variable
os.environ['GITHUB_TOKEN'] = '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'
token = os.getenv('GITHUB_TOKEN')

if not token:
    raise Exception("GitHub token not found. Please set the GITHUB_TOKEN environment variable.")
g = Github(token)

# Initialize SentenceTransformer model from Hugging Face
model = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L6-v2')

# Initialize Weaviate Client
client = weaviate.Client(url="http://weaviate:8080")

# Check if the "Developer" class already exists before creating the schema
class_exists = False
schema_existing = client.schema.get()
for existing_class in schema_existing['classes']:
    if existing_class['class'] == "Developer":
        class_exists = True
        break

# If the class does not exist, create it
if not class_exists:
    schema = {
        "classes": [
            {
                "class": "Developer",
                "properties": [
                    {"name": "name", "dataType": ["string"]},
                    {"name": "repository", "dataType": ["string"]},
                    {"name": "commits", "dataType": ["int"]},
                    {"name": "additions", "dataType": ["int"]},
                    {"name": "deletions", "dataType": ["int"]},
                    {"name": "commit_frequency", "dataType": ["number"]},
                    {"name": "prs_created", "dataType": ["int"]},
                    {"name": "prs_merged", "dataType": ["int"]},
                    {"name": "prs_closed", "dataType": ["int"]},
                    {"name": "prs_open", "dataType": ["int"]},
                    {"name": "commit_merge", "dataType": ["int"]},
                    {"name": "code_reviews", "dataType": ["int"]},
                    {"name": "issues_created", "dataType": ["int"]},
                    {"name": "issues_assigned", "dataType": ["int"]},
                    {"name": "issues_resolved", "dataType": ["int"]},
                    {"name": "affected_files", "dataType": ["string"]},
                    {"name": "embedding", "dataType": ["blob"]},
                ]
            }
        ]
    }
    client.schema.create(schema)

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

# Columns Setup
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

# Make start_date and end_date offset-aware by converting them to EST timezone
start_date = est.localize(start_date)
end_date = est.localize(end_date)

# Fetch Repository Data
repo = g.get_repo(f"{org_name}/{repo_name}")
total_repos = g.get_user().get_repos().totalCount

# Initialize Data Collection
developer_data = {}
developer_texts = []

# Fetch Issues within the date range
issues = repo.get_issues(state='all', since=start_date)

for issue in issues:
    if issue.created_at >= start_date and issue.created_at <= end_date:
        creator = issue.user.login if issue.user else 'Unknown'
        assignees = [assignee.login for assignee in issue.assignees] if issue.assignees else []
        
        if creator not in developer_data:
            developer_data[creator] = {
                'commits': 0,
                'additions': 0,
                'deletions': 0,
                'total_changes': 0,
                'commit_frequency': 0,
                'commit_details': [],
                'prs_created': 0,
                'prs_merged': 0,
                'prs_closed': 0,
                'prs_reviewed': 0,
                'code_reviews': 0,
                'issues_created': 0,  # Initialize issue resolution fields
                'issues_assigned': 0,
                'issues_resolved': 0,
                'affected_files': set()
            }
        
        # Track issues created
        developer_data[creator]['issues_created'] += 1
        
        # Track issues assigned
        for assignee in assignees:
            if assignee not in developer_data:
                developer_data[assignee] = {
                    'commits': 0,
                    'additions': 0,
                    'deletions': 0,
                    'total_changes': 0,
                    'commit_frequency': 0,
                    'commit_details': [],
                    'prs_created': 0,
                    'prs_merged': 0,
                    'prs_closed': 0,
                    'prs_reviewed': 0,
                    'code_reviews': 0,
                    'issues_created': 0,
                    'issues_assigned': 0,
                    'issues_resolved': 0,
                    'affected_files': set()
                }
            developer_data[assignee]['issues_assigned'] += 1
        
        # Track issues resolved
        if issue.state == 'closed':
            closer = issue.closed_by.login if issue.closed_by else 'Unknown'
            if closer not in developer_data:
                developer_data[closer] = {
                    'commits': 0,
                    'additions': 0,
                    'deletions': 0,
                    'total_changes': 0,
                    'commit_frequency': 0,
                    'commit_details': [],
                    'prs_created': 0,
                    'prs_merged': 0,
                    'prs_closed': 0,
                    'prs_reviewed': 0,
                    'code_reviews': 0,
                    'issues_created': 0,
                    'issues_assigned': 0,
                    'issues_resolved': 0,
                    'affected_files': set()
                }
            developer_data[closer]['issues_resolved'] += 1

# Fetch Pull Requests and filter them manually
pulls = repo.get_pulls(state='closed', sort='created', direction='desc', base='main')

# Filter pull requests within the date range
filtered_pulls = [pull for pull in pulls if pull.created_at >= start_date and pull.created_at <= end_date]

# Initialize PR counters for each developer
for pull in filtered_pulls:
    author = pull.user.login if pull.user else 'Unknown'
    if author not in developer_data:
        developer_data[author] = {
            'commits': 0,
            'additions': 0,
            'deletions': 0,
            'total_changes': 0,
            'commit_frequency': 0,
            'commit_details': [],
            'prs_created': 0,
            'prs_merged': 0,
            'prs_closed': 0,
            'prs_reviewed': 0,
            'code_reviews': 0,  # Initialize code reviews
            'affected_files': set()
        }
    
    # Count PRs
    developer_data[author]['prs_created'] += 1
    if pull.merged_at:
        developer_data[author]['prs_merged'] += 1
    if pull.state == 'closed':
        developer_data[author]['prs_closed'] += 1

        # Count code reviews
    reviews = pull.get_reviews()
    for review in reviews:
        reviewer = review.user.login if review.user else 'Unknown'
        if reviewer not in developer_data:
            developer_data[reviewer] = {
                'commits': 0,
                'additions': 0,
                'deletions': 0,
                'total_changes': 0,
                'commit_frequency': 0,
                'commit_details': [],
                'prs_created': 0,
                'prs_merged': 0,
                'prs_closed': 0,
                'prs_reviewed': 0,
                'code_reviews': 0,  # Initialize code reviews
                'affected_files': set()
            }
        developer_data[reviewer]['code_reviews'] += 1

        # Adding fields for Commit Merge and PR Open in developer_data
for dev in developer_data:
    developer_data[dev]['commit_merge'] = 0  # Initialize commit_merge field
    developer_data[dev]['prs_open'] = 0       # Initialize pr_open field

# Iterate Over Commits
for commit in repo.get_commits(since=start_date, until=end_date):
    author = commit.author.login if commit.author else 'Unknown'
    additions = commit.stats.additions
    deletions = commit.stats.deletions
    total_changes = additions + deletions
    files = [file.filename for file in commit.files]

    if author not in developer_data:
        developer_data[author] = {
            'commits': 0,
            'additions': 0,
            'deletions': 0,
            'total_changes': 0,
            'commit_frequency': 0,
            'commit_details': [],
            'prs_created': 0,
            'prs_open': 0,       # Initialize pr_open field
            'prs_merged': 0,
            'prs_closed': 0,
            'prs_reviewed': 0,
            'affected_files': set(),
            'commit_merge': 0,  # Initialize commit_merge field
            
        }

    developer_data[author]['commits'] += 1
    developer_data[author]['additions'] += additions
    developer_data[author]['deletions'] += deletions
    developer_data[author]['total_changes'] += total_changes
    developer_data[author]['commit_frequency'] = developer_data[author]['commits'] / days
    developer_data[author]['affected_files'].update(files)
    
    commit_detail = f"Commit: '{commit.commit.message}', Additions: {additions}, Deletions: {deletions}, Total changes: {total_changes}"
    developer_data[author]['commit_details'].append(commit_detail)

    developer_texts.append(f"{author} made the following commit in {repo_name}: {commit_detail}")

# Count commit merges (simple heuristic by checking for "Merge" in the message)
    if "merge" in commit.commit.message.lower():
        developer_data[author]['commit_merge'] += 1

# Process pull request commits
for pull in filtered_pulls:
    pr_commits = pull.get_commits()
    for pr_commit in pr_commits:
        pr_author = pr_commit.author.login if pr_commit.author else 'Unknown'
        pr_additions = pr_commit.stats.additions
        pr_deletions = pr_commit.stats.deletions
        pr_total_changes = pr_additions + pr_deletions
        pr_files = [file.filename for file in pr_commit.files]

        if pr_author not in developer_data:
            developer_data[pr_author] = {
                'commits': 0,
                'additions': 0,
                'deletions': 0,
                'total_changes': 0,
                'commit_frequency': 0,
                'commit_details': [],
                'prs_created': 0,
                'prs_open': 0 ,      # Initialize pr_open field
                'prs_merged': 0,
                'prs_closed': 0,
                'prs_reviewed': 0,
                'affected_files': set(),
                'commit_merge': 0,  # Initialize commit_merge field
                
            }

        developer_data[pr_author]['commits'] += 1
        developer_data[pr_author]['additions'] += pr_additions
        developer_data[pr_author]['deletions'] += pr_deletions
        developer_data[pr_author]['total_changes'] += pr_total_changes
        developer_data[pr_author]['commit_frequency'] = developer_data[pr_author]['commits'] / days
        developer_data[pr_author]['affected_files'].update(pr_files)

        pr_commit_detail = f"PR Commit: '{pr_commit.commit.message}', Additions: {pr_additions}, Deletions: {pr_deletions}, Total changes: {pr_total_changes}"
        developer_data[pr_author]['commit_details'].append(pr_commit_detail)

        developer_texts.append(f"{pr_author} made the following PR commit in {repo_name}: {pr_commit_detail}")
  # Count open PRs
        developer_data[pr_author]['prs_open'] += 1

# Function to encode the embedding as base64
def encode_embedding(embedding_vector):
    embedding_bytes = np.array(embedding_vector, dtype=np.float32).tobytes()
    return base64.b64encode(embedding_bytes).decode('utf-8')

# Store developer data in Weaviate
def store_in_weaviate(repo_name):
    for dev, data in developer_data.items():
        # Ensure all necessary keys are present with default values
        commit_merge = data.get('commit_merge', 0)
        code_reviews = data.get('code_reviews', 0)
        issues_created = data.get('issues_created', 0)
        issues_assigned = data.get('issues_assigned', 0)
        issues_resolved = data.get('issues_resolved', 0)
        additions = data.get('additions', 0)
        deletions = data.get('deletions', 0)
        total_changes = data.get('total_changes', 0)
        commit_frequency = data.get('commit_frequency', 0)
        prs_created = data.get('prs_created', 0)
        prs_merged = data.get('prs_merged', 0)
        prs_closed = data.get('prs_closed', 0)
        prs_open = data.get('prs_open', 0)

        # Embed the developer's data and convert it to base64 using Hugging Face
        embedding_vector = model.encode(
            f"{dev}: {data['commits']} commits, {additions} additions, {deletions} deletions, {commit_frequency} commits/day, "
            f"{prs_created} PRs created, {prs_merged} PRs merged, {prs_closed} PRs closed, {prs_open} PRs open, "
            f"{commit_merge} commits merged, {code_reviews} code reviews, {issues_created} issues created, {issues_assigned} issues assigned, "
            f"{issues_resolved} issues resolved."
        )
        embedding_base64 = encode_embedding(embedding_vector)

        # Store the data in Weaviate with the repository name
        client.data_object.create({
            "name": dev,
            "repository": repo_name,  # Adding repository name
            "commits": data['commits'],
            "additions": additions,
            "deletions": deletions,
            "commit_frequency": commit_frequency,
            "prs_created": prs_created,
            "prs_merged": prs_merged,
            "prs_closed": prs_closed,
            "prs_open": prs_open,
            "commit_merge": commit_merge,
            "code_reviews": code_reviews,
            "issues_created": issues_created,
            "issues_assigned": issues_assigned,
            "issues_resolved": issues_resolved,
            "affected_files": ', '.join(data['affected_files']),
            "embedding": embedding_base64
        }, "Developer")

# Call the function to store data with the repository name
store_in_weaviate(repo_name)

# Fetch and print data from Weaviate to verify storage
stored_data = client.query.get("Developer", ["name", "repository", "commits", "additions", "deletions"]).do()

print("Stored Developer Data in Weaviate:")
for dev in stored_data["data"]["Get"]["Developer"]:
    print(dev)


# Query Weaviate Directly Based on User Input
def query_openai_with_weaviate(prompt):
    query_vector = np.array(model.encode(prompt))

    results = client.query.get("Developer", ["name", "repository", "commits", "additions", "deletions", "commit_frequency",
                                             "prs_created", "prs_merged", "prs_closed", "prs_open", "commit_merge",
                                             "code_reviews", "issues_created", "issues_assigned", "issues_resolved", 
                                             "affected_files"]).with_near_vector({
        "vector": query_vector.tolist(),
        "certainty": 0.85  # Adjust this as necessary
    }).do()

    st.write("Print Result")
    st.write(results) 

    if len(results["data"]["Get"]["Developer"]) > 0:
        dev_info = results["data"]["Get"]["Developer"][0]
        result_text = f"{dev_info['name']} (Repository: {dev_info['repository']}): {dev_info['commits']} commits, " \
                      f"{dev_info['additions']} additions, {dev_info['deletions']} deletions, {dev_info['commit_frequency']} commits/day, " \
                      f"{dev_info['prs_created']} PRs created, {dev_info['prs_merged']} PRs merged, {dev_info['prs_closed']} PRs closed, " \
                      f"{dev_info['prs_open']} PRs open, {dev_info['commit_merge']} commits merged, {dev_info['code_reviews']} code reviews, " \
                      f"{dev_info['issues_created']} issues created, {dev_info['issues_assigned']} issues assigned, {dev_info['issues_resolved']} issues resolved."
    else:
        result_text = "No relevant developer found."

    response = llm([
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=f"Based on the following information:\n\n{result_text}\n\nPlease provide a detailed summary or answer.")
    ])
    
    return response.content.strip()
