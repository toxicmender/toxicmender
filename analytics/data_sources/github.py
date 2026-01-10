from analytics.data_sources.base import DataSource
from analytics.exceptions import DataSourceError
from analytics.utils.validation import require_non_empty
import subprocess, json

class GitHubSource(DataSource):
    def __init__(self, username: str):
        require_non_empty(username, "username")
        self.username = username

    def fetch(self):
        try:
            out = subprocess.check_output(
                ["gh", "repo", "list", self.username, "--json", "name,stargazerCount"],
                text=True
            )
            return json.loads(out)
        except subprocess.CalledProcessError as e:
            raise DataSourceError(
                f"Failed to fetch repos for {self.username}"
            ) from e
        except json.JSONDecodeError as e:
            raise DataSourceError(
                f"Failed to parse JSON response for {self.username}"
            ) from e