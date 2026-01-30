# Caching Implementation

## Overview

The data collection pipeline now implements per-repository caching to handle GitHub API rate limits and resume progress efficiently.

## Features

### 1. Per-Repository Caching
Each repository is cached as an individual JSON file in `data/{username}/repos_cache/`:
```
data/
  username/
    repos_cache/
      repo1.json
      repo2.json
      repo3.json
```

### 2. Rate Limit Handling
- When rate limits are hit, the system automatically falls back to cached data
- Progress is saved after each successful repository fetch
- You can resume data collection without re-fetching already cached repos

### 3. Cache Invalidation
Cache is automatically invalidated when:
- Repository `updated_at` timestamp changes
- Latest commit hash differs from cached version

This ensures you always get fresh data when repositories are updated.

## Usage

### Basic Usage
```bash
# Collect data with caching
uv run main.py collect-data --username "your-username"
```

### With GitHub Token (Recommended)
For higher rate limits, provide a GitHub personal access token:
```bash
# With token for higher rate limits
uv run main.py collect-data --username "your-username" --token "your-github-token"
```

### Resume After Rate Limit
If you hit rate limits, simply run the command again:
```bash
# Will use cached data and only fetch missing/updated repos
uv run main.py collect-data --username "your-username"
```

## Cache Structure

Each cached repository file contains:
```json
{
  "name": "repo-name",
  "loc": 5000,
  "commits": 100,
  "stars": 50,
  "forks": 10,
  "languages": {
    "Python": 3000,
    "JavaScript": 2000
  },
  "pr_metrics": {
    "pr_count": 25,
    "pr_merged_count": 22,
    "pr_closed_count": 3,
    "avg_pr_merge_time_hours": 36.5,
    "pr_review_count": 60,
    "avg_reviews_per_pr": 2.4,
    "pr_comments_count": 150,
    "unique_reviewers": 10
  },
  "updated_at": "2025-01-20T10:30:00",
  "latest_commit": "abc123...",
  "cached_at": "2025-01-26T12:00:00"
}
```

### PR Metrics Caching

Pull request data is cached alongside repository metrics:
- **PR counts**: Total, merged, and closed PRs
- **Review statistics**: Review counts, average reviews per PR, unique reviewers
- **Merge timing**: Average time to merge PRs
- **Comments**: Total comment count across all PRs

PR data is limited to the most recent 100 PRs per repository to avoid excessive API calls and storage.

**Note**: PR metrics are fetched with each repository but cached separately. If you need to refresh only PR data, delete the cached file for that repository.

## Benefits

1. **Resilient to Rate Limits**: Automatically resume from where you left off
2. **Faster Subsequent Runs**: Only re-fetch updated repositories
3. **No Data Loss**: All fetched data is preserved even if collection is interrupted
4. **Transparent**: Cache validation happens automatically

## Implementation Details

### GitHubSource
- `_fetch_or_load_repo()`: Checks cache validity before fetching
- `_is_cache_valid()`: Validates cache using timestamp and commit hash
- `_save_to_cache()`: Saves individual repo data after successful fetch

### CacheDataSource
- Supports both single-file (legacy) and directory-based caching
- Loads all JSON files from cache directory
- Gracefully handles corrupt cache files

### Pipeline Integration
The collect pipeline automatically:
1. Uses GitHubSource with per-repo caching
2. Falls back to CacheDataSource if GitHub fetch fails
3. Merges cached and fresh data transparently
