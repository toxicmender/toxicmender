from analytics.data_sources.base import DataSource
from analytics.exceptions import DataSourceError
from analytics.utils.validation import require_non_empty
from github import Github, GithubException


class GitHubSource(DataSource):
    def __init__(self, username: str):
        require_non_empty(username, "username")
        self.username = username
        self.client = Github()

    def fetch(self):
        try:
            user = self.client.get_user(self.username)
            repos = user.get_repos()

            result = []
            for repo in repos:
                result.append({
                    "name": repo.name,
                    "stargazerCount": repo.stargazers_count
                })

            return result
        except GithubException as e:
            raise DataSourceError(
                f"Failed to fetch repos for {self.username}"
            ) from e
        except Exception as e:
            raise DataSourceError(
                f"Failed to fetch repos for {self.username}"
            ) from e