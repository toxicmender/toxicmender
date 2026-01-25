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
  "updated_at": "2025-01-20T10:30:00",
  "latest_commit": "abc123...",
  "cached_at": "2025-01-26T12:00:00"
}
```

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
