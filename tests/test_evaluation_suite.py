from rdflib import Literal
from rdflib.namespace import RDF

from src.evaluation import GatewayEvaluationSuite, DEFAULT_SCENARIOS
from src.evaluation.pipeline import InMemoryValidationPipeline
from src.evaluation.scenarios import TOURISM
from src.gateway.models import GatewayFeatureFlags, ValidationErrorType


def _scenario_by_name(name: str):
    return next(s for s in DEFAULT_SCENARIOS if s.name == name)


def test_valid_attraction_passes_with_all_features():
    suite = GatewayEvaluationSuite(
        scenarios=[_scenario_by_name("valid_attraction")],
        feature_flag_sets=[GatewayFeatureFlags()],
    )
    results = suite.run()
    assert len(results) == 1
    result = results[0]
    assert result.passed
    assert result.response.success


def test_invalid_rating_detected_by_shacl():
    suite = GatewayEvaluationSuite(
        scenarios=[_scenario_by_name("invalid_rating")],
        feature_flag_sets=[GatewayFeatureFlags()],
    )
    results = suite.run()
    assert not results[0].response.success
    assert results[0].passed


def test_invalid_rating_slips_without_shacl():
    suite = GatewayEvaluationSuite(
        scenarios=[_scenario_by_name("invalid_rating")],
        feature_flag_sets=[GatewayFeatureFlags(enable_shacl=False)],
    )
    results = suite.run()
    assert results[0].response.success
    assert not results[0].passed


def test_markdown_rendering_includes_all_results():
    suite = GatewayEvaluationSuite(
        scenarios=[_scenario_by_name("valid_attraction")],
        feature_flag_sets=[GatewayFeatureFlags(), GatewayFeatureFlags(enable_reasoning=False)],
    )
    results = suite.run()
    table = suite.render_markdown_table(results)
    assert table.count("| valid_attraction |") == 2


def test_consensus_conflict_detected_when_enabled():
    pipeline = InMemoryValidationPipeline.from_repository()
    attraction = TOURISM.DubaiAquarium
    pipeline.base_graph.add((attraction, RDF.type, TOURISM.Attraction))
    pipeline.base_graph.add((attraction, TOURISM.hasAmenity, Literal("Accessible")))

    suite = GatewayEvaluationSuite(
        scenarios=[_scenario_by_name("valid_attraction")],
        feature_flag_sets=[GatewayFeatureFlags(enable_agent_consistency=False)],
        pipeline=pipeline,
    )

    results = suite.run()
    response = results[0].response
    assert not response.success
    assert any(error.error_type == ValidationErrorType.LOGIC_CONTRADICTION for error in response.errors)


def test_consensus_conflict_skipped_when_checks_disabled():
    pipeline = InMemoryValidationPipeline.from_repository()
    attraction = TOURISM.DubaiAquarium
    pipeline.base_graph.add((attraction, RDF.type, TOURISM.Attraction))
    pipeline.base_graph.add((attraction, TOURISM.hasAmenity, Literal("Accessible")))

    suite = GatewayEvaluationSuite(
        scenarios=[_scenario_by_name("valid_attraction")],
        feature_flag_sets=[GatewayFeatureFlags(
            enable_agent_consistency=False, enable_consensus_checks=False
        )],
        pipeline=pipeline,
    )

    results = suite.run()
    response = results[0].response
    assert response.success
