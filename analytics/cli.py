import typer
from pathlib import Path
from analytics.pipeline import analyse, collect, visualize, render
import typer
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
    username: str = typer.Option(..., help="GitHub username"),
    output: Path = typer.Option(Path("data"), help="Output directory")
):
    """
    Fetch repositories, metadata, and activity data.
    """
    typer.echo("🔍 Collecting data...")
    collect.run(username=username, output_dir=output)
    typer.echo("✅ Data collection complete")


@app.command()
def analyze_data(
    input_dir: Path = typer.Option(Path("data"), help="Input data directory"),
    output_dir: Path = typer.Option(Path("data"), help="Output directory")
):
    """
    Compute metrics and normalized scores.
    """
    typer.echo("🧮 Analyzing data...")
    analyse.run(input_dir=input_dir, output_dir=output_dir)
    typer.echo("✅ Analysis complete")


@app.command()
def visualize_data(
    data_dir: Path = typer.Option(Path("data"), help="Metrics directory"),
    charts_dir: Path = typer.Option(Path("charts"), help="Charts output")
):
    """
    Generate charts using matplotlib.
    """
    typer.echo("📊 Generating charts...")
    visualize.run(data_dir=data_dir, charts_dir=charts_dir)
    typer.echo("✅ Charts generated")


@app.command()
def render_readme(
    template: Path = typer.Option(Path("README.template.md")),
    output: Path = typer.Option(Path("README.md")),
    data_dir: Path = typer.Option(Path("data"))
):
    """
    Render README from template and metrics.
    """
    typer.echo("📝 Rendering README...")
    render.run(template, output, data_dir)
    typer.echo("✅ README updated")


@app.command()
def run(
    username: str = typer.Option(..., help="GitHub username"),
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
