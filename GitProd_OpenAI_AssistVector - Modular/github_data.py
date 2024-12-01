import os
from github import Github
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st



# Initialize GitHub client
def init_github_client():
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        raise Exception("GitHub token not found. Please set the GITHUB_TOKEN environment variable.")
    return Github(token)

# Fetch the repository object
def fetch_repo(org_name, repo_name):
    g = init_github_client()
    repo = g.get_repo(f"{org_name}/{repo_name}")
    return repo, g.get_user().get_repos().totalCount

# Fetch issues within the date range
def fetch_issues(repo, start_date, end_date):
    issues = repo.get_issues(state='all', since=start_date)
    return issues

# Fetch pull requests within the date range
def fetch_pull_requests(repo, start_date, end_date):
    pulls = repo.get_pulls(state='closed', sort='created', direction='desc', base='main')
    filtered_pulls = [pull for pull in pulls if pull.created_at >= start_date and pull.created_at <= end_date]
    return filtered_pulls

# Fetch commits within the date range
def fetch_commits(repo, start_date, end_date):
    commits = repo.get_commits(since=start_date, until=end_date)
    return commits

# Process issues and populate developer data
def process_issues(issues, developer_data):
    for issue in issues:
        creator = issue.user.login if issue.user else 'Unknown'
        assignees = [assignee.login for assignee in issue.assignees] if issue.assignees else []
        
        if creator not in developer_data:
            developer_data[creator] = create_initial_developer_record()

        developer_data[creator]['issues_created'] += 1
        
        for assignee in assignees:
            if assignee not in developer_data:
                developer_data[assignee] = create_initial_developer_record()
            developer_data[assignee]['issues_assigned'] += 1
        
        if issue.state == 'closed':
            closer = issue.closed_by.login if issue.closed_by else 'Unknown'
            if closer not in developer_data:
                developer_data[closer] = create_initial_developer_record()
            developer_data[closer]['issues_resolved'] += 1

# Process pull requests and populate developer data
def process_pull_requests(pulls, developer_data):
    for pull in pulls:
        author = pull.user.login if pull.user else 'Unknown'
        if author not in developer_data:
            developer_data[author] = create_initial_developer_record()

        developer_data[author]['prs_created'] += 1
        if pull.merged_at:
            developer_data[author]['prs_merged'] += 1
        if pull.state == 'closed':
            developer_data[author]['prs_closed'] += 1

        # Process reviews in the pull request
        reviews = pull.get_reviews()
        for review in reviews:
            reviewer = review.user.login if review.user else 'Unknown'
            if reviewer not in developer_data:
                developer_data[reviewer] = create_initial_developer_record()
            developer_data[reviewer]['code_reviews'] += 1

# Process commits and populate developer data
def process_commits(commits, developer_data, repo_name, days):
    developer_texts = []
    for commit in commits:
        author = commit.author.login if commit.author else 'Unknown'
        additions = commit.stats.additions
        deletions = commit.stats.deletions
        total_changes = additions + deletions
        files = [file.filename for file in commit.files]
        commit_date = commit.commit.author.date  # Get the commit date

        if author not in developer_data:
            developer_data[author] = create_initial_developer_record()

        developer_data[author]['commits'] += 1
        developer_data[author]['additions'] += additions
        developer_data[author]['deletions'] += deletions
        developer_data[author]['total_changes'] += total_changes
        developer_data[author]['commit_frequency'] = developer_data[author]['commits'] / days
        developer_data[author]['affected_files'].update(files)

        commit_detail = {
            'commit_message': commit.commit.message,
            'additions': additions,
            'deletions': deletions,
            'total_changes': total_changes,
            'commit_date': commit_date.strftime('%Y-%m-%d %H:%M:%S'),  # Format the date
        }
        developer_data[author]['commit_details'].append(commit_detail)

        developer_texts.append(f"{author} made the following commit in {repo_name}: {commit_detail['commit_message']}")

        if "merge" in commit.commit.message.lower():
            developer_data[author]['commit_merge'] += 1

    return developer_texts

# Create the initial structure for each developer
def create_initial_developer_record():
    return {
        'commits': 0,
        'additions': 0,
        'deletions': 0,
        'total_changes': 0,
        'commit_frequency': 0,
        'commit_details': [],
        'prs_created': 0,
        'prs_open': 0,
        'prs_merged': 0,
        'prs_closed': 0,
        'prs_reviewed': 0,
        'code_reviews': 0,
        'issues_created': 0,
        'issues_assigned': 0,
        'issues_resolved': 0,
        'affected_files': set(),
        'commit_merge': 0,
    }

# Convert developer data to a pandas DataFrame for tabular display
def create_developer_df(developer_data):
    developer_df = pd.DataFrame.from_dict(developer_data, orient='index')
    developer_df.reset_index(inplace=True)
    developer_df.rename(columns={'index': 'Developer'}, inplace=True)
    developer_df['affected_files'] = developer_df['affected_files'].apply(lambda x: ', '.join(x))
    return developer_df
