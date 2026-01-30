"""
Authentication configuration for external services.
"""
import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def get_github_token() -> Optional[str]:
    """
    Get GitHub personal access token from environment or config file.

    Priority:
    1. GITHUB_TOKEN environment variable
    2. GH_TOKEN environment variable
    3. .env file in project root

    Returns:
        GitHub token if found, None otherwise
    """
    # Try environment variables
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        logger.debug("Using GITHUB_TOKEN from environment")
        return token

    token = os.environ.get('GH_TOKEN')
    if token:
        logger.debug("Using GH_TOKEN from environment")
        return token

    # Try .env file
    env_file = Path('.env')
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('GITHUB_TOKEN='):
                        token = line.split('=', 1)[1].strip().strip('"\'')
                        if token:
                            logger.debug("Using GITHUB_TOKEN from .env file")
                            return token
                    elif line.startswith('GH_TOKEN='):
                        token = line.split('=', 1)[1].strip().strip('"\'')
                        if token:
                            logger.debug("Using GH_TOKEN from .env file")
                            return token
        except IOError as e:
            logger.warning(f"Failed to read .env file: {e}")

    logger.info("No GitHub token found, using unauthenticated API (lower rate limits)")
    return None
