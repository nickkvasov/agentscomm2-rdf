"""In-memory validation pipeline used for automated evaluations."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

from pyshacl import validate
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF, SH, XSD

from src.gateway.models import (
    GatewayFeatureFlags,
    ValidationError,
    ValidationErrorType,
    ValidationResponse,
)

TOURISM = Namespace("http://example.org/tourism#")


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_graph_from_file(path: Path) -> Graph:
    graph = Graph()
    graph.parse(path, format="turtle")
    return graph


@dataclass(slots=True)
class InMemoryValidationPipeline:
    """Simplified validation harness that mirrors the gateway stages."""

    base_graph: Graph
    shapes_graph: Graph

    @classmethod
    def from_repository(cls) -> "InMemoryValidationPipeline":
        root = _project_root()
        shapes_graph = _load_graph_from_file(root / "ontology" / "tourism_shacl_shapes.ttl")
        base_graph = Graph()
        base_graph.bind("tourism", TOURISM)
        return cls(base_graph=base_graph, shapes_graph=shapes_graph)

    def evaluate(self, payload: Graph, feature_flags: GatewayFeatureFlags) -> ValidationResponse:
        start = time.perf_counter()
        merged_graph = Graph()
        merged_graph += self.base_graph
        merged_graph += payload

        if feature_flags.enable_agent_consistency:
            agent_errors = self._run_agent_consistency_checks(merged_graph)
            if agent_errors:
                return ValidationResponse(
                    success=False,
                    message="Agent consistency validation failed",
                    errors=agent_errors,
                    processing_time_ms=(time.perf_counter() - start) * 1000,
                )

        if feature_flags.enable_shacl:
            shacl_errors = self._run_shacl_validation(merged_graph)
            if shacl_errors:
                return ValidationResponse(
                    success=False,
                    message="SHACL validation failed",
                    errors=shacl_errors,
                    processing_time_ms=(time.perf_counter() - start) * 1000,
                )

        derived_facts: List[Tuple] = []
        contradictions: List[dict] = []
        reasoning_iterations = 0

        if feature_flags.enable_reasoning:
            derived_facts, contradictions, reasoning_iterations = self._run_reasoning(merged_graph)
            if contradictions:
                errors = [
                    ValidationError(
                        error_type=ValidationErrorType.LOGIC_CONTRADICTION,
                        message=contradiction["message"],
                        focus_node=contradiction.get("entity"),
                        details=contradiction,
                    )
                    for contradiction in contradictions
                ]
                return ValidationResponse(
                    success=False,
                    message="Logic contradictions detected",
                    errors=errors,
                    contradictions=contradictions,
                    derived_facts=self._format_derived_facts(derived_facts),
                    reasoning_iterations=reasoning_iterations,
                    processing_time_ms=(time.perf_counter() - start) * 1000,
                )

        if feature_flags.enable_consensus_checks:
            consensus_errors = self._run_consensus_validation(payload)
            if consensus_errors:
                return ValidationResponse(
                    success=False,
                    message="Consensus/main consistency validation failed",
                    errors=consensus_errors,
                    derived_facts=self._format_derived_facts(derived_facts),
                    reasoning_iterations=reasoning_iterations,
                    processing_time_ms=(time.perf_counter() - start) * 1000,
                )

        processing_ms = (time.perf_counter() - start) * 1000
        return ValidationResponse(
            success=True,
            message="Validation successful",
            derived_facts=self._format_derived_facts(derived_facts),
            reasoning_iterations=reasoning_iterations,
            processing_time_ms=processing_ms,
        )

    def _run_agent_consistency_checks(self, graph: Graph) -> List[ValidationError]:
        errors: List[ValidationError] = []
        for subject in set(graph.subjects(RDF.type, TOURISM.Attraction)):
            name_values = {str(o) for o in graph.objects(subject, TOURISM.hasName)}
            if len(name_values) > 1:
                errors.append(
                    ValidationError(
                        error_type=ValidationErrorType.LOGIC_CONTRADICTION,
                        message="Attraction has conflicting names",
                        focus_node=str(subject),
                        details={"values": sorted(name_values)},
                    )
                )
            rating_values = {str(o) for o in graph.objects(subject, TOURISM.hasRating)}
            if len(rating_values) > 1:
                errors.append(
                    ValidationError(
                        error_type=ValidationErrorType.LOGIC_CONTRADICTION,
                        message="Attraction has conflicting ratings",
                        focus_node=str(subject),
                        details={"values": sorted(rating_values)},
                    )
                )
        return errors

    def _run_shacl_validation(self, graph: Graph) -> List[ValidationError]:
        conforms, results_graph, _ = validate(
            data_graph=graph,
            shacl_graph=self.shapes_graph,
            inference="rdfs",
            abort_on_first=False,
            meta_shacl=False,
            advanced=True,
        )
        if conforms:
            return []

        errors: List[ValidationError] = []
        for result in results_graph.subjects(RDF.type, SH.ValidationResult):
            message = results_graph.value(result, SH.resultMessage)
            focus = results_graph.value(result, SH.focusNode)
            path = results_graph.value(result, SH.resultPath)
            severity = results_graph.value(result, SH.resultSeverity)
            errors.append(
                ValidationError(
                    error_type=ValidationErrorType.SHACL_VIOLATION,
                    message=str(message) if message else "SHACL constraint violated",
                    focus_node=str(focus) if focus else None,
                    property_path=str(path) if path else None,
                    severity=str(severity) if severity else "error",
                    details={"result": str(result)},
                )
            )
        return errors

    def _run_reasoning(self, graph: Graph) -> Tuple[List[Tuple], List[dict], int]:
        derived: List[Tuple] = []
        contradictions: List[dict] = []
        iteration = 0
        updated = True

        while updated:
            updated = False
            iteration += 1
            newly_derived = self._apply_reasoning_rules(graph)
            if newly_derived:
                updated = True
                for triple in newly_derived:
                    if triple not in graph:
                        graph.add(triple)
                        derived.append(triple)

        contradictions.extend(self._detect_contradictions(graph))
        return derived, contradictions, iteration - 1 if iteration else 0

    def _run_consensus_validation(self, payload: Graph) -> List[ValidationError]:
        errors: List[ValidationError] = []
        seen_subject_predicate: set[Tuple[str, str]] = set()

        for subject, predicate, obj in payload:
            key = (str(subject), str(predicate))
            if key in seen_subject_predicate:
                continue
            seen_subject_predicate.add(key)

            existing_values = {existing for existing in self.base_graph.objects(subject, predicate)}
            if not existing_values:
                continue

            if obj not in existing_values:
                details = {
                    "existing": sorted(str(value) for value in existing_values),
                    "proposed": str(obj),
                }
                errors.append(
                    ValidationError(
                        error_type=ValidationErrorType.LOGIC_CONTRADICTION,
                        message="Payload conflicts with committed consensus/main value",
                        focus_node=str(subject),
                        details=details,
                    )
                )

        return errors

    def _apply_reasoning_rules(self, graph: Graph) -> List[Tuple]:
        new_facts: List[Tuple] = []

        for attraction in set(graph.subjects(RDF.type, TOURISM.Attraction)):
            for amenity in graph.objects(attraction, TOURISM.hasAmenity):
                if str(amenity) == "Playground" and (attraction, RDF.type, TOURISM.FamilyFriendlyAttraction) not in graph:
                    new_facts.append((attraction, RDF.type, TOURISM.FamilyFriendlyAttraction))

            for min_age_literal in graph.objects(attraction, TOURISM.hasMinAge):
                try:
                    min_age = int(min_age_literal)
                except (TypeError, ValueError):
                    continue
                if min_age > 12 and (attraction, RDF.type, TOURISM.NotFamilyFriendlyAttraction) not in graph:
                    new_facts.append((attraction, RDF.type, TOURISM.NotFamilyFriendlyAttraction))

            for city in graph.objects(attraction, TOURISM.locatedIn):
                if (city, RDF.type, TOURISM.CoastalCity) in graph and (
                    attraction, RDF.type, TOURISM.CoastalAttraction
                ) not in graph:
                    new_facts.append((attraction, RDF.type, TOURISM.CoastalAttraction))

            rating_literal = next(iter(graph.objects(attraction, TOURISM.hasRating)), None)
            if rating_literal is not None:
                try:
                    rating = float(rating_literal)
                except (TypeError, ValueError):
                    rating = None
            else:
                rating = None

            if rating is not None and rating >= 4.5:
                if (attraction, RDF.type, TOURISM.FamilyFriendlyAttraction) in graph:
                    local_name = str(attraction).split("#")[-1]
                    destination = TOURISM[f"CoastalFamilyDestination_{local_name}"]
                    if (destination, RDF.type, TOURISM.CoastalFamilyDestination) not in graph:
                        new_facts.extend(
                            [
                                (destination, RDF.type, TOURISM.CoastalFamilyDestination),
                                (destination, TOURISM.hasPrimaryAttraction, attraction),
                                (destination, TOURISM.hasRating, Literal(rating)),
                            ]
                        )
                        for city in graph.objects(attraction, TOURISM.locatedIn):
                            new_facts.append((destination, TOURISM.hasCity, city))
        return new_facts

    def _detect_contradictions(self, graph: Graph) -> List[dict]:
        contradictions: List[dict] = []
        for attraction in set(graph.subjects(RDF.type, TOURISM.Attraction)):
            is_family = (attraction, RDF.type, TOURISM.FamilyFriendlyAttraction) in graph
            is_not_family = (attraction, RDF.type, TOURISM.NotFamilyFriendlyAttraction) in graph
            if is_family and is_not_family:
                contradictions.append(
                    {
                        "entity": str(attraction),
                        "message": "Attraction is both family-friendly and not family-friendly",
                        "conflicting_types": [
                            str(TOURISM.FamilyFriendlyAttraction),
                            str(TOURISM.NotFamilyFriendlyAttraction),
                        ],
                    }
                )
        return contradictions

    def _format_derived_facts(self, triples: Iterable[Tuple]) -> List[dict]:
        formatted: List[dict] = []
        for subject, predicate, obj in triples:
            formatted.append(
                {
                    "subject": str(subject),
                    "predicate": str(predicate),
                    "object": str(obj),
                }
            )
        return formatted
