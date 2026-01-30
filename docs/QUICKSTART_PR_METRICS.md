# Quick Start: Pull Request Metrics

Get started with PR and Code Review metrics in 3 steps!

## Step 1: Set Up GitHub Token (2 minutes)

### Why?
- **Higher rate limits**: 5,000 requests/hour vs 60 without token
- **Better PR data**: Access to detailed review information

### How?

**Option A: Environment Variable (Easiest)**
```bash
# Windows PowerShell
$env:GITHUB_TOKEN="your_token_here"

# Linux/Mac
export GITHUB_TOKEN="your_token_here"
```

**Option B: .env File**
```bash
# 1. Copy example file
cp .env.example .env

# 2. Edit .env and add your token
# GITHUB_TOKEN=your_token_here
```

**Get a token**: https://github.com/settings/tokens
- Scope needed: `public_repo` (or `repo` for private repos)

## Step 2: Run the Analysis (1 command)

```bash
uv run main.py run --username your-github-username
```

That's it! PR metrics are collected, analyzed, and visualized automatically.

## Step 3: View Results

Your analysis includes:

### New Visualizations
- `charts/pr_metrics.png` - PR velocity, quality, collaboration
- `charts/review_engagement.png` - Review coverage and thoroughness

### New Sections in README.md
- **PR Review Metric** - Velocity, quality, engagement, collaboration
- **Code Review Metric** - Thoroughness, coverage, diversity, efficiency
- **Top Repositories by PR Activity** - Most active PR repos

### New Data in metrics.json
```json
{
  "pr_review": {
    "values": {
      "pr_velocity": [...],
      "pr_quality": [...],
      "review_engagement": [...],
      "collaboration": [...]
    }
  },
  "code_review": {
    "values": {
      "review_thoroughness": [...],
      "review_coverage": [...],
      "reviewer_diversity": [...],
      "merge_efficiency": [...]
    }
  }
}
```

## What Gets Analyzed?

For each repository with PRs:
- ✅ Total PRs (merged, closed)
- ✅ Average merge time
- ✅ Review counts per PR
- ✅ Comment counts
- ✅ Unique reviewers
- ✅ Merge rates
- ✅ Review coverage

**Note:** Analyzes the 100 most recent PRs per repository.

## Troubleshooting

### "API rate limit exceeded"
```bash
# Add a GitHub token - see Step 1 above
```

### "No Pull Request Data Available" in charts
- This is normal! It means your repos don't have merged PRs
- The feature is working correctly

### Token not detected
```bash
# Check spelling (case sensitive):
echo $GITHUB_TOKEN  # Linux/Mac
echo $env:GITHUB_TOKEN  # Windows PowerShell

# Restart terminal after setting env variable
```

## Learn More

- **Full Documentation**: [docs/PR_METRICS.md](PR_METRICS.md)
- **Token Setup Guide**: [docs/GITHUB_TOKEN_SETUP.md](GITHUB_TOKEN_SETUP.md)
- **Implementation Details**: [docs/IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

## Example Output

### PR Metrics Summary
```
PR Review Metric:
- Total PRs Merged: 156
- Average Merge Rate: 87.3%
- Average Reviews per PR: 2.4
- Unique Reviewers: 12

Code Review Metric:
- Average Comments per PR: 8.5
- Review Coverage: 94.2%
- Reviewer Diversity: 0.58
- Average Merge Time: 18.5 hours
```

---

**Time to complete**: ~5 minutes (setup) + analysis time (varies by repo count)
**Difficulty**: Beginner-friendly
**Dependencies**: GitHub token (optional but recommended)

Happy analyzing! 🚀
