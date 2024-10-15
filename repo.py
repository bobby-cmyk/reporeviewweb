import os
import base64
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get GitHub token from environment
token = os.getenv("GITHUB_TOKEN")
owner = "bobby-cmyk"  # Replace with the repository owner
repo = "fortunecookie"    # Replace with the repository name
ref = "main"     # Optional, set your branch, commit, or tag; default is the default branch

# Check if the token was loaded correctly
if not token:
    raise ValueError("GITHUB_TOKEN not found in .env file")

# Define the GitHub API URL for the Git Tree API (recursive)
url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{ref}?recursive=1"

# Set up headers
headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {token}",
    "X-GitHub-Api-Version": "2022-11-28"
}

# Make the GET request to the Git Trees API
response = requests.get(url, headers=headers)

# Handle response for recursive file listing
if response.status_code == 200:
    print("Request successful (200 OK)!")
    content = response.json()

    # Extract the paths of all Java files
    java_files = [item['path'] for item in content['tree'] if item['type'] == 'blob' and item['path'].endswith('.java')]

    print("Found Java files:")
    for java_file in java_files:
        print(f"- {java_file}")

    # Function to fetch and print Java file content
    def fetch_and_print_java_file(file_path):
        file_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        file_response = requests.get(file_url, headers=headers, params={"ref": ref})

        # Handle the response
        if file_response.status_code == 200:
            file_content = file_response.json().get('content')
            if file_content:
                # Decode the Base64 content to plain text
                decoded_content = base64.b64decode(file_content).decode('utf-8')
                print(f"--- {file_path} ---")
                print(decoded_content)  # Print the content of the Java file
                print("\n")
            else:
                print(f"No content found in the file: {file_path}")
        else:
            print(f"Failed to fetch {file_path}, status code: {file_response.status_code}")
            print(file_response.text)

    # Iterate over the list of Java files and fetch each one
    for java_file in java_files:
        fetch_and_print_java_file(java_file)

else:
    print(f"Failed to retrieve file tree, status code: {response.status_code}")
    print(response.text)

