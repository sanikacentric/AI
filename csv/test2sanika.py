import os
os.environ['GITHUB_TOKEN'] = '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'
from github import Github
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
# Step 1: Authenticate to GitHub
token = os.getenv('GITHUB_TOKEN')
if not token:
   raise Exception("GitHub token not found. Please set the GITHUB_TOKEN environment variable.")
g = Github(token)
# Step 2: Define Parameters
org_name = 'sanikacentric'   # Replace with your organization name or username
repo_name = 'streamlit' # Replace with your repository name
start_date = datetime.now() - timedelta(days=30)  # Last 30 days
end_date = datetime.now()
# Step 3: Fetch Repository Data
repo = g.get_repo(f"sanikacentric/streamlit")
# Step 4: Initialize Data Collection
developer_data = {}
# Step 5: Iterate Over Commits
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
# Step 6: Print and Visualize the Data
print("Developer Productivity Report (Last 30 Days):")
for developer, data in developer_data.items():
   print(f"{developer}: {data['commits']} commits, {data['additions']} additions, {data['deletions']} deletions")
# Step 7: Plot Data
developers = list(developer_data.keys())
commits = [developer_data[dev]['commits'] for dev in developers]
additions = [developer_data[dev]['additions'] for dev in developers]
deletions = [developer_data[dev]['deletions'] for dev in developers]
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