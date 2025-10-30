"""Synthetic evaluation scenarios for the validator gateway."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, List, Sequence, Set

from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF, XSD

from src.gateway.models import ValidationErrorType

TOURISM = Namespace("http://example.org/tourism#")


PayloadBuilder = Callable[[], Graph]


@dataclass(slots=True)
class EvaluationScenario:
    """Container describing a single automated evaluation scenario."""

    name: str
    description: str
    build_payload: PayloadBuilder
    expect_success: bool
    expected_error_types: Sequence[ValidationErrorType] = field(default_factory=tuple)

    def payload_as_turtle(self) -> str:
        """Return the payload graph serialized as Turtle."""
        graph = self.build_payload()
        return graph.serialize(format="turtle")


def _base_graph() -> Graph:
    graph = Graph()
    graph.bind("tourism", TOURISM)
    graph.add((TOURISM.Dubai, RDF.type, TOURISM.City))
    graph.add((TOURISM.Dubai, RDF.type, TOURISM.CoastalCity))
    graph.add((TOURISM.Dubai, TOURISM.hasName, Literal("Dubai")))
    graph.add((TOURISM.Dubai, TOURISM.inCountry, TOURISM.UAE))
    graph.add((TOURISM.UAE, RDF.type, TOURISM.Country))
    graph.add((TOURISM.UAE, TOURISM.hasName, Literal("United Arab Emirates")))
    return graph


def _valid_attraction_payload() -> Graph:
    graph = _base_graph()
    attraction = TOURISM.DubaiAquarium
    graph.add((attraction, RDF.type, TOURISM.Attraction))
    graph.add((attraction, TOURISM.hasName, Literal("Dubai Aquarium")))
    graph.add((attraction, TOURISM.locatedIn, TOURISM.Dubai))
    graph.add((attraction, TOURISM.hasAmenity, Literal("Playground")))
    graph.add((attraction, TOURISM.hasRating, Literal("4.7", datatype=XSD.decimal)))
    graph.add((attraction, TOURISM.hasEntryFeeAmount, Literal("25.0", datatype=XSD.decimal)))
    graph.add((attraction, TOURISM.hasEntryFeeCurrency, Literal("AED")))
    return graph


def _invalid_rating_payload() -> Graph:
    graph = _valid_attraction_payload()
    graph.set((TOURISM.DubaiAquarium, TOURISM.hasRating, Literal("8.5", datatype=XSD.decimal)))
    return graph


def _contradictory_payload() -> Graph:
    graph = _valid_attraction_payload()
    attraction = TOURISM.DubaiAquarium
    graph.add((attraction, RDF.type, TOURISM.FamilyFriendlyAttraction))
    graph.add((attraction, RDF.type, TOURISM.NotFamilyFriendlyAttraction))
    graph.add((attraction, TOURISM.hasMinAge, Literal(18, datatype=XSD.integer)))
    return graph


def _missing_location_payload() -> Graph:
    graph = Graph()
    graph.bind("tourism", TOURISM)
    attraction = TOURISM.MysteryPark
    graph.add((attraction, RDF.type, TOURISM.Attraction))
    graph.add((attraction, TOURISM.hasName, Literal("Mystery Park")))
    graph.add((attraction, TOURISM.hasRating, Literal("4.2", datatype=XSD.decimal)))
    graph.add((attraction, TOURISM.hasEntryFeeCurrency, Literal("USD")))
    return graph


DEFAULT_SCENARIOS: List[EvaluationScenario] = [
    EvaluationScenario(
        name="valid_attraction",
        description="All constraints satisfied; should validate successfully.",
        build_payload=_valid_attraction_payload,
        expect_success=True,
        expected_error_types=(),
    ),
    EvaluationScenario(
        name="invalid_rating",
        description="Rating exceeds max inclusive bound and should trigger SHACL violation.",
        build_payload=_invalid_rating_payload,
        expect_success=False,
        expected_error_types=(ValidationErrorType.SHACL_VIOLATION,),
    ),
    EvaluationScenario(
        name="contradictory_classification",
        description="Entity is marked as both family-friendly and not family-friendly; should trigger contradiction.",
        build_payload=_contradictory_payload,
        expect_success=False,
        expected_error_types=(
            ValidationErrorType.SHACL_VIOLATION,
            ValidationErrorType.LOGIC_CONTRADICTION,
        ),
    ),
    EvaluationScenario(
        name="missing_location",
        description="Attraction missing required location triple; should fail SHACL validation.",
        build_payload=_missing_location_payload,
        expect_success=False,
        expected_error_types=(ValidationErrorType.SHACL_VIOLATION,),
    ),
]
