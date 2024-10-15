import os
import base64
import requests

class GitHubRepoReader:
    def __init__(self, owner, repo, token, ref="main"):
        self.owner = owner
        self.repo = repo
        self.token = token
        self.ref = ref
        self.base_url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    def get_file_tree(self):
        """Fetches the file tree of the repository recursively"""

        print(">>> Fetching directory structure of repository\n")

        url = f"{self.base_url}/git/trees/{self.ref}?recursive=1"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get('tree', [])
        else:
            print(f"Failed to retrieve file tree, status code: {response.status_code}")
            print(response.text)
            return []

    def fetch_file_content(self, file_path):
        """Fetches the content of a file from the GitHub repository"""

        print(">>> Reading your java code in %s\n",file_path)

        url = f"{self.base_url}/contents/{file_path}"
        response = requests.get(url, headers=self.headers, params={"ref": self.ref})
        if response.status_code == 200:
            file_content_base64 = response.json().get('content')
            if file_content_base64:
                return base64.b64decode(file_content_base64).decode('utf-8')
            else:
                print(f"No content found in the file: {file_path}")
                return None
        else:
            print(f"Failed to fetch {file_path}, status code: {response.status_code}")
            print(response.text)
            return None
