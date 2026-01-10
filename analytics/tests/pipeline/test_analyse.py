def test_analyzer_runs(sample_repo):
    from analytics.pipeline.analyse import Analyser
    from analytics.metrics.loc import LOCMetric

    analyser = Analyser([LOCMetric()])
    result = analyser.run([sample_repo])
    assert "loc" in result
    # LOCMetric.compute returns a dict directly, not a MetricResult
    assert isinstance(result["loc"], dict)
    assert "test-repo" in result["loc"]
    assert result["loc"]["test-repo"] == 1500
