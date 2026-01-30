from typing import Annotated
import typer
from pathlib import Path
from analytics.pipeline import analyse, collect, visualize, render
from analytics.migration import MigrationManager
from analytics.exceptions import AnalyticsError

app = typer.Typer(
    name="analytics",
    help="GitHub profile analytics pipeline"
)

# @app.callback()
# def main():
#     pass

@app.command()
def collect_data(
    username: Annotated[str, typer.Option(help="GitHub username")],
    output: Annotated[Path, typer.Option(help="Output directory")] = Path("data/"),
    token: Annotated[str, typer.Option(help="GitHub personal access token (optional, for higher rate limits)")] = None
):
    """
    Fetch repositories, metadata, and activity data.
    Caches each repo individually to handle rate limits and resume progress.
    """
    typer.echo("🔍 Collecting data...")
    collect.run(username=username, output_dir=output.joinpath(username), github_token=token)
    typer.echo("✅ Data collection complete")


@app.command()
def analyze_data(
    input_dir: Annotated[Path, typer.Option(help="Input data directory")] = Path("data/"),
    output_dir: Annotated[Path, typer.Option(help="Output directory")] = Path("data/")
):
    """
    Compute metrics and normalized scores.
    """
    typer.echo("🧮 Analyzing data...")
    analyse.run(input_dir=input_dir, output_dir=output_dir)
    typer.echo("✅ Analysis complete")


@app.command()
def visualize_data(
    data_dir: Annotated[Path, typer.Option(help="Metrics directory")] = Path("data/"),
    charts_dir: Annotated[Path, typer.Option(help="Charts output")] = Path("charts/")
):
    """
    Generate charts using matplotlib.
    """
    typer.echo("📊 Generating charts...")
    visualize.run(data_dir=data_dir, charts_dir=charts_dir)
    typer.echo("✅ Charts generated")


@app.command()
def render_readme(
    template: Annotated[Path, typer.Option(help="Template file path")] = Path("README.template.md"),
    output: Annotated[Path, typer.Option(help="Output file path")] = Path("README.md"),
    data_dir: Annotated[Path, typer.Option(help="Data directory")] = Path("data/")
):
    """
    Render README from template and metrics.
    """
    typer.echo("📝 Rendering README...")
    render.run(template, output, data_dir)
    typer.echo("✅ README updated")


@app.command()
def run(
    username: Annotated[str, typer.Option(help="GitHub username")]
):
    """
    Run full analytics pipeline.
    """
    try:
        typer.echo("🚀 Starting full analytics pipeline...")
        collect_data(username=username)
        analyze_data()
        visualize_data()
        render_readme()
        typer.echo("🎉 Analytics pipeline complete!")
    except AnalyticsError as e:
        typer.secho(f"❌ {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command()
def migrate_data(
    username: Annotated[str, typer.Option(help="GitHub username")],
    data_dir: Annotated[Path, typer.Option(help="Data directory")] = Path("data/"),
    force: Annotated[bool, typer.Option(help="Overwrite existing history if present")] = False
):
    """
    Migrate v1.x metrics.json to v2.0 history format.
    """
    user_dir = data_dir / username
    manager = MigrationManager(user_dir)
    try:
        typer.echo(f"🔄 Migrating data for {username}...")
        history = manager.migrate_user_data(username=username, force=force)
        typer.echo(f"✅ Migration complete: {len(history.runs)} run(s) migrated")
    except Exception as e:
        typer.secho(f"❌ Migration failed: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command()
def check_migration(
    username: Annotated[str, typer.Option(help="GitHub username")],
    data_dir: Annotated[Path, typer.Option(help="Data directory")] = Path("data/")
):
    """
    Validate migration status for a user.
    """
    user_dir = data_dir / username
    manager = MigrationManager(user_dir)
    report = manager.validate_migration()
    if report["success"]:
        typer.echo(f"✅ Migration OK: {report['runs_found']} run(s) found")
    else:
        typer.secho("⚠️ Migration issues detected:", fg=typer.colors.YELLOW)
        for err in report["errors"]:
            typer.echo(f" - {err}")

if __name__ == "__main__":
    app()
