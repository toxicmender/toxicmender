def test_analyzer_runs(sample_repo):
    from analytics.pipeline.analyse import Analyser
    from analytics.metrics.loc import LOCMetric

    analyser = Analyser([LOCMetric()])
    result = analyser.run([sample_repo])
    assert "loc" in result
    assert result["loc"] > 0
    assert isinstance(result["loc"], int)
