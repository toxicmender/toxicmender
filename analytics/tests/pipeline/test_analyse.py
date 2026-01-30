def test_analyzer_runs(sample_repo):
    from analytics.pipeline.analyse import Analyser
    from analytics.metrics.loc import LOCMetric
    from analytics.models.metrics import MetricResult

    analyser = Analyser([LOCMetric()])
    result = analyser.run(repos=[sample_repo])
    assert "loc" in result
    assert isinstance(result["loc"], MetricResult)
    assert "test-repo" in result["loc"].repo_names
    assert result["loc"].get_value_by_repo("test-repo", "total_loc") == 1500
