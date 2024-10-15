import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from github_repo_reader import GitHubRepoReader
from gpt_feedback_provider import GPTFeedbackProvider  # Import the GPTFeedbackProvider class
import textwrap
# Load environment variables from .env file
load_dotenv()

# Extract owner and repository name from a GitHub URL
def extract_owner_and_repo(github_url):
    """Extracts the owner and repository name from the GitHub URL"""
    parsed_url = urlparse(github_url)
    path_parts = parsed_url.path.strip("/").split("/")
    if len(path_parts) >= 2:
        owner = path_parts[0]
        repo = path_parts[1]
        return owner, repo
    else:
        raise ValueError("Invalid GitHub URL format. Expected format: https://github.com/owner/repo")
    
def print_formatted_feedback(feedback):
    # Set the width for text wrapping (e.g., 80 characters per line)
    wrapper = textwrap.TextWrapper(width=80)

    # Header for the feedback
    print("\n--- GPT Feedback ---\n")

    # Wrap and print each paragraph in the feedback
    for line in feedback.splitlines():
        # If the line is not empty, wrap and print it
        if line.strip():
            print(wrapper.fill(line))
        else:
            # Print an empty line as it is
            print()

    print("\n--- End of Feedback ---\n")

if __name__ == "__main__":
    # Input repository URL from the terminal
    print(">>> Welcome to RepoReview!")
    repo_url = input(">>> Enter the GitHub repository URL: ")

    # Extract owner and repo from the URL
    try:
        owner, repo = extract_owner_and_repo(repo_url)
    except ValueError as e:
        print(e)
        exit(1)

    # Load GitHub token from .env file
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN not found in .env file")

    # Load OpenAI API key from .env file
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file")

    # Create an instance of the GitHubRepoReader class
    github_reader = GitHubRepoReader(owner, repo, token)

    # Fetch the directory structure and Java files content
    tree = github_reader.get_file_tree()

    
    if not tree:
        print("No files found in the repository.")
        exit(1)

    directory_structure = ""
    java_files_content = ""
    java_files = []

    # Build directory structure and collect Java file content
    for item in tree:
        directory_structure += f"- {item['path']} ({item['type']})\n"
        if item['type'] == 'blob' and item['path'].endswith('.java'):
            java_files.append(item['path'])

    # Fetch and append the content of each Java file
    for java_file in java_files:
        java_content = github_reader.fetch_file_content(java_file)
        if java_content:
            java_files_content += f"\n--- {java_file} ---\n{java_content}\n"

    if java_files_content:
        print(">>> Sending content to GPT for feedback...\n")
        
        # Create an instance of the GPTFeedbackProvider class
        gpt_feedback = GPTFeedbackProvider(api_key=openai_api_key)
        
        # Send the directory structure and Java files content to GPT
        feedback = gpt_feedback.get_feedback(directory_structure, java_files_content)
        
        print_formatted_feedback(feedback)
    else:
        print(">>> No Java files found to analyze.")


