import os
os.environ['GITHUB_TOKEN'] = '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'
from github import Github, GithubException  # Ensure GithubException is imported
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Step 1: Authenticate to GitHub
token = os.getenv('GITHUB_TOKEN')
if not token:
    raise Exception("GitHub token not found. Please set the GITHUB_TOKEN environment variable.")
g = Github(token)

# Step 2: Define Parameters
org_name = 'sanikacentric'  # Replace with your organization name
start_date = datetime.now() - timedelta(days=30)  # Last 30 days
end_date = datetime.now()

# Step 3: Fetch Organization Members
try:
    org = g.get_organization(org_name)
except GithubException as e:
    if e.status == 404:
        print(f"Organization '{org_name}' not found. Please check the organization name.")
    else:
        print(f"An error occurred: {e}")
    exit(1)

members = org.get_members()
developer_info = {member.login: {'name': member.name, 'github_id': member.login} for member in members}

# Step 4: Fetch Repositories for the Organization
repos = org.get_repos()

# Step 5: Initialize Data Collection
developer_data = {}

# Step 6: Iterate Over Repositories and Commits
for repo in repos:
    print(f"Processing repository: {repo.name}")
    for commit in repo.get_commits(since=start_date, until=end_date):
        author = commit.author.login if commit.author else 'Unknown'
        if author in developer_info:
            author_name = developer_info[author]['name'] or author
            author_github_id = developer_info[author]['github_id']
        else:
            author_name = 'Unknown'
            author_github_id = 'Unknown'
        
        additions = commit.stats.additions
        deletions = commit.stats.deletions
        total_changes = additions + deletions

        if author not in developer_data:
            developer_data[author] = {
                'name': author_name,
                'github_id': author_github_id,
                'commits': 0, 
                'additions': 0, 
                'deletions': 0, 
                'total_changes': 0
            }
        
        developer_data[author]['commits'] += 1
        developer_data[author]['additions'] += additions
        developer_data[author]['deletions'] += deletions
        developer_data[author]['total_changes'] += total_changes

# Step 7: Print and Visualize the Data
print("Developer Productivity Report (Last 30 Days):")
for developer, data in developer_data.items():
    print(f"{data['name']} (GitHub ID: {data['github_id']}): {data['commits']} commits, {data['additions']} additions, {data['deletions']} deletions")

# Step 8: Plot Data
developers = [data['name'] for data in developer_data.values()]
commits = [data['commits'] for data in developer_data.values()]
additions = [data['additions'] for data in developer_data.values()]
deletions = [data['deletions'] for data in developer_data.values()]

plt.figure(figsize=(10, 6))
plt.bar(developers, commits, color='blue', alpha=0.6, label='Commits')
plt.bar(developers, additions, color='green', alpha=0.6, label='Additions')
plt.bar(developers, deletions, color='red', alpha=0.6, label='Deletions')
plt.xlabel('Developers')
plt.ylabel('Count')
plt.title('Developer Productivity Report')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
