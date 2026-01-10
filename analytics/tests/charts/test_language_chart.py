from analytics.charts.language import LanguageChart

def test_language_chart(tmp_path):
    chart = LanguageChart({"Python": 70, "JS": 30})
    out = tmp_path / "chart.svg"
    chart.render(out)
    assert out.exists()
