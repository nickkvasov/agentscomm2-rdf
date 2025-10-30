"""Entry point for executing evaluation scenarios against the pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

from src.gateway.models import EvaluationScenarioResult, GatewayFeatureFlags

from .pipeline import InMemoryValidationPipeline
from .scenarios import EvaluationScenario, DEFAULT_SCENARIOS


def _default_feature_flags() -> List[GatewayFeatureFlags]:
    return [
        GatewayFeatureFlags(),
        GatewayFeatureFlags(enable_reasoning=False),
        GatewayFeatureFlags(enable_shacl=False),
        GatewayFeatureFlags(enable_agent_consistency=False),
    ]


@dataclass
class EvaluationSummary:
    total: int
    passed: int

    @property
    def failed(self) -> int:
        return self.total - self.passed

    @property
    def pass_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.passed / self.total


class GatewayEvaluationSuite:
    """Runs synthetic evaluation scenarios across feature configurations."""

    def __init__(
        self,
        scenarios: Sequence[EvaluationScenario] | None = None,
        feature_flag_sets: Sequence[GatewayFeatureFlags] | None = None,
        pipeline: InMemoryValidationPipeline | None = None,
    ) -> None:
        self.scenarios = list(scenarios or DEFAULT_SCENARIOS)
        self.feature_flag_sets = list(feature_flag_sets or _default_feature_flags())
        self.pipeline = pipeline or InMemoryValidationPipeline.from_repository()

    def run(self) -> List[EvaluationScenarioResult]:
        results: List[EvaluationScenarioResult] = []
        for flags in self.feature_flag_sets:
            for scenario in self.scenarios:
                payload_graph = scenario.build_payload()
                response = self.pipeline.evaluate(payload_graph, flags)
                actual_error_types = {error.error_type for error in response.errors}
                expected_types = set(scenario.expected_error_types)
                success_matches = response.success == scenario.expect_success
                if scenario.expect_success:
                    error_matches = True
                elif not expected_types:
                    error_matches = not response.success
                else:
                    error_matches = bool(actual_error_types.intersection(expected_types))
                result = EvaluationScenarioResult(
                    scenario_name=scenario.name,
                    feature_flags=GatewayFeatureFlags(**flags.model_dump()),
                    response=response,
                    passed=success_matches and error_matches,
                    expected_success=scenario.expect_success,
                    expected_error_types=list(expected_types),
                )
                results.append(result)
        return results

    @staticmethod
    def summarize(results: Iterable[EvaluationScenarioResult]) -> EvaluationSummary:
        result_list = list(results)
        passed = sum(1 for result in result_list if result.passed)
        return EvaluationSummary(total=len(result_list), passed=passed)

    @staticmethod
    def render_markdown_table(results: Iterable[EvaluationScenarioResult]) -> str:
        lines = [
            "| Scenario | Feature Flags | Actual | Expected | Passed |",
            "|---|---|---|---|---|",
        ]
        for result in results:
            flags_label = _format_flags(result.feature_flags)
            actual = "✅" if result.response.success else "❌"
            expected = "✅" if result.expected_success else "❌"
            passed = "✅" if result.passed else "❌"
            lines.append(
                f"| {result.scenario_name} | {flags_label} | {actual} | {expected} | {passed} |"
            )
        return "\n".join(lines)


def _format_flags(flags: GatewayFeatureFlags) -> str:
    return ", ".join(
        [
            f"consistency={'on' if flags.enable_agent_consistency else 'off'}",
            f"shacl={'on' if flags.enable_shacl else 'off'}",
            f"reasoning={'on' if flags.enable_reasoning else 'off'}",
            f"consensus={'on' if flags.enable_consensus_checks else 'off'}",
        ]
    )
