"""
Pull Request Metrics Chart.
Visualizes PR velocity, review engagement, and collaboration metrics.
"""
import matplotlib.pyplot as plt
import numpy as np
from analytics.charts.base import Chart
from analytics.models.metrics import MetricResult
from analytics.models.repo import RepoStats
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger(__name__)


class PRMetricsChart(Chart):
    """Generates charts for pull request metrics."""

    def __init__(self, output_path: str = "charts/pr_metrics.png"):
        """
        Initialize PR metrics chart.

        Args:
            output_path: Path to save the generated chart
        """
        self.output_path = output_path

    def render(self, output: Path) -> None:
        """Render method for compatibility with Chart base class."""
        # Not used since we call generate() directly
        pass

    def generate(
        self,
        pr_review_result: MetricResult,
        code_review_result: MetricResult,
        repos: List[RepoStats],
        top_n: int = 10
    ) -> None:
        """
        Generate PR metrics visualization.

        Creates a multi-panel chart showing:
        - Top repositories by PRs merged
        - Review engagement distribution
        - PR quality (merge rate) distribution
        - Collaboration score

        Args:
            pr_review_result: PRReviewMetric results
            code_review_result: CodeReviewMetric results
            repos: List of repositories
            top_n: Number of top repositories to display
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Pull Request & Code Review Metrics', fontsize=16, fontweight='bold')

        # Extract metric values
        pr_velocity = pr_review_result.values.get('pr_velocity', [])
        pr_quality = pr_review_result.values.get('pr_quality', [])
        review_engagement = pr_review_result.values.get('review_engagement', [])
        collaboration = pr_review_result.values.get('collaboration', [])

        # Filter repos with PR data
        repos_with_prs = [
            (repo, vel, qual, eng, collab)
            for repo, vel, qual, eng, collab in zip(repos, pr_velocity, pr_quality, review_engagement, collaboration)
            if vel > 0  # Only repos with merged PRs
        ]

        if not repos_with_prs:
            # No PR data to display
            for ax in [ax1, ax2, ax3, ax4]:
                ax.text(0.5, 0.5, 'No Pull Request Data Available',
                       ha='center', va='center', fontsize=14, color='gray')
                ax.set_xticks([])
                ax.set_yticks([])
            plt.tight_layout()
            plt.savefig(self.output_path, dpi=300, bbox_inches='tight')
            plt.close()
            return

        # Sort by PR velocity and take top N
        repos_with_prs.sort(key=lambda x: x[1], reverse=True)
        top_repos = repos_with_prs[:top_n]

        # 1. Top Repositories by PRs Merged (Bar Chart)
        repo_names = [r[0].name[:20] for r in top_repos]
        merged_counts = [r[1] for r in top_repos]

        bars = ax1.barh(repo_names, merged_counts, color='#2E86AB')
        ax1.set_xlabel('Merged Pull Requests', fontweight='bold')
        ax1.set_title('Top Repositories by PR Velocity', fontweight='bold')
        ax1.invert_yaxis()

        # Add value labels on bars
        for i, (bar, count) in enumerate(zip(bars, merged_counts)):
            ax1.text(count, i, f' {int(count)}', va='center', fontsize=9)

        # 2. Review Engagement Distribution (Histogram)
        all_engagement = [r[3] for r in repos_with_prs]
        ax2.hist(all_engagement, bins=15, color='#A23B72', edgecolor='black', alpha=0.7)
        ax2.set_xlabel('Average Reviews per PR', fontweight='bold')
        ax2.set_ylabel('Number of Repositories', fontweight='bold')
        ax2.set_title('Review Engagement Distribution', fontweight='bold')
        ax2.axvline(np.mean(all_engagement), color='red', linestyle='--',
                   label=f'Mean: {np.mean(all_engagement):.2f}')
        ax2.legend()

        # 3. PR Quality (Merge Rate) Distribution (Box Plot)
        all_quality = [r[2] for r in repos_with_prs]
        ax3.violinplot([all_quality], vert=False, showmeans=True, showmedians=True)
        ax3.set_xlabel('PR Merge Rate (0-1)', fontweight='bold')
        ax3.set_title('PR Quality Distribution', fontweight='bold')
        ax3.set_yticks([])
        ax3.axvline(0.5, color='gray', linestyle=':', alpha=0.5)
        ax3.axvline(0.8, color='green', linestyle=':', alpha=0.5, label='Excellent (0.8)')
        ax3.legend()

        # 4. Collaboration Score (Scatter Plot)
        velocities = [r[1] for r in repos_with_prs]
        collaborations = [r[4] for r in repos_with_prs]

        scatter = ax4.scatter(velocities, collaborations,
                            s=100, alpha=0.6, c=range(len(velocities)),
                            cmap='viridis', edgecolors='black')
        ax4.set_xlabel('Merged PRs', fontweight='bold')
        ax4.set_ylabel('Unique Reviewers', fontweight='bold')
        ax4.set_title('Collaboration vs PR Velocity', fontweight='bold')

        # Add trend line
        if len(velocities) > 1:
            z = np.polyfit(velocities, collaborations, 1)
            p = np.poly1d(z)
            x_trend = np.linspace(min(velocities), max(velocities), 100)
            ax4.plot(x_trend, p(x_trend), "r--", alpha=0.5, label='Trend')
            ax4.legend()

        plt.tight_layout()
        plt.savefig(self.output_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"PR metrics chart saved to {self.output_path}")


class ReviewEngagementChart(Chart):
    """Generates detailed code review engagement charts."""

    def __init__(self, output_path: str = "charts/review_engagement.png"):
        """
        Initialize review engagement chart.

        Args:
            output_path: Path to save the generated chart
        """
        self.output_path = output_path

    def render(self, output: Path) -> None:
        """Render method for compatibility with Chart base class."""
        # Not used since we call generate() directly
        pass

    def generate(
        self,
        code_review_result: MetricResult,
        repos: List[RepoStats],
        top_n: int = 15
    ) -> None:
        """
        Generate code review engagement visualization.

        Args:
            code_review_result: CodeReviewMetric results
            repos: List of repositories
            top_n: Number of repositories to display
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle('Code Review Quality Metrics', fontsize=16, fontweight='bold')

        # Extract metric values
        thoroughness = code_review_result.values.get('review_thoroughness', [])
        coverage = code_review_result.values.get('review_coverage', [])
        diversity = code_review_result.values.get('reviewer_diversity', [])

        # Filter repos with review data
        repos_with_reviews = [
            (repo, thor, cov, div)
            for repo, thor, cov, div in zip(repos, thoroughness, coverage, diversity)
            if repo.pr_metrics and repo.pr_metrics.pr_count > 0
        ]

        if not repos_with_reviews:
            for ax in [ax1, ax2]:
                ax.text(0.5, 0.5, 'No Code Review Data Available',
                       ha='center', va='center', fontsize=14, color='gray')
                ax.set_xticks([])
                ax.set_yticks([])
            plt.tight_layout()
            plt.savefig(self.output_path, dpi=300, bbox_inches='tight')
            plt.close()
            return

        # Sort by review coverage
        repos_with_reviews.sort(key=lambda x: x[2], reverse=True)
        top_repos = repos_with_reviews[:top_n]

        # 1. Review Coverage by Repository
        repo_names = [r[0].name[:25] for r in top_repos]
        coverages = [r[2] * 100 for r in top_repos]  # Convert to percentage

        bars = ax1.barh(repo_names, coverages, color='#F18F01')
        ax1.set_xlabel('Review Coverage (%)', fontweight='bold')
        ax1.set_title('Review Coverage by Repository', fontweight='bold')
        ax1.invert_yaxis()
        ax1.set_xlim(0, 100)

        # Add threshold lines
        ax1.axvline(90, color='green', linestyle='--', alpha=0.5, label='Excellent (90%)')
        ax1.axvline(70, color='orange', linestyle='--', alpha=0.5, label='Good (70%)')
        ax1.legend()

        # 2. Review Thoroughness vs Diversity
        all_thoroughness = [r[1] for r in repos_with_reviews]
        all_diversity = [r[3] for r in repos_with_reviews]

        scatter = ax2.scatter(all_thoroughness, all_diversity,
                            s=100, alpha=0.6, c=coverages[:len(all_thoroughness)],
                            cmap='RdYlGn', vmin=0, vmax=100, edgecolors='black')
        ax2.set_xlabel('Comments per PR', fontweight='bold')
        ax2.set_ylabel('Reviewers per PR', fontweight='bold')
        ax2.set_title('Review Thoroughness vs Reviewer Diversity', fontweight='bold')

        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax2)
        cbar.set_label('Review Coverage (%)', fontweight='bold')

        plt.tight_layout()
        plt.savefig(self.output_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Review engagement chart saved to {self.output_path}")
