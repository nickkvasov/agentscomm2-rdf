"""
Test Scenarios for Multi-Agent Collaboration POC

This module implements the test scenarios described in the POC document
to validate the system's functionality according to the acceptance criteria.
"""

import pytest
import time
import logging
from typing import Dict, List, Any, Optional
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD

from ontology.tourism_ontology import TourismOntology, create_sample_data
from ontology.shacl_shapes import TourismSHACLShapes
from ontology.reasoning_rules import TourismReasoningEngine
from gateway.validator_gateway import ValidatorGateway
from agents.ingest_agent import IngestAgent
from agents.collect_agent import CollectAgent
from agents.reason_agent import ReasonAgent

# Define namespaces
TOURISM = Namespace("http://example.org/tourism#")

logger = logging.getLogger(__name__)

class TestScenarios:
    """Test scenarios for the POC system."""
    
    def __init__(self):
        """Initialize test scenarios."""
        self.ontology = TourismOntology()
        self.shacl_shapes = TourismSHACLShapes()
        self.reasoning_engine = TourismReasoningEngine()
        self.gateway = None
        self.agents = {}
        
        # Test results
        self.test_results = {}
        
        logger.info("Test scenarios initialized")
    
    def setup_gateway(self, fuseki_endpoint: str = "http://localhost:3030/ds"):
        """Setup the validator gateway for testing."""
        self.gateway = ValidatorGateway(fuseki_endpoint)
        
        # Register test agents
        self.gateway.register_agent("test_ingest", "key_ingest_123", ["read", "write_staging"])
        self.gateway.register_agent("test_collect", "key_collect_456", ["read", "write_staging"])
        self.gateway.register_agent("test_reason", "key_reason_789", ["read", "write_staging"])
        
        logger.info("Gateway setup completed")
    
    def setup_agents(self, gateway_url: str = "http://localhost:8000"):
        """Setup test agents."""
        self.agents = {
            "ingest": IngestAgent("test_ingest", gateway_url),
            "collect": CollectAgent("test_collect", gateway_url),
            "reason": ReasonAgent("test_reason", gateway_url)
        }
        
        logger.info("Test agents setup completed")
    
    def run_all_scenarios(self) -> Dict[str, Any]:
        """Run all test scenarios."""
        logger.info("Starting all test scenarios")
        
        results = {}
        
        # Test 1: Happy Path
        results["happy_path"] = self.test_happy_path()
        
        # Test 2: Shape Rejection
        results["shape_rejection"] = self.test_shape_rejection()
        
        # Test 3: Logic Contradiction
        results["logic_contradiction"] = self.test_logic_contradiction()
        
        # Test 4: Rescission
        results["rescission"] = self.test_rescission()
        
        # Test 5: Cross-graph Consistency
        results["cross_graph_consistency"] = self.test_cross_graph_consistency()
        
        self.test_results = results
        logger.info("All test scenarios completed")
        
        return results
    
    def test_happy_path(self) -> Dict[str, Any]:
        """
        Test Scenario 1: Happy Path
        
        Two agents collaborate successfully:
        - Agent A supplies City (coastal) and Attraction (playground, fee, currency, rating 4.6)
        - Agent B adds complementary facts
        - Expected: SHACL pass; rules derive CoastalCity, CoastalAttraction, FamilyFriendlyAttraction; 
          composite destination materialized; selected derived facts promoted to Main
        """
        logger.info("Running Happy Path test scenario")
        
        try:
            # Create test data
            test_graph = Graph()
            test_graph.bind("tourism", TOURISM)
            
            # Agent A data: Coastal city
            dubai = TOURISM.City_Dubai
            test_graph.add((dubai, RDF.type, TOURISM.City))
            test_graph.add((dubai, TOURISM.hasName, Literal("Dubai")))
            test_graph.add((dubai, TOURISM.isCoastal, Literal(True)))
            test_graph.add((dubai, TOURISM.inCountry, TOURISM.Country_UAE))
            
            # Agent A data: Attraction with playground
            aquarium = TOURISM.Attraction_DubaiAquarium
            test_graph.add((aquarium, RDF.type, TOURISM.Attraction))
            test_graph.add((aquarium, TOURISM.hasName, Literal("Dubai Aquarium")))
            test_graph.add((aquarium, TOURISM.locatedIn, dubai))
            test_graph.add((aquarium, TOURISM.hasAmenity, Literal("Playground")))
            test_graph.add((aquarium, TOURISM.hasRating, Literal(4.6)))
            test_graph.add((aquarium, TOURISM.hasEntryFeeAmount, Literal(25.0)))
            test_graph.add((aquarium, TOURISM.hasEntryFeeCurrency, Literal("AED")))
            
            # Validate with SHACL
            shacl_result = self.shacl_shapes.get_validation_report(test_graph)
            
            # Run reasoning
            reasoning_result = self.reasoning_engine.run_reasoning(test_graph)
            
            # Check for derived facts
            derived_facts = reasoning_result["derived_facts"]
            derived_types = set()
            
            for fact in derived_facts:
                if fact[1] == RDF.type:
                    derived_types.add(str(fact[2]))
            
            # Validate expected derived facts
            expected_derivations = {
                str(TOURISM.CoastalCity),
                str(TOURISM.CoastalAttraction),
                str(TOURISM.FamilyFriendlyAttraction)
            }
            
            # Check for composite destination
            composite_destinations = []
            for fact in derived_facts:
                if fact[1] == RDF.type and str(fact[2]) == str(TOURISM.CoastalFamilyDestination):
                    composite_destinations.append(fact[0])
            
            # Validate results
            success = (
                shacl_result["conforms"] and
                reasoning_result["reached_fixpoint"] and
                len(reasoning_result["contradictions"]) == 0 and
                expected_derivations.issubset(derived_types) and
                len(composite_destinations) > 0
            )
            
            result = {
                "success": success,
                "shacl_conforms": shacl_result["conforms"],
                "reasoning_reached_fixpoint": reasoning_result["reached_fixpoint"],
                "contradictions": len(reasoning_result["contradictions"]),
                "derived_facts_count": len(derived_facts),
                "derived_types": list(derived_types),
                "composite_destinations": len(composite_destinations),
                "reasoning_iterations": reasoning_result["iterations"]
            }
            
            logger.info(f"Happy Path test result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Happy Path test failed: {e}")
            return {"success": False, "error": str(e)}
    
    def test_shape_rejection(self) -> Dict[str, Any]:
        """
        Test Scenario 2: Shape Rejection
        
        Agent A attempts to assert a non-decimal entry fee.
        Expected: reject; SHACL report captured; no change to Consensus.
        """
        logger.info("Running Shape Rejection test scenario")
        
        try:
            # Create invalid data (non-decimal entry fee)
            test_graph = Graph()
            test_graph.bind("tourism", TOURISM)
            
            # Valid attraction with invalid entry fee
            aquarium = TOURISM.Attraction_DubaiAquarium
            test_graph.add((aquarium, RDF.type, TOURISM.Attraction))
            test_graph.add((aquarium, TOURISM.hasName, Literal("Dubai Aquarium")))
            test_graph.add((aquarium, TOURISM.locatedIn, TOURISM.City_Dubai))
            test_graph.add((aquarium, TOURISM.hasEntryFeeAmount, Literal("not_a_number")))  # Invalid!
            test_graph.add((aquarium, TOURISM.hasEntryFeeCurrency, Literal("AED")))
            
            # Validate with SHACL
            shacl_result = self.shacl_shapes.get_validation_report(test_graph)
            
            # Should fail validation
            success = not shacl_result["conforms"] and len(shacl_result["violations"]) > 0
            
            result = {
                "success": success,
                "shacl_conforms": shacl_result["conforms"],
                "violations": len(shacl_result["violations"]),
                "violation_details": shacl_result["violations"]
            }
            
            logger.info(f"Shape Rejection test result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Shape Rejection test failed: {e}")
            return {"success": False, "error": str(e)}
    
    def test_logic_contradiction(self) -> Dict[str, Any]:
        """
        Test Scenario 3: Logic Contradiction
        
        Agent B asserts MinAge 16, implying NotFamilyFriendly; 
        conflicts with FamilyFriendly from Playground amenity.
        Expected: reject; unsat cause recorded; agents collaborate to retract or clarify; 
        next pass succeeds.
        """
        logger.info("Running Logic Contradiction test scenario")
        
        try:
            # Create contradictory data
            test_graph = Graph()
            test_graph.bind("tourism", TOURISM)
            
            # Attraction with playground (should be family-friendly)
            aquarium = TOURISM.Attraction_DubaiAquarium
            test_graph.add((aquarium, RDF.type, TOURISM.Attraction))
            test_graph.add((aquarium, TOURISM.hasName, Literal("Dubai Aquarium")))
            test_graph.add((aquarium, TOURISM.hasAmenity, Literal("Playground")))  # Family-friendly
            test_graph.add((aquarium, TOURISM.hasMinAge, Literal(16)))  # Not family-friendly!
            
            # Run reasoning to detect contradiction
            reasoning_result = self.reasoning_engine.run_reasoning(test_graph)
            
            # Check for contradictions
            contradictions = reasoning_result["contradictions"]
            
            # Should detect contradiction between FamilyFriendly and NotFamilyFriendly
            has_contradiction = len(contradictions) > 0
            
            # Validate consistency
            consistency_result = self.reasoning_engine.validate_consistency(test_graph)
            
            result = {
                "success": has_contradiction,
                "contradictions_found": len(contradictions),
                "contradiction_details": contradictions,
                "is_consistent": consistency_result["is_consistent"],
                "consistency_issues": len(consistency_result["consistency_issues"])
            }
            
            logger.info(f"Logic Contradiction test result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Logic Contradiction test failed: {e}")
            return {"success": False, "error": str(e)}
    
    def test_rescission(self) -> Dict[str, Any]:
        """
        Test Scenario 4: Rescission
        
        After a composite is materialized, introduce a fact that violates its prerequisite.
        Expected: composite marked invalid or retracted; alert explains the dependent relationship.
        """
        logger.info("Running Rescission test scenario")
        
        try:
            # First, create valid composite destination
            initial_graph = Graph()
            initial_graph.bind("tourism", TOURISM)
            
            # Coastal city
            dubai = TOURISM.City_Dubai
            initial_graph.add((dubai, RDF.type, TOURISM.City))
            initial_graph.add((dubai, TOURISM.isCoastal, Literal(True)))
            
            # Family-friendly attraction with high rating
            aquarium = TOURISM.Attraction_DubaiAquarium
            initial_graph.add((aquarium, RDF.type, TOURISM.Attraction))
            initial_graph.add((aquarium, TOURISM.locatedIn, dubai))
            initial_graph.add((aquarium, TOURISM.hasAmenity, Literal("Playground")))
            initial_graph.add((aquarium, TOURISM.hasRating, Literal(4.6)))
            
            # Run reasoning to create composite
            initial_result = self.reasoning_engine.run_reasoning(initial_graph)
            initial_composites = [f for f in initial_result["derived_facts"] 
                                if f[1] == RDF.type and str(f[2]) == str(TOURISM.CoastalFamilyDestination)]
            
            # Now introduce violating fact (age restriction)
            modified_graph = initial_graph.copy()
            modified_graph.add((aquarium, TOURISM.hasMinAge, Literal(16)))  # Violates family-friendly
            
            # Run reasoning again
            modified_result = self.reasoning_engine.run_reasoning(modified_graph)
            
            # Check for contradictions
            contradictions = modified_result["contradictions"]
            
            # Should detect that the composite is no longer valid
            has_rescission = len(contradictions) > 0 or not modified_result["reached_fixpoint"]
            
            result = {
                "success": has_rescission,
                "initial_composites": len(initial_composites),
                "contradictions_after_modification": len(contradictions),
                "reasoning_reached_fixpoint": modified_result["reached_fixpoint"],
                "rescission_detected": has_rescission
            }
            
            logger.info(f"Rescission test result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Rescission test failed: {e}")
            return {"success": False, "error": str(e)}
    
    def test_cross_graph_consistency(self) -> Dict[str, Any]:
        """
        Test Scenario 5: Cross-graph Consistency
        
        Attempt to assert in Consensus a fact that contradicts Main.
        Expected: reject or require explicit RETRACT workflow; audit trail preserved.
        """
        logger.info("Running Cross-graph Consistency test scenario")
        
        try:
            # Create main graph with established fact
            main_graph = Graph()
            main_graph.bind("tourism", TOURISM)
            
            dubai = TOURISM.City_Dubai
            main_graph.add((dubai, RDF.type, TOURISM.City))
            main_graph.add((dubai, TOURISM.isCoastal, Literal(True)))  # Established fact
            
            # Create consensus graph with contradictory fact
            consensus_graph = Graph()
            consensus_graph.bind("tourism", TOURISM)
            
            # Same city, different coastal status
            consensus_graph.add((dubai, RDF.type, TOURISM.City))
            consensus_graph.add((dubai, TOURISM.isCoastal, Literal(False)))  # Contradicts main!
            
            # Merge graphs to simulate cross-graph validation
            merged_graph = main_graph + consensus_graph
            
            # Check for contradictions
            reasoning_result = self.reasoning_engine.run_reasoning(merged_graph)
            contradictions = reasoning_result["contradictions"]
            
            # Validate consistency
            consistency_result = self.reasoning_engine.validate_consistency(merged_graph)
            
            # Should detect cross-graph contradiction
            has_cross_graph_contradiction = (
                len(contradictions) > 0 or 
                not consistency_result["is_consistent"] or
                len(consistency_result["consistency_issues"]) > 0
            )
            
            result = {
                "success": has_cross_graph_contradiction,
                "contradictions": len(contradictions),
                "is_consistent": consistency_result["is_consistent"],
                "consistency_issues": len(consistency_result["consistency_issues"]),
                "cross_graph_contradiction_detected": has_cross_graph_contradiction
            }
            
            logger.info(f"Cross-graph Consistency test result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Cross-graph Consistency test failed: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate a comprehensive test report."""
        if not self.test_results:
            return {"error": "No test results available"}
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() 
                              if result.get("success", False))
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": (successful_tests / total_tests) * 100 if total_tests > 0 else 0
            },
            "test_results": self.test_results,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        for test_name, result in self.test_results.items():
            if not result.get("success", False):
                if test_name == "happy_path":
                    recommendations.append("Review ontology and reasoning rules for happy path scenario")
                elif test_name == "shape_rejection":
                    recommendations.append("Verify SHACL shapes are properly configured")
                elif test_name == "logic_contradiction":
                    recommendations.append("Check contradiction detection logic")
                elif test_name == "rescission":
                    recommendations.append("Improve rescission detection mechanisms")
                elif test_name == "cross_graph_consistency":
                    recommendations.append("Enhance cross-graph consistency checking")
        
        return recommendations


if __name__ == "__main__":
    # Run test scenarios
    logging.basicConfig(level=logging.INFO)
    
    test_scenarios = TestScenarios()
    results = test_scenarios.run_all_scenarios()
    
    # Generate and print report
    report = test_scenarios.generate_test_report()
    print("\n" + "="*50)
    print("POC TEST SCENARIOS REPORT")
    print("="*50)
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Successful: {report['summary']['successful_tests']}")
    print(f"Failed: {report['summary']['failed_tests']}")
    print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
    print("\nDetailed Results:")
    for test_name, result in report['test_results'].items():
        status = "PASS" if result.get('success', False) else "FAIL"
        print(f"  {test_name}: {status}")
    
    if report['recommendations']:
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  - {rec}")
