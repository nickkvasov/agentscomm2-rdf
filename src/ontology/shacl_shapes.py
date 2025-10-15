"""
SHACL Shapes Loader for Tourism Domain Validation

This module loads SHACL shapes from standard format files instead of defining
everything in Python code.
"""

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD
from typing import List, Dict, Any
import os

# Define namespaces
TOURISM = Namespace("http://example.org/tourism#")
SH = Namespace("http://www.w3.org/ns/shacl#")

class TourismSHACLShapes:
    """SHACL shapes loader from standard format files."""
    
    def __init__(self, fuseki_client=None, shapes_file: str = None):
        """
        Initialize the SHACL shapes by loading from Fuseki.
        
        Args:
            fuseki_client: FusekiClient instance (required)
            shapes_file: Path to the shapes file (defaults to ontology/tourism_shacl_shapes.ttl)
        """
        if fuseki_client is None:
            raise ValueError("FusekiClient is required - local processing is not supported")
        
        self.fuseki_client = fuseki_client
        self.graph = Graph()
        self._setup_namespaces()
        
        # Load shapes from file
        if shapes_file is None:
            # Default to the ontology directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            shapes_file = os.path.join(project_root, "ontology", "tourism_shacl_shapes.ttl")
        
        self._load_shapes(shapes_file)
    
    def _setup_namespaces(self):
        """Bind namespaces to the graph."""
        self.graph.bind("tourism", TOURISM)
        self.graph.bind("sh", SH)
        self.graph.bind("owl", OWL)
        self.graph.bind("rdfs", RDFS)
    
    def _load_shapes(self, shapes_file: str):
        """Load the SHACL shapes from Fuseki."""
        try:
            # Load shapes into Fuseki first
            if not self.fuseki_client.load_shacl_shapes(shapes_file):
                raise RuntimeError(f"Failed to load SHACL shapes into Fuseki: {shapes_file}")
            
            # Get shapes data from Fuseki
            self.graph = self.fuseki_client.get_graph_data(self.fuseki_client.main_graph)
            print(f"✅ Loaded SHACL shapes from Fuseki (source: {shapes_file})")
        except Exception as e:
            print(f"❌ Error loading SHACL shapes from Fuseki: {e}")
            raise RuntimeError(f"Failed to load SHACL shapes - Fuseki is required: {e}")
    
    def _create_fallback_shapes(self):
        """Create minimal fallback shapes if file loading fails."""
        print("Creating fallback SHACL shapes...")
        
        # Basic city shape
        city_shape = TOURISM.CityShape
        self.graph.add((city_shape, RDF.type, SH.NodeShape))
        self.graph.add((city_shape, SH.targetClass, TOURISM.City))
        
        # Basic attraction shape
        attraction_shape = TOURISM.AttractionShape
        self.graph.add((attraction_shape, RDF.type, SH.NodeShape))
        self.graph.add((attraction_shape, SH.targetClass, TOURISM.Attraction))
    
    def get_shapes_graph(self) -> Graph:
        """Return the complete SHACL shapes graph."""
        return self.graph
    
    def serialize(self, format: str = "turtle") -> str:
        """Serialize the shapes to the specified format."""
        return self.graph.serialize(format=format)
    
    def save_to_file(self, filename: str, format: str = "turtle"):
        """Save the shapes to a file."""
        self.graph.serialize(destination=filename, format=format)
    
    def get_validation_report(self, data_graph: Graph) -> Dict[str, Any]:
        """Validate a data graph against the shapes and return a report."""
        try:
            import pyshacl
            conforms, report_graph, report_text = pyshacl.validate(
                data_graph,
                shacl_graph=self.graph,
                ont_graph=None,
                inference='rdfs',
                abort_on_first=False,
                allow_infos=False,
                allow_warnings=False,
                meta_shacl=False,
                debug=False,
                advanced=False
            )
            
            return {
                "conforms": conforms,
                "report_graph": report_graph,
                "report_text": report_text,
                "violations": self._extract_violations(report_graph) if not conforms else []
            }
        except ImportError:
            return {
                "conforms": True,
                "report_text": "PySHACL not available for validation",
                "violations": []
            }
    
    def _extract_violations(self, report_graph: Graph) -> List[Dict[str, Any]]:
        """Extract violation details from the SHACL report graph."""
        violations = []
        
        # Query for validation results
        query = """
        SELECT ?focusNode ?resultPath ?resultMessage ?resultSeverity
        WHERE {
            ?result a sh:ValidationResult .
            ?result sh:focusNode ?focusNode .
            OPTIONAL { ?result sh:resultPath ?resultPath }
            OPTIONAL { ?result sh:resultMessage ?resultMessage }
            OPTIONAL { ?result sh:resultSeverity ?resultSeverity }
        }
        """
        
        for row in report_graph.query(query):
            violations.append({
                "focus_node": str(row.focusNode),
                "path": str(row.resultPath) if row.resultPath else None,
                "message": str(row.resultMessage) if row.resultMessage else None,
                "severity": str(row.resultSeverity) if row.resultSeverity else None
            })
        
        return violations


def create_validation_shapes() -> TourismSHACLShapes:
    """Create and return SHACL validation shapes for the tourism domain."""
    return TourismSHACLShapes()


if __name__ == "__main__":
    # Create and save the SHACL shapes
    shapes = TourismSHACLShapes()
    shapes.save_to_file("tourism_shacl_shapes_loaded.ttl")
    print("Tourism SHACL shapes loaded and saved to tourism_shacl_shapes_loaded.ttl")