"""
Reason Agent for the multi-agent collaboration system.

This agent is responsible for higher-level reasoning and analysis
of the tourism knowledge graph, including composite entity detection.
"""

import logging
from typing import Dict, List, Any, Optional
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD

from .base_agent import BaseAgent

# Define namespaces
TOURISM = Namespace("http://example.org/tourism#")

logger = logging.getLogger(__name__)

class ReasonAgent(BaseAgent):
    """Agent responsible for higher-level reasoning and analysis."""
    
    def __init__(self, agent_id: str = "agent_reason", gateway_url: str = "http://localhost:8000"):
        """Initialize the reason agent."""
        super().__init__(agent_id, gateway_url)
        self.reasoning_tasks = []
        self.analysis_results = []
        
        logger.info(f"Initialized Reason Agent: {agent_id}")
    
    def add_reasoning_task(self, task_type: str, task_data: Dict[str, Any]):
        """
        Add a reasoning task.
        
        Args:
            task_type: Type of reasoning task
            task_data: Task-specific data
        """
        self.reasoning_tasks.append({
            "type": task_type,
            "data": task_data,
            "timestamp": self.session_id
        })
        
        logger.info(f"Added reasoning task: {task_type}")
    
    def analyze_composite_destinations(self) -> List[Dict[str, Any]]:
        """
        Analyze the knowledge graph for composite destinations.
        
        Returns:
            List of composite destination analysis results
        """
        # Query for potential composite destinations
        query = """
        SELECT ?city ?attraction ?cityCoastal ?attractionFamilyFriendly ?rating
        WHERE {
            ?city rdf:type tourism:City .
            ?attraction rdf:type tourism:Attraction .
            ?attraction tourism:locatedIn ?city .
            ?city tourism:isCoastal ?cityCoastal .
            ?attraction tourism:hasRating ?rating .
            OPTIONAL {
                ?attraction rdf:type tourism:FamilyFriendlyAttraction .
                BIND(true as ?attractionFamilyFriendly)
            }
        }
        """
        
        result = self.query_knowledge_graph(query)
        composite_candidates = []
        
        if result.get("success"):
            bindings = result.get("results", {}).get("bindings", [])
            
            for binding in bindings:
                city = binding.get("city", {}).get("value", "")
                attraction = binding.get("attraction", {}).get("value", "")
                is_coastal = binding.get("cityCoastal", {}).get("value", "false") == "true"
                is_family_friendly = binding.get("attractionFamilyFriendly", {}).get("value", "false") == "true"
                rating = float(binding.get("rating", {}).get("value", "0"))
                
                if is_coastal and is_family_friendly and rating >= 4.5:
                    composite_candidates.append({
                        "city": city,
                        "attraction": attraction,
                        "rating": rating,
                        "reason": "Coastal city + family-friendly attraction + high rating"
                    })
        
        logger.info(f"Found {len(composite_candidates)} composite destination candidates")
        return composite_candidates
    
    def detect_contradictions(self) -> List[Dict[str, Any]]:
        """
        Detect logical contradictions using SWRL rule resolution only.
        
        Returns:
            List of contradiction analysis results
        """
        try:
            # Use the reasoning engine to detect contradictions via SWRL rules
            from ..ontology.reasoning_rules import TourismReasoningEngine
            from ..ontology.fuseki_client import FusekiClient
            
            # Initialize reasoning engine
            fuseki_client = FusekiClient()
            reasoning_engine = TourismReasoningEngine(fuseki_client)
            
            # Get current knowledge graph
            kg_data = self.get_knowledge_graph()
            if not kg_data.get("success"):
                logger.error("Failed to retrieve knowledge graph for contradiction detection")
                return []
            
            # Convert to RDF graph for reasoning
            from rdflib import Graph
            graph = Graph()
            
            for triple in kg_data.get("triples", []):
                try:
                    graph.add(triple)
                except Exception as e:
                    logger.warning(f"Failed to add triple to graph: {e}")
                    continue
            
            # Run SWRL reasoning to detect contradictions
            reasoning_result = reasoning_engine.run_reasoning(graph)
            contradictions = reasoning_result.get("contradictions", [])
            
            # Convert to expected format
            formatted_contradictions = []
            for contradiction in contradictions:
                formatted_contradictions.append({
                    "entity": contradiction.get("entity", "unknown"),
                    "contradicting_types": contradiction.get("conflicting_types", []),
                    "reason": contradiction.get("message", "SWRL rule detected contradiction"),
                    "type": contradiction.get("type", "SWRL_CONTRADICTION")
                })
            
            logger.info(f"Found {len(formatted_contradictions)} contradictions via SWRL rules")
            return formatted_contradictions
            
        except Exception as e:
            logger.error(f"Error in SWRL contradiction detection: {e}")
            return []
    
    
    def analyze_derived_facts(self) -> Dict[str, Any]:
        """
        Analyze derived facts from reasoning.
        
        Returns:
            Analysis of derived facts
        """
        derived_facts = self.get_derived_facts()
        
        analysis = {
            "total_derived_facts": len(derived_facts),
            "fact_types": {},
            "reasoning_patterns": []
        }
        
        for fact in derived_facts:
            predicate = fact.get("p", {}).get("value", "")
            object_val = fact.get("o", {}).get("value", "")
            
            if "rdf:type" in predicate:
                fact_type = object_val.split("#")[-1] if "#" in object_val else object_val
                analysis["fact_types"][fact_type] = analysis["fact_types"].get(fact_type, 0) + 1
        
        # Identify reasoning patterns
        if "CoastalAttraction" in analysis["fact_types"]:
            analysis["reasoning_patterns"].append("Coastal attraction derivation")
        
        if "FamilyFriendlyAttraction" in analysis["fact_types"]:
            analysis["reasoning_patterns"].append("Family-friendly classification")
        
        if "NotFamilyFriendlyAttraction" in analysis["fact_types"]:
            analysis["reasoning_patterns"].append("Age restriction classification")
        
        if "CoastalFamilyDestination" in analysis["fact_types"]:
            analysis["reasoning_patterns"].append("Composite destination materialization")
        
        logger.info(f"Derived facts analysis: {analysis}")
        return analysis
    
    def suggest_data_improvements(self) -> List[Dict[str, Any]]:
        """
        Suggest improvements to the knowledge graph.
        
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        # Check for missing ratings
        query = """
        SELECT ?attraction
        WHERE {
            ?attraction rdf:type tourism:Attraction .
            FILTER NOT EXISTS { ?attraction tourism:hasRating ?rating }
        }
        """
        
        result = self.query_knowledge_graph(query)
        
        if result.get("success"):
            bindings = result.get("results", {}).get("bindings", [])
            
            for binding in bindings:
                attraction = binding.get("attraction", {}).get("value", "")
                suggestions.append({
                    "type": "missing_rating",
                    "entity": attraction,
                    "suggestion": "Add rating information for better classification"
                })
        
        # Check for missing amenities
        query = """
        SELECT ?attraction
        WHERE {
            ?attraction rdf:type tourism:Attraction .
            FILTER NOT EXISTS { ?attraction tourism:hasAmenity ?amenity }
        }
        """
        
        result = self.query_knowledge_graph(query)
        
        if result.get("success"):
            bindings = result.get("results", {}).get("bindings", [])
            
            for binding in bindings:
                attraction = binding.get("attraction", {}).get("value", "")
                suggestions.append({
                    "type": "missing_amenities",
                    "entity": attraction,
                    "suggestion": "Add amenity information for family-friendly classification"
                })
        
        logger.info(f"Generated {len(suggestions)} improvement suggestions")
        return suggestions
    
    def process_reasoning_tasks(self) -> List[Dict[str, Any]]:
        """
        Process all reasoning tasks.
        
        Returns:
            List of reasoning results
        """
        results = []
        
        for task in self.reasoning_tasks:
            try:
                if task["type"] == "composite_analysis":
                    result = self.analyze_composite_destinations()
                    results.extend(result)
                    
                elif task["type"] == "contradiction_detection":
                    result = self.detect_contradictions()
                    results.extend(result)
                    
                elif task["type"] == "derived_facts_analysis":
                    result = self.analyze_derived_facts()
                    results.append(result)
                    
                elif task["type"] == "improvement_suggestions":
                    result = self.suggest_data_improvements()
                    results.extend(result)
                    
                else:
                    logger.warning(f"Unknown reasoning task type: {task['type']}")
                    
            except Exception as e:
                logger.error(f"Error processing reasoning task: {e}")
                continue
        
        self.analysis_results = results
        logger.info(f"Processed {len(results)} reasoning tasks")
        
        return results
    
    def run(self):
        """Main execution loop for the reason agent."""
        logger.info("Starting Reason Agent execution")
        
        try:
            # Add reasoning tasks
            self.add_reasoning_task("composite_analysis", {})
            self.add_reasoning_task("contradiction_detection", {})
            self.add_reasoning_task("derived_facts_analysis", {})
            self.add_reasoning_task("improvement_suggestions", {})
            
            # Process reasoning tasks
            results = self.process_reasoning_tasks()
            
            # Log analysis results
            for result in results:
                if isinstance(result, dict):
                    self.log_activity("reasoning_analysis", result)
                elif isinstance(result, list):
                    for item in result:
                        self.log_activity("reasoning_result", item)
            
            # Monitor for new derived facts
            derived_facts = self.get_derived_facts()
            if derived_facts:
                logger.info(f"Found {len(derived_facts)} derived facts")
                self.log_activity("derived_facts_monitored", {
                    "count": len(derived_facts),
                    "facts": derived_facts
                })
            
            # Check consensus facts
            consensus_facts = self.get_consensus_facts()
            if consensus_facts:
                logger.info(f"Found {len(consensus_facts)} consensus facts")
                self.log_activity("consensus_analysis", {
                    "count": len(consensus_facts)
                })
            
            logger.info("Reason Agent execution completed")
            
        except Exception as e:
            logger.error(f"Error in Reason Agent execution: {e}")
            self.log_activity("execution_error", {"error": str(e)})


if __name__ == "__main__":
    # Test the reason agent
    import time
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create and run the agent
    agent = ReasonAgent()
    
    # Wait a moment for the gateway to be ready
    time.sleep(2)
    
    # Run the agent
    agent.run()
