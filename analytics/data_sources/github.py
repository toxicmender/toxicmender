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
                # Get languages with their line counts
                languages = repo.get_languages()

                # Calculate total LOC from all languages
                loc = sum(languages.values()) if languages else 1

                result.append({
                    "name": repo.name,
                    "loc": loc,
                    "commits": repo.get_commits().totalCount,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "languages": languages if languages else {}
                })

            return result
        except GithubException as e:
            raise DataSourceError(
                f"Failed to fetch repos for {self.username} via GitHub API: {e}"
            ) from e
        except Exception as e:
            raise DataSourceError(
                f"Failed to fetch repos for {self.username} due to unexpected error {e}"
            ) from e