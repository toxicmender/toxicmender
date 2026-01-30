"""
Language filtering utility for excluding specified languages from analysis.
Provides functions to filter repository language data based on configuration.
"""
from analytics.models.repo import RepoStats
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml
import logging

logger = logging.getLogger(__name__)


def load_language_filters(config_path: Path) -> Dict[str, Any]:
    """
    Load language filter configuration from YAML file.

    Args:
        config_path: Path to language_filters.yml configuration file

    Returns:
        Dictionary containing filter configuration with keys:
        - excluded_languages: List of language names to exclude
        - filter_enabled: Boolean to enable/disable filtering
        - minimum_language_loc: Minimum LOC threshold per language
        - remove_empty_repos: Whether to remove repos with 0 LOC after filtering
        - case_sensitive: Whether language matching is case-sensitive

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Language filter config not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Provide defaults for missing keys
    defaults = {
        'excluded_languages': [],
        'filter_enabled': True,
        'minimum_language_loc': 0,
        'remove_empty_repos': True,
        'case_sensitive': False
    }

    return {**defaults, **config}


def should_exclude_language(language: str, excluded: List[str], case_sensitive: bool = False) -> bool:
    """
    Check if a language should be excluded based on exclusion list.

    Args:
        language: Language name to check
        excluded: List of excluded language names
        case_sensitive: Whether to use case-sensitive matching

    Returns:
        True if language should be excluded, False otherwise
    """
    if not excluded:
        return False

    if case_sensitive:
        return language in excluded

    # Case-insensitive matching
    language_lower = language.lower()
    excluded_lower = [lang.lower() for lang in excluded]
    return language_lower in excluded_lower


def filter_repo_languages(
    repo: RepoStats,
    excluded: List[str],
    minimum_loc: int = 0,
    case_sensitive: bool = False,
    track_filtered: bool = True
) -> RepoStats:
    """
    Filter languages from a repository based on exclusion list and minimum LOC.

    Creates a new RepoStats instance with filtered languages dictionary
    and recalculated total LOC.

    Args:
        repo: Original repository statistics
        excluded: List of language names to exclude
        minimum_loc: Minimum LOC threshold per language (0 to disable)
        case_sensitive: Whether language matching is case-sensitive
        track_filtered: Whether to track original LOC and filtered languages

    Returns:
        New RepoStats instance with filtered languages and updated LOC
    """
    # Filter languages
    filtered_languages = {}
    removed_languages = []

    for lang, loc in repo.languages.items():
        # Check if language should be excluded
        if should_exclude_language(lang, excluded, case_sensitive):
            removed_languages.append(lang)
            continue

        # Check minimum LOC threshold
        if minimum_loc > 0 and loc < minimum_loc:
            removed_languages.append(lang)
            continue

        # Keep this language
        filtered_languages[lang] = loc

    # Calculate new total LOC
    new_loc = sum(filtered_languages.values())

    # Ensure LOC is at least 1 (PositiveInt requirement)
    # If all languages filtered out, we'll handle this in filter_repos_list
    if new_loc == 0:
        new_loc = 1  # Temporary value, will be filtered out if remove_empty_repos=True

    # Create new RepoStats with filtered data
    repo_dict = repo.model_dump()
    repo_dict['languages'] = filtered_languages
    repo_dict['loc'] = new_loc

    # Add tracking fields if requested
    if track_filtered and removed_languages:
        repo_dict['original_loc'] = repo.loc
        repo_dict['filtered_languages'] = removed_languages

    return RepoStats(**repo_dict)


def filter_repos_list(
    repos: List[RepoStats],
    config: Dict[str, Any]
) -> List[RepoStats]:
    """
    Apply language filtering to a list of repositories.

    Args:
        repos: List of repository statistics to filter
        config: Filter configuration dictionary (from load_language_filters)

    Returns:
        List of filtered RepoStats objects
    """
    if not config.get('filter_enabled', True):
        logger.info("Language filtering disabled in config")
        return repos

    excluded_languages = config.get('excluded_languages', [])
    minimum_loc = config.get('minimum_language_loc', 0)
    remove_empty = config.get('remove_empty_repos', True)
    case_sensitive = config.get('case_sensitive', False)

    if not excluded_languages and minimum_loc == 0:
        logger.info("No language filters configured")
        return repos

    logger.info(f"Applying language filters: {len(excluded_languages)} excluded languages, "
                f"minimum LOC: {minimum_loc}")

    # Track statistics
    original_count = len(repos)
    original_total_loc = sum(repo.loc for repo in repos)
    total_languages_filtered = 0

    # Filter each repository
    filtered_repos = []
    for repo in repos:
        filtered_repo = filter_repo_languages(
            repo,
            excluded_languages,
            minimum_loc,
            case_sensitive,
            track_filtered=True
        )

        # Count filtered languages
        if hasattr(filtered_repo, 'filtered_languages') and filtered_repo.filtered_languages:
            total_languages_filtered += len(filtered_repo.filtered_languages)

        # Check if repo should be removed (has no code after filtering)
        if remove_empty and filtered_repo.loc <= 1 and not filtered_repo.languages:
            logger.debug(f"Removing empty repo after filtering: {repo.name}")
            continue

        filtered_repos.append(filtered_repo)

    # Log statistics
    filtered_count = len(filtered_repos)
    filtered_total_loc = sum(repo.loc for repo in filtered_repos)
    removed_repos = original_count - filtered_count
    removed_loc = original_total_loc - filtered_total_loc

    logger.info(f"Filtering complete:")
    logger.info(f"  - Repositories: {original_count} → {filtered_count} "
                f"({removed_repos} removed)")
    logger.info(f"  - Total LOC: {original_total_loc:,} → {filtered_total_loc:,} "
                f"({removed_loc:,} removed, {100 * removed_loc / original_total_loc:.1f}%)")
    logger.info(f"  - Language instances filtered: {total_languages_filtered}")

    return filtered_repos


def get_filter_summary(repos_before: List[RepoStats], repos_after: List[RepoStats]) -> Dict[str, Any]:
    """
    Generate a summary of filtering impact.

    Args:
        repos_before: Original repository list
        repos_after: Filtered repository list

    Returns:
        Dictionary with filtering statistics
    """
    # Collect all filtered languages
    all_filtered_languages = set()
    for repo in repos_after:
        if hasattr(repo, 'filtered_languages') and repo.filtered_languages:
            all_filtered_languages.update(repo.filtered_languages)

    return {
        'repos_before': len(repos_before),
        'repos_after': len(repos_after),
        'repos_removed': len(repos_before) - len(repos_after),
        'loc_before': sum(repo.loc for repo in repos_before),
        'loc_after': sum(repo.loc for repo in repos_after),
        'loc_removed': sum(repo.loc for repo in repos_before) - sum(repo.loc for repo in repos_after),
        'filtered_languages': sorted(list(all_filtered_languages))
    }
