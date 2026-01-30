# Pull Request and Code Review Metrics

## Overview

This feature adds comprehensive pull request and code review metrics to the GitHub repository analytics system. It tracks PR velocity, merge quality, review engagement, and collaboration patterns.

## New Metrics

### PR Review Metric (`pr_review`)

Tracks overall pull request activity and collaboration:

**Dimensions:**
- **PR Velocity**: Number of merged pull requests
- **PR Quality**: Merge rate (merged PRs / total PRs)
- **Review Engagement**: Average number of reviews per PR
- **Collaboration**: Number of unique reviewers across all PRs

**Formulas:**
```
PR Velocity = count(merged_prs)
PR Quality = merged_prs / total_prs
Review Engagement = total_reviews / total_prs
Collaboration = count(unique_reviewers)
```

### Code Review Metric (`code_review`)

Evaluates code review quality and thoroughness:

**Dimensions:**
- **Review Thoroughness**: Average comments per PR
- **Review Coverage**: Percentage of PRs with at least one review
- **Reviewer Diversity**: Ratio of unique reviewers to total PRs
- **Merge Efficiency**: Average time to merge (in hours)

**Formulas:**
```
Review Thoroughness = total_comments / total_prs
Review Coverage = min(1.0, prs_with_reviews / total_prs)
Reviewer Diversity = unique_reviewers / total_prs
Merge Efficiency = avg(merge_time_hours)
```

## Data Collection

### GitHub API Integration

PR metrics are collected using PyGithub's `get_pulls()` API:
- Fetches all PRs (open and closed) for each repository
- Limited to 100 most recent PRs to manage API rate limits
- Collects: PR state, merge status, review counts, comment counts, reviewers

### Cached Data Structure

```python
PRMetrics(
    pr_count=25,                      # Total PRs
    pr_merged_count=22,               # Successfully merged
    pr_closed_count=3,                # Closed without merge
    avg_pr_merge_time_hours=36.5,    # Average hours to merge
    pr_review_count=60,               # Total reviews across all PRs
    avg_reviews_per_pr=2.4,           # Mean reviews per PR
    pr_comments_count=150,            # Total comments
    unique_reviewers=10               # Distinct reviewer count
)
```

## Visualizations

### PR Metrics Chart (`charts/pr_metrics.png`)

4-panel visualization:
1. **Top Repositories by PR Velocity**: Horizontal bar chart of merged PRs
2. **Review Engagement Distribution**: Histogram of reviews per PR
3. **PR Quality Distribution**: Violin plot of merge rates
4. **Collaboration vs PR Velocity**: Scatter plot showing relationship

### Review Engagement Chart (`charts/review_engagement.png`)

2-panel visualization:
1. **Review Coverage by Repository**: Horizontal bar chart with threshold lines
2. **Thoroughness vs Diversity**: Scatter plot colored by coverage percentage

## Configuration

### Metric Weights (`analytics/config/weights.yml`)

```yaml
metric_weights:
  pr_review: 0.10      # 10% of engineering score
  code_review: 0.10    # 10% of engineering score
  # ... other metrics adjusted to sum to 1.0
```

### Quality Thresholds (`analytics/config/pr_thresholds.yml`)

Defines excellent/good/acceptable/poor levels for each dimension:

```yaml
pr_review:
  pr_velocity:
    excellent: 50    # 50+ merged PRs
    good: 20
    acceptable: 5
    poor: 0

  pr_quality:
    excellent: 0.80  # 80%+ merge rate
    good: 0.60
    acceptable: 0.40
    poor: 0.0
```

## Authentication

### GitHub Token Setup

**Required for**: Comprehensive PR data access and higher rate limits

**Setup**:
1. Create token at https://github.com/settings/tokens
2. Required scopes: `repo` or `public_repo`
3. Configure using one of:
   - Environment variable: `GITHUB_TOKEN=your_token`
   - `.env` file: Copy `.env.example` and add token
   - Command line: `--token your_token`

**Rate Limits**:
- Without token: 60 requests/hour
- With token: 5,000 requests/hour

See [docs/GITHUB_TOKEN_SETUP.md](../docs/GITHUB_TOKEN_SETUP.md) for detailed instructions.

## Usage

### Running Analysis with PR Metrics

```bash
# Set up authentication (recommended)
export GITHUB_TOKEN=your_token_here

# Run full analysis (includes PR metrics automatically)
uv run main.py run --username your-username

# PR data is collected, analyzed, and visualized automatically
```

### Accessing PR Metrics in Code

```python
from analytics.metrics import PRReviewMetric, CodeReviewMetric
from analytics.models.repo import RepoStats, PRMetrics

# Create metrics
pr_metric = PRReviewMetric()
code_metric = CodeReviewMetric()

# Compute for repositories
pr_result = pr_metric.compute(repos)
code_result = code_metric.compute(repos)

# Access dimensions
velocities = pr_result.values['pr_velocity']
qualities = pr_result.values['pr_quality']
```

## Testing

### Unit Tests

```bash
# Test PR review metric
pytest analytics/tests/metrics/test_pr_review.py

# Test code review metric
pytest analytics/tests/metrics/test_code_review.py

# Run all tests
pytest analytics/tests/
```

### Test Coverage

- **Edge cases**: Repos with 0 PRs, None PR metrics
- **Calculations**: All metric formulas verified
- **Data structures**: PRMetrics validation
- **API mocking**: Simulated GitHub responses

## Integration with Existing System

### Pipeline Flow

```
1. Collection (analytics.pipeline.collect)
   ├─ GitHubSource fetches repos + PR data
   └─ Data cached to data/{username}/repos_cache/*.json

2. Analysis (analytics.pipeline.analyse)
   ├─ PRReviewMetric computes PR velocity, quality, etc.
   ├─ CodeReviewMetric computes review quality metrics
   └─ Results saved to data/metrics.json

3. Visualization (analytics.pipeline.visualize)
   ├─ PRMetricsChart generates pr_metrics.png
   └─ ReviewEngagementChart generates review_engagement.png

4. Rendering (analytics.pipeline.render)
   └─ README.md includes PR/review sections
```

### Model Updates

- **RepoStats**: Added optional `pr_metrics: PRMetrics` field
- **PRMetrics**: New model for PR data (frozen, validated)
- **Backward compatible**: Existing repos without PR data work seamlessly

## Performance Considerations

### API Rate Limits

- Each repository requires ~3-5 additional API calls for PR data
- Limited to 100 PRs per repo to avoid excessive calls
- Cached data prevents repeated fetches
- Token authentication highly recommended for 50+ repos

### Optimization Strategies

1. **Caching**: PR data cached with repository data
2. **Pagination**: Limited to recent PRs (configurable)
3. **Lazy loading**: Only fetches when needed
4. **Graceful degradation**: Missing PR data doesn't break analysis

## Limitations

1. **PR Limit**: Analyzes most recent 100 PRs per repository
2. **Review Timing**: First review time not currently tracked
3. **Reviewer Details**: Names cached but not full profiles
4. **Private Repos**: Requires token with `repo` scope

## Future Enhancements

- [ ] Time-series tracking of PR metrics over time
- [ ] PR size analysis (lines changed per PR)
- [ ] Review response time (time to first review)
- [ ] PR categorization (feature/bugfix/refactor)
- [ ] Reviewer network graph visualization
- [ ] Compare PR metrics across time periods

## Troubleshooting

### "No Pull Request Data Available" in charts
- **Cause**: Repositories have no merged PRs
- **Solution**: This is normal for repos without PR activity

### PR metrics all showing as 0
- **Cause**: Authentication issue or API rate limit
- **Solution**: Add GitHub token and check logs for errors

### Slow data collection
- **Cause**: Fetching PR data for many repositories
- **Solution**: Use token for better rate limits, be patient (PR data takes time)

## References

- **PR Review Metric**: [analytics/metrics/pr_review.py](../analytics/metrics/pr_review.py)
- **Code Review Metric**: [analytics/metrics/code_review.py](../analytics/metrics/code_review.py)
- **Data Model**: [analytics/models/repo.py](../analytics/models/repo.py)
- **Visualization**: [analytics/charts/pr_metrics.py](../analytics/charts/pr_metrics.py)
- **Tests**: [analytics/tests/metrics/test_pr_review.py](../analytics/tests/metrics/test_pr_review.py)
