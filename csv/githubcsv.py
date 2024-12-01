import requests
import csv

# GitHub API URL for commits
GITHUB_API_URL = 'https://api.github.com/repos/sanikacentric/Code1/commits'

# Replace with your repository details
owner = 'sanikacentric'
repo = 'Code1'

# GitHub API request
response = requests.get(GITHUB_API_URL.format(owner=owner, repo=repo))

# Check if the response is successful
if response.status_code == 200:
    commits = response.json()

    # Open a CSV file to write the data
    with open('github_commits.csv', 'w', newline='') as csvfile:
        fieldnames = ['sha', 'author_name', 'author_email', 'message', 'date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the headers
        writer.writeheader()

        # Write commit data to the CSV file
        for commit in commits:
            writer.writerow({
                'sha': commit['sha'],
                'author_name': commit['commit']['author']['name'],
                'author_email': commit['commit']['author']['email'],
                'message': commit['commit']['message'],
                'date': commit['commit']['author']['date']
            })

    print("CSV file created successfully.")
else:
    print(f"Failed to fetch data from GitHub. Status code: {response.status_code}")
