import os
import streamlit as st
from github import Github
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# GitHub Token Environment Variable
os.environ['GITHUB_TOKEN'] = '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'
token = os.getenv('GITHUB_TOKEN')
if not token:
    raise Exception("GitHub token not found. Please set the GITHUB_TOKEN environment variable.")
g = Github(token)

# Streamlit App Title
st.title("GitHub Developer Productivity")

# Dropdown for Organization and Repository Selection
org_name = st.sidebar.text_input("Enter Organization Name:", value="sanikacentric")
repo_name = st.sidebar.text_input("Enter Repository Name:", value="streamlit")

# Date Range
days = st.sidebar.slider("Select the number of days:", min_value=1, max_value=365, value=30)
start_date = datetime.now() - timedelta(days=days)
end_date = datetime.now()

# Fetch Organization and Repository Data
#try:
   # org = g.get_organization(org_name)
    #repo = g.get_repo(f"{org_name}/{repo_name}")
#except Exception as e:
    #st.error(f"Error fetching data: {e}")
    #st.stop()

#members = org.get_members()
#developer_info = {member.login: {'name': member.name, 'github_id': member.login} for member in members}
# Step 3: Fetch Repository Data
repo = g.get_repo(f"sanikacentric/streamlit")

# Initialize Data Collection
developer_data = {}

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
