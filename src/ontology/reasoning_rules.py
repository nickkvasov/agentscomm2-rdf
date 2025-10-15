"""
Forward-Chaining Reasoning Rules for Tourism Domain

This module implements the reasoning rules for materializing higher-level concepts
and detecting contradictions in the tourism domain according to the POC requirements.
"""

from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD
from typing import List, Dict, Any, Set, Tuple, Optional
import logging

# Define namespaces
TOURISM = Namespace("http://example.org/tourism#")
MSG = Namespace("http://example.org/messages#")
RULES = Namespace("http://example.org/rules#")

logger = logging.getLogger(__name__)

class TourismReasoningEngine:
    """Forward-chaining reasoning engine for tourism domain."""
    
    def __init__(self):
        self.rules = []
        self._define_rules()
        self.derived_facts = set()
        self.contradictions = []
    
    def _define_rules(self):
        """Define forward-chaining reasoning rules."""
        self.rules = [
            self._rule_coastal_attraction,
            self._rule_family_friendly_playground,
            self._rule_not_family_friendly_age,
            self._rule_coastal_family_destination,
            self._rule_contradiction_detection
        ]
    
    def _rule_coastal_attraction(self, graph: Graph) -> List[Tuple]:
        """Rule: Attraction in CoastalCity => CoastalAttraction"""
        new_facts = []
        
        query = """
        SELECT ?attraction ?city
        WHERE {
            ?attraction tourism:locatedIn ?city .
            ?city rdf:type tourism:CoastalCity .
            ?attraction rdf:type tourism:Attraction .
            FILTER NOT EXISTS { ?attraction rdf:type tourism:CoastalAttraction }
        }
        """
        
        for row in graph.query(query):
            attraction = row.attraction
            new_facts.append((attraction, RDF.type, TOURISM.CoastalAttraction))
            logger.info(f"Derived: {attraction} is a CoastalAttraction")
        
        return new_facts
    
    def _rule_family_friendly_playground(self, graph: Graph) -> List[Tuple]:
        """Rule: Attraction with Playground amenity => FamilyFriendlyAttraction"""
        new_facts = []
        
        query = """
        SELECT ?attraction
        WHERE {
            ?attraction rdf:type tourism:Attraction .
            ?attraction tourism:hasAmenity "Playground" .
            FILTER NOT EXISTS { ?attraction rdf:type tourism:FamilyFriendlyAttraction }
        }
        """
        
        for row in graph.query(query):
            attraction = row.attraction
            new_facts.append((attraction, RDF.type, TOURISM.FamilyFriendlyAttraction))
            logger.info(f"Derived: {attraction} is FamilyFriendlyAttraction (has Playground)")
        
        return new_facts
    
    def _rule_not_family_friendly_age(self, graph: Graph) -> List[Tuple]:
        """Rule: Attraction with MinAge > 12 => NotFamilyFriendlyAttraction"""
        new_facts = []
        
        query = """
        SELECT ?attraction ?minAge
        WHERE {
            ?attraction rdf:type tourism:Attraction .
            ?attraction tourism:hasMinAge ?minAge .
            FILTER(?minAge > 12)
            FILTER NOT EXISTS { ?attraction rdf:type tourism:NotFamilyFriendlyAttraction }
        }
        """
        
        for row in graph.query(query):
            attraction = row.attraction
            min_age = row.minAge
            new_facts.append((attraction, RDF.type, TOURISM.NotFamilyFriendlyAttraction))
            logger.info(f"Derived: {attraction} is NotFamilyFriendlyAttraction (MinAge: {min_age})")
        
        return new_facts
    
    def _rule_coastal_family_destination(self, graph: Graph) -> List[Tuple]:
        """Rule: CoastalCity + FamilyFriendlyAttraction + Rating >= 4.5 => CoastalFamilyDestination"""
        new_facts = []
        
        query = """
        SELECT ?city ?attraction ?rating
        WHERE {
            ?city rdf:type tourism:CoastalCity .
            ?attraction rdf:type tourism:FamilyFriendlyAttraction .
            ?attraction tourism:locatedIn ?city .
            ?attraction tourism:hasRating ?rating .
            FILTER(?rating >= 4.5)
            FILTER NOT EXISTS {
                ?destination rdf:type tourism:CoastalFamilyDestination .
                ?destination tourism:hasCity ?city .
                ?destination tourism:hasPrimaryAttraction ?attraction .
            }
        }
        """
        
        for row in graph.query(query):
            city = row.city
            attraction = row.attraction
            rating = row.rating
            
            # Create a new composite destination
            destination = TOURISM[f"CoastalFamilyDestination_{city.split('#')[-1]}_{attraction.split('#')[-1]}"]
            
            new_facts.extend([
                (destination, RDF.type, TOURISM.CoastalFamilyDestination),
                (destination, TOURISM.hasCity, city),
                (destination, TOURISM.hasPrimaryAttraction, attraction),
                (destination, TOURISM.hasRating, Literal(rating))
            ])
            
            logger.info(f"Derived: {destination} is a CoastalFamilyDestination (City: {city}, Attraction: {attraction}, Rating: {rating})")
        
        return new_facts
    
    def _rule_contradiction_detection(self, graph: Graph) -> List[Tuple]:
        """Rule: Detect contradictions (disjoint classes)"""
        contradictions = []
        
        # Check for FamilyFriendlyAttraction and NotFamilyFriendlyAttraction contradiction
        query = """
        SELECT ?entity
        WHERE {
            ?entity rdf:type tourism:FamilyFriendlyAttraction .
            ?entity rdf:type tourism:NotFamilyFriendlyAttraction .
        }
        """
        
        for row in graph.query(query):
            entity = row.entity
            contradiction = {
                "type": "DISJOINT_CLASS_VIOLATION",
                "entity": str(entity),
                "conflicting_types": ["FamilyFriendlyAttraction", "NotFamilyFriendlyAttraction"],
                "message": f"Entity {entity} cannot be both FamilyFriendly and NotFamilyFriendly"
            }
            contradictions.append(contradiction)
            logger.warning(f"Contradiction detected: {contradiction['message']}")
        
        return contradictions
    
    def run_reasoning(self, graph: Graph, max_iterations: int = 10) -> Dict[str, Any]:
        """
        Run forward-chaining reasoning to fixpoint.
        
        Args:
            graph: The RDF graph to reason over
            max_iterations: Maximum number of reasoning iterations
            
        Returns:
            Dictionary with reasoning results including derived facts and contradictions
        """
        logger.info("Starting forward-chaining reasoning")
        
        new_facts = []
        all_derived_facts = []
        contradictions = []
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Reasoning iteration {iteration}")
            
            iteration_facts = []
            iteration_contradictions = []
            
            # Apply all rules
            for rule in self.rules:
                try:
                    if rule == self._rule_contradiction_detection:
                        rule_contradictions = rule(graph)
                        iteration_contradictions.extend(rule_contradictions)
                    else:
                        rule_facts = rule(graph)
                        iteration_facts.extend(rule_facts)
                except Exception as e:
                    logger.error(f"Error applying rule {rule.__name__}: {e}")
                    continue
            
            # Add new facts to graph
            for fact in iteration_facts:
                if fact not in all_derived_facts:
                    graph.add(fact)
                    all_derived_facts.append(fact)
                    new_facts.append(fact)
                    logger.debug(f"Added fact: {fact}")
            
            # Check for contradictions
            if iteration_contradictions:
                contradictions.extend(iteration_contradictions)
                logger.warning(f"Found {len(iteration_contradictions)} contradictions")
            
            # If no new facts were derived, we've reached fixpoint
            if not iteration_facts:
                logger.info(f"Reached fixpoint after {iteration} iterations")
                break
        
        if iteration >= max_iterations:
            logger.warning(f"Reached maximum iterations ({max_iterations}) without reaching fixpoint")
        
        return {
            "derived_facts": new_facts,
            "all_derived_facts": all_derived_facts,
            "contradictions": contradictions,
            "iterations": iteration,
            "reached_fixpoint": iteration < max_iterations
        }
    
    def validate_consistency(self, graph: Graph) -> Dict[str, Any]:
        """
        Validate logical consistency of the graph.
        
        Args:
            graph: The RDF graph to validate
            
        Returns:
            Dictionary with validation results
        """
        logger.info("Validating logical consistency")
        
        # Run contradiction detection
        contradictions = self._rule_contradiction_detection(graph)
        
        # Check for other consistency issues
        consistency_issues = []
        
        # Check for functional property violations
        functional_violations = self._check_functional_properties(graph)
        consistency_issues.extend(functional_violations)
        
        # Check for domain/range violations
        domain_range_violations = self._check_domain_range(graph)
        consistency_issues.extend(domain_range_violations)
        
        return {
            "is_consistent": len(contradictions) == 0 and len(consistency_issues) == 0,
            "contradictions": contradictions,
            "consistency_issues": consistency_issues,
            "total_issues": len(contradictions) + len(consistency_issues)
        }
    
    def _check_functional_properties(self, graph: Graph) -> List[Dict[str, Any]]:
        """Check for functional property violations."""
        violations = []
        
        # Check locatedIn functional property
        query = """
        SELECT ?attraction ?city1 ?city2
        WHERE {
            ?attraction tourism:locatedIn ?city1 .
            ?attraction tourism:locatedIn ?city2 .
            FILTER(?city1 != ?city2)
        }
        """
        
        for row in graph.query(query):
            violation = {
                "type": "FUNCTIONAL_PROPERTY_VIOLATION",
                "property": "tourism:locatedIn",
                "entity": str(row.attraction),
                "values": [str(row.city1), str(row.city2)],
                "message": f"Attraction {row.attraction} is located in multiple cities"
            }
            violations.append(violation)
        
        return violations
    
    def _check_domain_range(self, graph: Graph) -> List[Dict[str, Any]]:
        """Check for domain/range violations."""
        violations = []
        
        # Check rating range (0-5)
        query = """
        SELECT ?entity ?rating
        WHERE {
            ?entity tourism:hasRating ?rating .
            FILTER(?rating < 0 || ?rating > 5)
        }
        """
        
        for row in graph.query(query):
            violation = {
                "type": "RANGE_VIOLATION",
                "property": "tourism:hasRating",
                "entity": str(row.entity),
                "value": str(row.rating),
                "message": f"Rating {row.rating} is outside valid range [0, 5]"
            }
            violations.append(violation)
        
        return violations
    
    def get_derived_facts_summary(self, graph: Graph) -> Dict[str, int]:
        """Get summary of derived facts by type."""
        summary = {}
        
        # Count derived classes
        query = """
        SELECT ?type (COUNT(?entity) as ?count)
        WHERE {
            ?entity rdf:type ?type .
            FILTER(?type IN (tourism:CoastalAttraction, tourism:FamilyFriendlyAttraction, 
                           tourism:NotFamilyFriendlyAttraction, tourism:CoastalFamilyDestination))
        }
        GROUP BY ?type
        """
        
        for row in graph.query(query):
            summary[str(row.type)] = int(row.count)
        
        return summary


def create_reasoning_engine() -> TourismReasoningEngine:
    """Create and return a tourism reasoning engine."""
    return TourismReasoningEngine()


if __name__ == "__main__":
    # Test the reasoning engine
    from .tourism_ontology import create_sample_data
    
    # Create sample data
    sample_graph = create_sample_data()
    
    # Create reasoning engine
    engine = TourismReasoningEngine()
    
    # Run reasoning
    results = engine.run_reasoning(sample_graph)
    
    print("Reasoning Results:")
    print(f"Derived facts: {len(results['derived_facts'])}")
    print(f"Contradictions: {len(results['contradictions'])}")
    print(f"Iterations: {results['iterations']}")
    print(f"Reached fixpoint: {results['reached_fixpoint']}")
    
    # Validate consistency
    consistency = engine.validate_consistency(sample_graph)
    print(f"\nConsistency check: {consistency['is_consistent']}")
    
    # Get summary
    summary = engine.get_derived_facts_summary(sample_graph)
    print(f"\nDerived facts summary: {summary}")
