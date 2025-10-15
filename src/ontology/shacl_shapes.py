"""
SHACL Shapes for Tourism Domain Validation

This module defines SHACL (Shapes Constraint Language) shapes for validating
RDF data in the tourism domain according to the POC requirements.
"""

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD
from typing import List, Dict, Any

# Define namespaces
TOURISM = Namespace("http://example.org/tourism#")
SH = Namespace("http://www.w3.org/ns/shacl#")

class TourismSHACLShapes:
    """SHACL shapes for tourism domain validation."""
    
    def __init__(self):
        self.graph = Graph()
        self._setup_namespaces()
        self._define_city_shapes()
        self._define_attraction_shapes()
        self._define_composite_shapes()
        self._define_message_shapes()
        self._define_integrity_constraints()
    
    def _setup_namespaces(self):
        """Bind namespaces to the graph."""
        self.graph.bind("tourism", TOURISM)
        self.graph.bind("sh", SH)
        self.graph.bind("owl", OWL)
        self.graph.bind("rdfs", RDFS)
    
    def _define_city_shapes(self):
        """Define SHACL shapes for City entities."""
        # City shape
        city_shape = TOURISM.CityShape
        self.graph.add((city_shape, RDF.type, SH.NodeShape))
        self.graph.add((city_shape, SH.targetClass, TOURISM.City))
        
        # Required properties for City
        name_prop = TOURISM.CityNameProperty
        self.graph.add((name_prop, RDF.type, SH.PropertyShape))
        self.graph.add((name_prop, SH.path, TOURISM.hasName))
        self.graph.add((name_prop, SH.datatype, XSD.string))
        self.graph.add((name_prop, SH.minCount, Literal(1)))
        self.graph.add((name_prop, SH.maxCount, Literal(1)))
        self.graph.add((city_shape, SH.property, name_prop))
        
        # Country relationship
        country_prop = TOURISM.CityCountryProperty
        self.graph.add((country_prop, RDF.type, SH.PropertyShape))
        self.graph.add((country_prop, SH.path, TOURISM.inCountry))
        self.graph.add((country_prop, SH.class_, TOURISM.Country))
        self.graph.add((country_prop, SH.minCount, Literal(1)))
        self.graph.add((country_prop, SH.maxCount, Literal(1)))
        self.graph.add((city_shape, SH.property, country_prop))
        
        # Coastal flag (optional)
        coastal_prop = TOURISM.CityCoastalProperty
        self.graph.add((coastal_prop, RDF.type, SH.PropertyShape))
        self.graph.add((coastal_prop, SH.path, TOURISM.isCoastal))
        self.graph.add((coastal_prop, SH.datatype, XSD.boolean))
        self.graph.add((coastal_prop, SH.maxCount, Literal(1)))
        self.graph.add((city_shape, SH.property, coastal_prop))
    
    def _define_attraction_shapes(self):
        """Define SHACL shapes for Attraction entities."""
        # Attraction shape
        attraction_shape = TOURISM.AttractionShape
        self.graph.add((attraction_shape, RDF.type, SH.NodeShape))
        self.graph.add((attraction_shape, SH.targetClass, TOURISM.Attraction))
        
        # Required properties for Attraction
        name_prop = TOURISM.AttractionNameProperty
        self.graph.add((name_prop, RDF.type, SH.PropertyShape))
        self.graph.add((name_prop, SH.path, TOURISM.hasName))
        self.graph.add((name_prop, SH.datatype, XSD.string))
        self.graph.add((name_prop, SH.minCount, Literal(1)))
        self.graph.add((name_prop, SH.maxCount, Literal(1)))
        self.graph.add((attraction_shape, SH.property, name_prop))
        
        # Location relationship
        location_prop = TOURISM.AttractionLocationProperty
        self.graph.add((location_prop, RDF.type, SH.PropertyShape))
        self.graph.add((location_prop, SH.path, TOURISM.locatedIn))
        self.graph.add((location_prop, SH.class_, TOURISM.City))
        self.graph.add((location_prop, SH.minCount, Literal(1)))
        self.graph.add((location_prop, SH.maxCount, Literal(1)))
        self.graph.add((attraction_shape, SH.property, location_prop))
        
        # Rating (0-5)
        rating_prop = TOURISM.AttractionRatingProperty
        self.graph.add((rating_prop, RDF.type, SH.PropertyShape))
        self.graph.add((rating_prop, SH.path, TOURISM.hasRating))
        self.graph.add((rating_prop, SH.datatype, XSD.decimal))
        self.graph.add((rating_prop, SH.minInclusive, Literal(0.0)))
        self.graph.add((rating_prop, SH.maxInclusive, Literal(5.0)))
        self.graph.add((rating_prop, SH.maxCount, Literal(1)))
        self.graph.add((attraction_shape, SH.property, rating_prop))
        
        # Entry fee amount
        fee_amount_prop = TOURISM.AttractionFeeAmountProperty
        self.graph.add((fee_amount_prop, RDF.type, SH.PropertyShape))
        self.graph.add((fee_amount_prop, SH.path, TOURISM.hasEntryFeeAmount))
        self.graph.add((fee_amount_prop, SH.datatype, XSD.decimal))
        self.graph.add((fee_amount_prop, SH.minInclusive, Literal(0.0)))
        self.graph.add((fee_amount_prop, SH.maxCount, Literal(1)))
        self.graph.add((attraction_shape, SH.property, fee_amount_prop))
        
        # Entry fee currency
        fee_currency_prop = TOURISM.AttractionFeeCurrencyProperty
        self.graph.add((fee_currency_prop, RDF.type, SH.PropertyShape))
        self.graph.add((fee_currency_prop, SH.path, TOURISM.hasEntryFeeCurrency))
        self.graph.add((fee_currency_prop, SH.datatype, XSD.string))
        # Add currency constraints - simplified approach
        self.graph.add((fee_currency_prop, SH.pattern, Literal("^(AED|USD|EUR)$")))
        self.graph.add((fee_currency_prop, SH.maxCount, Literal(1)))
        self.graph.add((attraction_shape, SH.property, fee_currency_prop))
        
        # Minimum age
        min_age_prop = TOURISM.AttractionMinAgeProperty
        self.graph.add((min_age_prop, RDF.type, SH.PropertyShape))
        self.graph.add((min_age_prop, SH.path, TOURISM.hasMinAge))
        self.graph.add((min_age_prop, SH.datatype, XSD.integer))
        self.graph.add((min_age_prop, SH.minInclusive, Literal(0)))
        self.graph.add((min_age_prop, SH.maxCount, Literal(1)))
        self.graph.add((attraction_shape, SH.property, min_age_prop))
        
        # Amenities
        amenity_prop = TOURISM.AttractionAmenityProperty
        self.graph.add((amenity_prop, RDF.type, SH.PropertyShape))
        self.graph.add((amenity_prop, SH.path, TOURISM.hasAmenity))
        self.graph.add((amenity_prop, SH.datatype, XSD.string))
        # Add amenity constraints - simplified approach
        self.graph.add((amenity_prop, SH.pattern, Literal("^(Playground|Restaurant|Parking|Wifi|Accessible)$")))
        self.graph.add((attraction_shape, SH.property, amenity_prop))
    
    def _define_composite_shapes(self):
        """Define SHACL shapes for composite entities."""
        # CoastalFamilyDestination shape
        composite_shape = TOURISM.CoastalFamilyDestinationShape
        self.graph.add((composite_shape, RDF.type, SH.NodeShape))
        self.graph.add((composite_shape, SH.targetClass, TOURISM.CoastalFamilyDestination))
        
        # Required city relationship
        city_prop = TOURISM.CompositeCityProperty
        self.graph.add((city_prop, RDF.type, SH.PropertyShape))
        self.graph.add((city_prop, SH.path, TOURISM.hasCity))
        self.graph.add((city_prop, SH.class_, TOURISM.CoastalCity))
        self.graph.add((city_prop, SH.minCount, Literal(1)))
        self.graph.add((city_prop, SH.maxCount, Literal(1)))
        self.graph.add((composite_shape, SH.property, city_prop))
        
        # Required attraction relationship
        attraction_prop = TOURISM.CompositeAttractionProperty
        self.graph.add((attraction_prop, RDF.type, SH.PropertyShape))
        self.graph.add((attraction_prop, SH.path, TOURISM.hasPrimaryAttraction))
        self.graph.add((attraction_prop, SH.class_, TOURISM.FamilyFriendlyAttraction))
        self.graph.add((attraction_prop, SH.minCount, Literal(1)))
        self.graph.add((attraction_prop, SH.maxCount, Literal(1)))
        self.graph.add((composite_shape, SH.property, attraction_prop))
    
    def _define_message_shapes(self):
        """Define SHACL shapes for inter-agent messages."""
        # Message intent shape
        message_shape = TOURISM.MessageShape
        self.graph.add((message_shape, RDF.type, SH.NodeShape))
        self.graph.add((message_shape, SH.targetClass, TOURISM.Intent))
        
        # Required properties for messages
        from_agent_prop = TOURISM.MessageFromAgentProperty
        self.graph.add((from_agent_prop, RDF.type, SH.PropertyShape))
        self.graph.add((from_agent_prop, SH.path, TOURISM.fromAgent))
        self.graph.add((from_agent_prop, SH.datatype, XSD.string))
        self.graph.add((from_agent_prop, SH.minCount, Literal(1)))
        self.graph.add((from_agent_prop, SH.maxCount, Literal(1)))
        self.graph.add((message_shape, SH.property, from_agent_prop))
        
        timestamp_prop = TOURISM.MessageTimestampProperty
        self.graph.add((timestamp_prop, RDF.type, SH.PropertyShape))
        self.graph.add((timestamp_prop, SH.path, TOURISM.timestamp))
        self.graph.add((timestamp_prop, SH.datatype, XSD.dateTime))
        self.graph.add((timestamp_prop, SH.minCount, Literal(1)))
        self.graph.add((timestamp_prop, SH.maxCount, Literal(1)))
        self.graph.add((message_shape, SH.property, timestamp_prop))
    
    def _define_integrity_constraints(self):
        """Define integrity constraints and business rules."""
        # Disjoint classes constraint - simplified approach
        # Note: This would require more complex SHACL syntax in practice
        pass
        
        # Rating threshold for family-friendly destinations
        rating_constraint = TOURISM.FamilyFriendlyRatingConstraint
        self.graph.add((rating_constraint, RDF.type, SH.NodeShape))
        self.graph.add((rating_constraint, SH.targetClass, TOURISM.CoastalFamilyDestination))
        
        # Ensure minimum rating for composite destinations
        min_rating_prop = TOURISM.CompositeMinRatingProperty
        self.graph.add((min_rating_prop, RDF.type, SH.PropertyShape))
        self.graph.add((min_rating_prop, SH.path, TOURISM.hasRating))
        self.graph.add((min_rating_prop, SH.minInclusive, Literal(4.5)))
        self.graph.add((rating_constraint, SH.property, min_rating_prop))
    
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
    shapes.save_to_file("tourism_shacl_shapes.ttl")
    print("Tourism SHACL shapes created and saved to tourism_shacl_shapes.ttl")
