"""
Tourism Domain Ontology Loader

This module loads the tourism domain ontology from standard RDF/OWL format files
instead of defining everything in Python code.
"""

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD
from typing import Dict, List, Optional
import os

# Define namespaces
TOURISM = Namespace("http://example.org/tourism#")
MSG = Namespace("http://example.org/messages#")
SHACL = Namespace("http://www.w3.org/ns/shacl#")

class TourismOntology:
    """Tourism domain ontology loader from standard RDF/OWL files."""
    
    def __init__(self, fuseki_client=None, ontology_file: str = None):
        """
        Initialize the ontology by loading from Fuseki.
        
        Args:
            fuseki_client: FusekiClient instance (required)
            ontology_file: Path to the ontology file (defaults to ontology/tourism_ontology.ttl)
        """
        if fuseki_client is None:
            raise ValueError("FusekiClient is required - local processing is not supported")
        
        self.fuseki_client = fuseki_client
        self.graph = Graph()
        self._setup_namespaces()
        
        # Load ontology from file
        if ontology_file is None:
            # Default to the ontology directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            ontology_file = os.path.join(project_root, "ontology", "tourism_ontology.ttl")
        
        self._load_ontology(ontology_file)
    
    def _setup_namespaces(self):
        """Bind namespaces to the graph."""
        self.graph.bind("tourism", TOURISM)
        self.graph.bind("msg", MSG)
        self.graph.bind("shacl", SHACL)
        self.graph.bind("owl", OWL)
        self.graph.bind("rdfs", RDFS)
    
    def _load_ontology(self, ontology_file: str):
        """Load the ontology from Fuseki."""
        try:
            # Load ontology into Fuseki first
            if not self.fuseki_client.load_ontology(ontology_file):
                raise RuntimeError(f"Failed to load ontology into Fuseki: {ontology_file}")
            
            # Get ontology data from Fuseki
            self.graph = self.fuseki_client.get_graph_data(self.fuseki_client.main_graph)
            print(f"✅ Loaded tourism ontology from Fuseki (source: {ontology_file})")
        except Exception as e:
            print(f"❌ Error loading ontology from Fuseki: {e}")
            raise RuntimeError(f"Failed to load ontology - Fuseki is required: {e}")
    
    def _create_fallback_ontology(self):
        """Create a minimal fallback ontology if file loading fails."""
        print("Creating fallback ontology...")
        
        # Basic classes
        self.graph.add((TOURISM.City, RDF.type, OWL.Class))
        self.graph.add((TOURISM.Country, RDF.type, OWL.Class))
        self.graph.add((TOURISM.Attraction, RDF.type, OWL.Class))
        
        # Basic properties
        self.graph.add((TOURISM.locatedIn, RDF.type, OWL.ObjectProperty))
        self.graph.add((TOURISM.locatedIn, RDFS.domain, TOURISM.Attraction))
        self.graph.add((TOURISM.locatedIn, RDFS.range, TOURISM.City))
        
        self.graph.add((TOURISM.hasName, RDF.type, OWL.DatatypeProperty))
        self.graph.add((TOURISM.hasName, RDFS.domain, TOURISM.City))
        self.graph.add((TOURISM.hasName, RDFS.range, XSD.string))
    
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
    ontology.save_to_file("tourism_ontology_loaded.ttl")
    print("Tourism ontology loaded and saved to tourism_ontology_loaded.ttl")
    
    # Create sample data
    sample_data = create_sample_data()
    sample_data.serialize(destination="sample_tourism_data.ttl", format="turtle")
    print("Sample tourism data created and saved to sample_tourism_data.ttl")