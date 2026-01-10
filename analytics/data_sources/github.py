from analytics.data_sources.base import DataSource


class GitHubSource(DataSource):
    def fetch(self):
        return {
            "repos": self._fetch_repos(),
            "events": self._fetch_events()
        }
