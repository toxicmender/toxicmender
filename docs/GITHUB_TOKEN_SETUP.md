# GitHub Token Authentication Setup

## Overview

This project supports GitHub Personal Access Tokens for authenticated API access, providing:
- **Higher rate limits**: 5,000 requests/hour (vs 60 for unauthenticated)
- **Access to private repositories**: View your private repos if needed
- **Better PR/review data**: More detailed pull request information

## Setup Instructions

### 1. Create a GitHub Personal Access Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token" (classic)
3. Give it a descriptive name (e.g., "GitHub Analytics Tool")
4. Select the following scopes:
   - `repo` (if you want to analyze private repositories)
   - `public_repo` (if analyzing only public repositories)
5. Click "Generate token"
6. **Copy the token immediately** (you won't be able to see it again)

### 2. Configure the Token

Choose one of the following methods:

#### Option A: Environment Variable (Recommended)

**Windows PowerShell:**
```powershell
$env:GITHUB_TOKEN="your_token_here"
```

**Windows Command Prompt:**
```cmd
set GITHUB_TOKEN=your_token_here
```

**Linux/Mac:**
```bash
export GITHUB_TOKEN="your_token_here"
```

#### Option B: .env File

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your token:
   ```
   GITHUB_TOKEN=your_token_here
   ```

3. Make sure `.env` is in your `.gitignore` (it already is by default)

#### Option C: Command Line Argument

```bash
uv run main.py run --username your-username --token your_token_here
```

## Token Priority

The system checks for tokens in this order:
1. `--token` command line argument
2. `GITHUB_TOKEN` environment variable
3. `GH_TOKEN` environment variable (alternative name)
4. `.env` file in project root

## Security Best Practices

✅ **DO:**
- Use environment variables for production
- Use `.env` files for local development
- Keep tokens private and never commit them
- Regenerate tokens periodically
- Use tokens with minimal required scopes

❌ **DON'T:**
- Commit tokens to version control
- Share tokens with others
- Use tokens with excessive permissions
- Store tokens in plain text files tracked by git

## Verifying Token Setup

Run the analytics without errors to verify your token is working:

```bash
uv run main.py run --username your-username
```

If you see "No GitHub token found, using unauthenticated API (lower rate limits)" in the logs, your token isn't being detected.

## Troubleshooting

### "API rate limit exceeded"
- **Solution**: Add a GitHub token using one of the methods above
- Without a token, you're limited to 60 requests/hour

### "Bad credentials"
- **Solution**: Check that your token is correctly copied without extra spaces
- Regenerate the token if needed

### Token not detected
- **Solution**: Check environment variable spelling: `GITHUB_TOKEN` or `GH_TOKEN`
- Ensure `.env` file is in the project root directory
- Restart your terminal/IDE after setting environment variables

## Rate Limits

| Authentication | Requests per hour |
|----------------|-------------------|
| No token | 60 |
| With token | 5,000 |

For large repositories (50+ repos), a token is highly recommended to avoid rate limiting.
