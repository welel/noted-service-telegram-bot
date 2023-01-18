"""A module for making requests to GITHUB API."""
import requests
from typing import Optional, List

from config import GITHUB_TOKEN, REPO_OWNER, REPO_NAME


HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": "Bearer {gh_token}".format(gh_token=GITHUB_TOKEN),
    "X-GitHub-Api-Version": "2022-11-28",
}

LIST_COMMITS_API_URL = "https://api.github.com/repos/{owner}/{repo}/commits"


def get_commits(num: int = 3) -> Optional[List[dict]]:
    """Makes API call to get last commits of a repository.

    Attrs:
        num: number of commits.
    Returns:
        list: return list of dicts with commit info
              (keys - "sha", "comment", "url")
    """
    URL = LIST_COMMITS_API_URL.format(owner=REPO_OWNER, repo=REPO_NAME)
    URL += f"?per_page={num}"
    try:
        response = requests.get(URL, headers=HEADERS)
    except requests.exceptions.ConnectionError as erorr:
        print(erorr)
        return
    commits = []
    for commit in response.json():
        commits.append(
            {
                "sha": commit["sha"],
                "comment": commit["commit"]["message"],
                "url": commit["html_url"],
            }
        )
    return commits
