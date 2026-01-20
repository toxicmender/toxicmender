from typing import Annotated
import typer
from pathlib import Path
from analytics.pipeline import analyse, collect, visualize, render
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
    output: Annotated[Path, typer.Option(help="Output directory")] = Path("data/")
):
    """
    Fetch repositories, metadata, and activity data.
    """
    typer.echo("🔍 Collecting data...")
    collect.run(username=username, output_dir=output.joinpath(username))
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

if __name__ == "__main__":
    app()
