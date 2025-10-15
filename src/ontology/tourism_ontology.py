"""
Tourism Domain Ontology for Multi-Agent Collaboration POC

This module defines the RDF ontology for the tourism domain including:
- Core classes: City, CoastalCity, Country, Attraction, etc.
- Properties: locatedIn, inCountry, hasAmenity, hasRating, etc.
- Composite concepts: CoastalFamilyDestination
- Message vocabulary for inter-agent communication
"""

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD
from typing import Dict, List, Optional

# Define namespaces
TOURISM = Namespace("http://example.org/tourism#")
MSG = Namespace("http://example.org/messages#")
SHACL = Namespace("http://www.w3.org/ns/shacl#")

class TourismOntology:
    """Tourism domain ontology with classes, properties, and constraints."""
    
    def __init__(self):
        self.graph = Graph()
        self._setup_namespaces()
        self._define_classes()
        self._define_properties()
        self._define_constraints()
        self._define_composite_concepts()
        self._define_message_vocabulary()
    
    def _setup_namespaces(self):
        """Bind namespaces to the graph."""
        self.graph.bind("tourism", TOURISM)
        self.graph.bind("msg", MSG)
        self.graph.bind("shacl", SHACL)
        self.graph.bind("owl", OWL)
        self.graph.bind("rdfs", RDFS)
    
    def _define_classes(self):
        """Define core classes and their hierarchy."""
        # Core classes
        self.graph.add((TOURISM.City, RDF.type, OWL.Class))
        self.graph.add((TOURISM.Country, RDF.type, OWL.Class))
        self.graph.add((TOURISM.Attraction, RDF.type, OWL.Class))
        
        # Specialized classes
        self.graph.add((TOURISM.CoastalCity, RDF.type, OWL.Class))
        self.graph.add((TOURISM.CoastalCity, RDFS.subClassOf, TOURISM.City))
        
        self.graph.add((TOURISM.CoastalAttraction, RDF.type, OWL.Class))
        self.graph.add((TOURISM.CoastalAttraction, RDFS.subClassOf, TOURISM.Attraction))
        
        self.graph.add((TOURISM.FamilyFriendlyAttraction, RDF.type, OWL.Class))
        self.graph.add((TOURISM.FamilyFriendlyAttraction, RDFS.subClassOf, TOURISM.Attraction))
        
        self.graph.add((TOURISM.NotFamilyFriendlyAttraction, RDF.type, OWL.Class))
        self.graph.add((TOURISM.NotFamilyFriendlyAttraction, RDFS.subClassOf, TOURISM.Attraction))
        
        # Disjoint classes
        self.graph.add((TOURISM.FamilyFriendlyAttraction, OWL.disjointWith, TOURISM.NotFamilyFriendlyAttraction))
        
        # Composite concept
        self.graph.add((TOURISM.CoastalFamilyDestination, RDF.type, OWL.Class))
    
    def _define_properties(self):
        """Define object and data properties."""
        # Object properties
        self.graph.add((TOURISM.locatedIn, RDF.type, OWL.ObjectProperty))
        self.graph.add((TOURISM.locatedIn, RDFS.domain, TOURISM.Attraction))
        self.graph.add((TOURISM.locatedIn, RDFS.range, TOURISM.City))
        
        self.graph.add((TOURISM.inCountry, RDF.type, OWL.ObjectProperty))
        self.graph.add((TOURISM.inCountry, RDFS.domain, TOURISM.City))
        self.graph.add((TOURISM.inCountry, RDFS.range, TOURISM.Country))
        
        self.graph.add((TOURISM.hasPrimaryAttraction, RDF.type, OWL.ObjectProperty))
        self.graph.add((TOURISM.hasPrimaryAttraction, RDFS.domain, TOURISM.CoastalFamilyDestination))
        self.graph.add((TOURISM.hasPrimaryAttraction, RDFS.range, TOURISM.Attraction))
        
        self.graph.add((TOURISM.hasCity, RDF.type, OWL.ObjectProperty))
        self.graph.add((TOURISM.hasCity, RDFS.domain, TOURISM.CoastalFamilyDestination))
        self.graph.add((TOURISM.hasCity, RDFS.range, TOURISM.City))
        
        # Data properties
        self.graph.add((TOURISM.hasAmenity, RDF.type, OWL.DatatypeProperty))
        self.graph.add((TOURISM.hasAmenity, RDFS.domain, TOURISM.Attraction))
        self.graph.add((TOURISM.hasAmenity, RDFS.range, XSD.string))
        
        self.graph.add((TOURISM.hasRating, RDF.type, OWL.DatatypeProperty))
        self.graph.add((TOURISM.hasRating, RDFS.domain, TOURISM.Attraction))
        self.graph.add((TOURISM.hasRating, RDFS.range, XSD.decimal))
        
        self.graph.add((TOURISM.hasEntryFeeAmount, RDF.type, OWL.DatatypeProperty))
        self.graph.add((TOURISM.hasEntryFeeAmount, RDFS.domain, TOURISM.Attraction))
        self.graph.add((TOURISM.hasEntryFeeAmount, RDFS.range, XSD.decimal))
        
        self.graph.add((TOURISM.hasEntryFeeCurrency, RDF.type, OWL.DatatypeProperty))
        self.graph.add((TOURISM.hasEntryFeeCurrency, RDFS.domain, TOURISM.Attraction))
        self.graph.add((TOURISM.hasEntryFeeCurrency, RDFS.range, XSD.string))
        
        self.graph.add((TOURISM.hasMinAge, RDF.type, OWL.DatatypeProperty))
        self.graph.add((TOURISM.hasMinAge, RDFS.domain, TOURISM.Attraction))
        self.graph.add((TOURISM.hasMinAge, RDFS.range, XSD.integer))
        
        self.graph.add((TOURISM.isCoastal, RDF.type, OWL.DatatypeProperty))
        self.graph.add((TOURISM.isCoastal, RDFS.domain, TOURISM.City))
        self.graph.add((TOURISM.isCoastal, RDFS.range, XSD.boolean))
        
        self.graph.add((TOURISM.hasName, RDF.type, OWL.DatatypeProperty))
        self.graph.add((TOURISM.hasName, RDFS.domain, TOURISM.City))
        self.graph.add((TOURISM.hasName, RDFS.range, XSD.string))
        
        self.graph.add((TOURISM.hasName, RDFS.domain, TOURISM.Attraction))
        self.graph.add((TOURISM.hasName, RDFS.domain, TOURISM.Country))
    
    def _define_constraints(self):
        """Define functional properties and constraints."""
        # Functional properties
        self.graph.add((TOURISM.locatedIn, RDF.type, OWL.FunctionalProperty))
        self.graph.add((TOURISM.inCountry, RDF.type, OWL.FunctionalProperty))
        
        # Rating constraints (0-5)
        self.graph.add((TOURISM.hasRating, RDFS.range, XSD.decimal))
        
        # Currency constraints
        self.graph.add((TOURISM.hasEntryFeeCurrency, RDFS.range, XSD.string))
    
    def _define_composite_concepts(self):
        """Define composite concepts and their relationships."""
        # CoastalFamilyDestination requires both coastal city and family-friendly attraction
        self.graph.add((TOURISM.CoastalFamilyDestination, RDFS.comment, 
                       Literal("A destination that combines a coastal city with a family-friendly attraction")))
    
    def _define_message_vocabulary(self):
        """Define vocabulary for inter-agent messages."""
        # Message types
        self.graph.add((MSG.Intent, RDF.type, OWL.Class))
        self.graph.add((MSG.Intent, RDFS.comment, Literal("Represents an agent's intent or action")))
        
        # Message properties
        self.graph.add((MSG.about, RDF.type, OWL.ObjectProperty))
        self.graph.add((MSG.about, RDFS.domain, MSG.Intent))
        self.graph.add((MSG.about, RDFS.range, OWL.Thing))
        
        self.graph.add((MSG.payloadGraph, RDF.type, OWL.ObjectProperty))
        self.graph.add((MSG.payloadGraph, RDFS.domain, MSG.Intent))
        self.graph.add((MSG.payloadGraph, RDFS.range, OWL.Thing))
        
        self.graph.add((MSG.fromAgent, RDF.type, OWL.DatatypeProperty))
        self.graph.add((MSG.fromAgent, RDFS.domain, MSG.Intent))
        self.graph.add((MSG.fromAgent, RDFS.range, XSD.string))
        
        self.graph.add((MSG.timestamp, RDF.type, OWL.DatatypeProperty))
        self.graph.add((MSG.timestamp, RDFS.domain, MSG.Intent))
        self.graph.add((MSG.timestamp, RDFS.range, XSD.dateTime))
    
    def get_ontology_graph(self) -> Graph:
        """Return the complete ontology graph."""
        return self.graph
    
    def serialize(self, format: str = "turtle") -> str:
        """Serialize the ontology to the specified format."""
        return self.graph.serialize(format=format)
    
    def save_to_file(self, filename: str, format: str = "turtle"):
        """Save the ontology to a file."""
        self.graph.serialize(destination=filename, format=format)
    
    def get_controlled_vocabularies(self) -> Dict[str, List[str]]:
        """Return controlled vocabularies for validation."""
        return {
            "currencies": ["AED", "USD", "EUR"],
            "amenities": ["Playground", "Restaurant", "Parking", "Wifi", "Accessible"],
            "agent_types": ["Ingest", "Collect", "Reason"]
        }
    
    def get_validation_rules(self) -> List[Dict]:
        """Return validation rules for the ontology."""
        return [
            {
                "rule": "rating_range",
                "property": TOURISM.hasRating,
                "constraint": "min: 0, max: 5"
            },
            {
                "rule": "currency_values",
                "property": TOURISM.hasEntryFeeCurrency,
                "constraint": "enum: AED, USD, EUR"
            },
            {
                "rule": "disjoint_family_friendly",
                "classes": [TOURISM.FamilyFriendlyAttraction, TOURISM.NotFamilyFriendlyAttraction],
                "constraint": "disjoint"
            }
        ]


def create_sample_data() -> Graph:
    """Create sample tourism data for testing."""
    g = Graph()
    g.bind("tourism", TOURISM)
    
    # Sample cities
    g.add((TOURISM.Dubai, RDF.type, TOURISM.CoastalCity))
    g.add((TOURISM.Dubai, TOURISM.hasName, Literal("Dubai")))
    g.add((TOURISM.Dubai, TOURISM.isCoastal, Literal(True)))
    g.add((TOURISM.Dubai, TOURISM.inCountry, TOURISM.UAE))
    
    g.add((TOURISM.UAE, RDF.type, TOURISM.Country))
    g.add((TOURISM.UAE, TOURISM.hasName, Literal("United Arab Emirates")))
    
    # Sample attractions
    g.add((TOURISM.DubaiAquarium, RDF.type, TOURISM.Attraction))
    g.add((TOURISM.DubaiAquarium, TOURISM.hasName, Literal("Dubai Aquarium")))
    g.add((TOURISM.DubaiAquarium, TOURISM.locatedIn, TOURISM.Dubai))
    g.add((TOURISM.DubaiAquarium, TOURISM.hasAmenity, Literal("Playground")))
    g.add((TOURISM.DubaiAquarium, TOURISM.hasRating, Literal(4.6)))
    g.add((TOURISM.DubaiAquarium, TOURISM.hasEntryFeeAmount, Literal(25.0)))
    g.add((TOURISM.DubaiAquarium, TOURISM.hasEntryFeeCurrency, Literal("AED")))
    
    return g


if __name__ == "__main__":
    # Create and save the ontology
    ontology = TourismOntology()
    ontology.save_to_file("tourism_ontology.ttl")
    print("Tourism ontology created and saved to tourism_ontology.ttl")
    
    # Create sample data
    sample_data = create_sample_data()
    sample_data.serialize(destination="sample_tourism_data.ttl", format="turtle")
    print("Sample tourism data created and saved to sample_tourism_data.ttl")
