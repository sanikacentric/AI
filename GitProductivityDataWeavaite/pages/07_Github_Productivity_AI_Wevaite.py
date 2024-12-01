import os
import streamlit as st
from github import Github
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytz
import weaviate
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import altair as alt
import base64
import numpy as np

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

# Initialize OpenAI components using LangChain
llm = ChatOpenAI(openai_api_key='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', model="gpt-4o-mini")
embedding_model = OpenAIEmbeddings(openai_api_key='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')


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

        # Embed the developer's data and convert it to base64
        embedding_vector = embedding_model.embed_query(
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
    query_vector = np.array(embedding_model.embed_query(prompt))

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

# Convert developer data to a pandas DataFrame for tabular display
developer_df = pd.DataFrame.from_dict(developer_data, orient='index')
developer_df.reset_index(inplace=True)
developer_df.rename(columns={'index': 'Developer'}, inplace=True)

# Convert affected files from set to a comma-separated string
developer_df['affected_files'] = developer_df['affected_files'].apply(lambda x: ', '.join(x))

# Streamlit layout
with col[0]:
    max_commits = developer_df['commits'].max()
    min_commits = developer_df['commits'].min()

    highest_commit_developers = developer_df[developer_df['commits'] == max_commits][['Developer', 'commits']]
    lowest_commit_developers = developer_df[developer_df['commits'] == min_commits][['Developer', 'commits']]

    highest_commit_developers['Performer'] = 'Best Performer'
    lowest_commit_developers['Performer'] = 'Average Performer'

    commit_extremes_df = pd.concat([highest_commit_developers, lowest_commit_developers])

    def highlight_best_performer(val):
        return f'background-color: green' if val == 'Best Performer' else ''

    styled_commit_extremes_df = commit_extremes_df.style.applymap(highlight_best_performer, subset=['Performer'])

    st.subheader("Developers with Highest and Lowest Commits")
    st.dataframe(styled_commit_extremes_df)

    developer_df['total_prs'] = developer_df['prs_created'] + developer_df['prs_merged'] + developer_df['prs_closed']
    max_prs = developer_df['total_prs'].max()
    min_prs = developer_df['total_prs'].min()

    highest_pr_developers = developer_df[developer_df['total_prs'] == max_prs][['Developer', 'total_prs']]
    lowest_pr_developers = developer_df[developer_df['total_prs'] == min_prs][['Developer', 'total_prs']]

    highest_pr_developers['Performer'] = 'Highest PR Performer'
    lowest_pr_developers['Performer'] = 'Lowest PR Performer'

    pr_extremes_df = pd.concat([highest_pr_developers, lowest_pr_developers])

    def highlight_pr_performer(val):
        return f'background-color: green' if val == 'Highest PR Performer' else ''

    styled_pr_extremes_df = pr_extremes_df.style.applymap(highlight_pr_performer, subset=['Performer'])

    st.subheader("Developers with Highest and Lowest Total PRs")
    st.dataframe(styled_pr_extremes_df)

    st.subheader("Developer Productivity Report (Last 30 Days)")
    st.dataframe(developer_df.style.set_table_styles([{'selector': 'th', 'props': [('font-weight', 'bold'), ('text-align', 'center')]}]))

with col[1]:
    st.subheader("Developer Productivity Bot")
    user_query = st.text_input("Ask a question about the developer productivity data:")
    if user_query:
        answer = query_openai_with_weaviate(user_query)
        st.write(f"Answer: {answer}")

with col[2]:
    st.markdown('#### Plot for Commits, Additions, and Deletions')
    developers = list(developer_data.keys())
    commits = [developer_data[dev]['commits'] for dev in developers]
    additions = [developer_data[dev]['additions'] for dev in developers]
    deletions = [developer_data[dev]['deletions'] for dev in developers]
    prs_created = [developer_data[dev]['prs_created'] for dev in developers]
    prs_merged = [developer_data[dev]['prs_merged'] for dev in developers]
    prs_closed = [developer_data[dev]['prs_closed'] for dev in developers]

    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.bar(developers, commits, color='blue', alpha=0.6, label='Commits')
    ax1.bar(developers, additions, color='green', alpha=0.6, label='Additions')
    ax1.bar(developers, deletions, color='red', alpha=0.6, label='Deletions')
    ax1.bar(developers, prs_created, color='orange', alpha=0.6, label='PRs Created')
    ax1.bar(developers, prs_merged, color='purple', alpha=0.6, label='PRs Merged')
    ax1.bar(developers, prs_closed, color='brown', alpha=0.6, label='PRs Closed')
    ax1.set_xlabel('Developers')
    ax1.set_ylabel('Count')
    ax1.set_title('Developer Productivity Report')
    ax1.legend()
    ax1.set_xticklabels(developers, rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig1)

    # Heat map visualization
    st.markdown("<h3 style='text-align: center;'>Heat Map</h3>", unsafe_allow_html=True)
    columns = ['Date', 'Developer', 'Commits', 'Repository']
    commit_data = pd.DataFrame(columns=columns)
    commits = repo.get_commits(since=start_date, until=end_date)
    for commit in commits:
        commit_date = commit.commit.author.date.date()
        developer = commit.author.login if commit.author else 'Unknown'
        repo_name = repo.name
        new_row = pd.DataFrame({'Date': [commit_date], 'Developer': [developer], 'Commits': [1], 'Repository': [repo_name]})
        commit_data = pd.concat([commit_data, new_row], ignore_index=True)

    commit_details_df = commit_data.groupby(['Date', 'Developer', 'Repository']).count().reset_index()
    heatmap_with_repo = alt.Chart(commit_details_df).mark_rect().encode(
        x=alt.X('Developer:N', title='Developer'),
        y=alt.Y('Date:T', title='Date'),
        color=alt.Color('Commits:Q', scale=alt.Scale(scheme='viridis'), legend=alt.Legend(title="Commits")),
        tooltip=['Date', 'Developer', 'Commits', 'Repository']
    ).properties(width=800, height=400)
    st.altair_chart(heatmap_with_repo, use_container_width=True)

    # Scatter plot visualization
    st.markdown("<h3 style='text-align: center;'>Scatter Plot</h3>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(12, 8))
    for dev in developers:
        dev_data = commit_details_df[commit_details_df['Developer'] == dev]
        ax.scatter(dev_data['Date'], [dev] * len(dev_data), s=dev_data['Commits'] * 10, label=dev, alpha=0.6)

    ax.set_xlabel('Date')
    ax.set_ylabel('Developer')
    ax.set_title('Commits per Developer Over Time')
    ax.legend(loc='upper right')
    plt.tight_layout()
    st.pyplot(fig)

    # Altair chart visualization
    st.markdown("<h3 style='text-align: center;'>Altair Chart</h3>", unsafe_allow_html=True)
    circle_plot = alt.Chart(commit_details_df).mark_circle(size=60).encode(
        x=alt.X('Developer:N', title='Developer'),
        y=alt.Y('Date:T', title='Date'),
        color=alt.Color('Commits:Q', scale=alt.Scale(scheme='viridis'), legend=alt.Legend(title="Commits")),
        tooltip=['Date', 'Developer', 'Commits', 'Repository']
    ).properties(width=800, height=400)
    st.altair_chart(circle_plot, use_container_width=True)

    # Line chart visualization
    st.markdown("<h3 style='text-align: center;'>Line Chart</h3>", unsafe_allow_html=True)
    commit_details_df['Cumulative Commits'] = commit_details_df.groupby('Developer')['Commits'].cumsum()
    line_chart = alt.Chart(commit_details_df).mark_line().encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('Cumulative Commits:Q', title='Cumulative Commits'),
        color=alt.Color('Developer:N', title='Developer'),
        tooltip=['Date', 'Developer', 'Cumulative Commits', 'Repository']
    ).properties(width=800, height=400)
    st.altair_chart(line_chart, use_container_width=True)

    # Bar chart visualization
    st.markdown("<h3 style='text-align: center;'>Altair Bar Chart</h3>", unsafe_allow_html=True)
    commit_details_df['Date'] = pd.to_datetime(commit_details_df['Date'])
    commit_details_df['Month'] = commit_details_df['Date'].dt.to_period('M')
    commit_details_df['Month'] = commit_details_df['Month'].dt.to_timestamp()

    bar_chart = alt.Chart(commit_details_df).mark_bar().encode(
        x=alt.X('Month:T', title='Month'),
        y=alt.Y('sum(Commits):Q', title='Total Commits'),
        color=alt.Color('Developer:N', title='Developer'),
        column='Developer:N',
        tooltip=['Month:T', 'Developer:N', 'sum(Commits):Q', 'Repository:N']
    ).properties(width=200, height=400)
    st.altair_chart(bar_chart, use_container_width=False)