"""
Collect Agent for the multi-agent collaboration system.

This agent is responsible for collecting additional information about
tourism entities and enriching the knowledge graph.
"""

import logging
from typing import Dict, List, Any, Optional
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD

from .base_agent import BaseAgent

# Define namespaces
TOURISM = Namespace("http://example.org/tourism#")

logger = logging.getLogger(__name__)

class CollectAgent(BaseAgent):
    """Agent responsible for collecting and enriching tourism data."""
    
    def __init__(self, agent_id: str = "agent_collect", gateway_url: str = "http://localhost:8000"):
        """Initialize the collect agent."""
        super().__init__(agent_id, gateway_url)
        self.collection_tasks = []
        self.enriched_data = []
        
        logger.info(f"Initialized Collect Agent: {agent_id}")
    
    def add_collection_task(self, task_type: str, target_entity: str, task_data: Dict[str, Any]):
        """
        Add a collection task.
        
        Args:
            task_type: Type of collection task
            target_entity: Entity to collect data for
            task_data: Task-specific data
        """
        self.collection_tasks.append({
            "type": task_type,
            "target": target_entity,
            "data": task_data,
            "timestamp": self.session_id
        })
        
        logger.info(f"Added collection task: {task_type} for {target_entity}")
    
    def enrich_attraction_rating(self, attraction_uri: str, new_rating: float) -> Graph:
        """
        Enrich an attraction with a new rating.
        
        Args:
            attraction_uri: URI of the attraction
            new_rating: New rating value
            
        Returns:
            RDF graph with rating information
        """
        graph = Graph()
        graph.bind("tourism", TOURISM)
        
        attraction_ref = URIRef(attraction_uri)
        
        # Add rating if within valid range
        if 0 <= new_rating <= 5:
            graph.add((attraction_ref, TOURISM.hasRating, Literal(new_rating)))
            logger.info(f"Added rating {new_rating} for attraction {attraction_uri}")
        else:
            logger.warning(f"Invalid rating {new_rating} for attraction {attraction_uri}")
        
        return graph
    
    def enrich_attraction_amenities(self, attraction_uri: str, amenities: List[str]) -> Graph:
        """
        Enrich an attraction with amenities.
        
        Args:
            attraction_uri: URI of the attraction
            amenities: List of amenities
            
        Returns:
            RDF graph with amenity information
        """
        graph = Graph()
        graph.bind("tourism", TOURISM)
        
        attraction_ref = URIRef(attraction_uri)
        
        # Add amenities
        for amenity in amenities:
            graph.add((attraction_ref, TOURISM.hasAmenity, Literal(amenity)))
            logger.info(f"Added amenity {amenity} for attraction {attraction_uri}")
        
        return graph
    
    def enrich_attraction_age_restriction(self, attraction_uri: str, min_age: int) -> Graph:
        """
        Enrich an attraction with age restriction.
        
        Args:
            attraction_uri: URI of the attraction
            min_age: Minimum age requirement
            
        Returns:
            RDF graph with age restriction
        """
        graph = Graph()
        graph.bind("tourism", TOURISM)
        
        attraction_ref = URIRef(attraction_uri)
        
        # Add minimum age
        if min_age >= 0:
            graph.add((attraction_ref, TOURISM.hasMinAge, Literal(min_age)))
            logger.info(f"Added min age {min_age} for attraction {attraction_uri}")
        else:
            logger.warning(f"Invalid min age {min_age} for attraction {attraction_uri}")
        
        return graph
    
    def enrich_city_coastal_status(self, city_uri: str, is_coastal: bool) -> Graph:
        """
        Enrich a city with coastal status.
        
        Args:
            city_uri: URI of the city
            is_coastal: Whether the city is coastal
            
        Returns:
            RDF graph with coastal status
        """
        graph = Graph()
        graph.bind("tourism", TOURISM)
        
        city_ref = URIRef(city_uri)
        
        # Add coastal status
        graph.add((city_ref, TOURISM.isCoastal, Literal(is_coastal)))
        logger.info(f"Added coastal status {is_coastal} for city {city_uri}")
        
        return graph
    
    def process_collection_tasks(self) -> List[Graph]:
        """
        Process all collection tasks and create enrichment data.
        
        Returns:
            List of enrichment RDF graphs
        """
        enrichment_graphs = []
        
        for task in self.collection_tasks:
            try:
                if task["type"] == "rating_enrichment":
                    graph = self.enrich_attraction_rating(
                        task["target"],
                        task["data"]["rating"]
                    )
                    enrichment_graphs.append(graph)
                    
                elif task["type"] == "amenity_enrichment":
                    graph = self.enrich_attraction_amenities(
                        task["target"],
                        task["data"]["amenities"]
                    )
                    enrichment_graphs.append(graph)
                    
                elif task["type"] == "age_restriction":
                    graph = self.enrich_attraction_age_restriction(
                        task["target"],
                        task["data"]["min_age"]
                    )
                    enrichment_graphs.append(graph)
                    
                elif task["type"] == "coastal_status":
                    graph = self.enrich_city_coastal_status(
                        task["target"],
                        task["data"]["is_coastal"]
                    )
                    enrichment_graphs.append(graph)
                    
                else:
                    logger.warning(f"Unknown task type: {task['type']}")
                    
            except Exception as e:
                logger.error(f"Error processing collection task: {e}")
                continue
        
        self.enriched_data = enrichment_graphs
        logger.info(f"Processed {len(enrichment_graphs)} collection tasks")
        
        return enrichment_graphs
    
    def collect_sample_enrichments(self):
        """Collect sample enrichment data for testing."""
        logger.info("Collecting sample enrichment data")
        
        # Add rating enrichment for Dubai Aquarium
        self.add_collection_task(
            "rating_enrichment",
            "http://example.org/tourism#Attraction_dubai_aquarium",
            {"rating": 4.8}
        )
        
        # Add amenity enrichment
        self.add_collection_task(
            "amenity_enrichment",
            "http://example.org/tourism#Attraction_dubai_aquarium",
            {"amenities": ["Wifi", "Accessible"]}
        )
        
        # Add age restriction (this might cause contradiction)
        self.add_collection_task(
            "age_restriction",
            "http://example.org/tourism#Attraction_dubai_aquarium",
            {"min_age": 16}  # This should cause a contradiction with Playground amenity
        )
        
        # Process and commit enrichments
        enrichment_graphs = self.process_collection_tasks()
        
        for graph in enrichment_graphs:
            success = self.validate_and_commit(graph)
            if success:
                self.log_activity("data_enriched", {
                    "graph_size": len(graph),
                    "triples": list(graph)
                })
    
    def validate_and_commit(self, graph: Graph) -> bool:
        """
        Validate and commit an enrichment graph.
        
        Args:
            graph: RDF graph to validate and commit
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Serialize graph to Turtle
            rdf_data = graph.serialize(format="turtle")
            
            # Validate through gateway
            validation_result = self.validate_data(rdf_data)
            
            if not validation_result.get("success", False):
                logger.error(f"Validation failed: {validation_result}")
                return False
            
            # Send to staging
            staging_result = self.send_staging_write(rdf_data)
            
            if not staging_result.get("success", False):
                logger.error(f"Staging write failed: {staging_result}")
                return False
            
            # Commit to consensus
            commit_result = self.commit_data()
            
            if not commit_result.get("success", False):
                logger.error(f"Commit failed: {commit_result}")
                return False
            
            logger.info("Successfully validated and committed enrichment data")
            return True
            
        except Exception as e:
            logger.error(f"Error in validate_and_commit: {e}")
            return False
    
    def monitor_derived_facts(self):
        """Monitor for new derived facts from reasoning."""
        derived_facts = self.get_derived_facts()
        
        if derived_facts:
            logger.info(f"Found {len(derived_facts)} derived facts")
            
            # Analyze derived facts
            for fact in derived_facts:
                subject = fact.get("s", {}).get("value", "")
                predicate = fact.get("p", {}).get("value", "")
                object_val = fact.get("o", {}).get("value", "")
                
                if "CoastalAttraction" in object_val:
                    self.log_activity("coastal_attraction_derived", {
                        "attraction": subject,
                        "reason": "Located in coastal city"
                    })
                
                elif "FamilyFriendlyAttraction" in object_val:
                    self.log_activity("family_friendly_derived", {
                        "attraction": subject,
                        "reason": "Has playground amenity"
                    })
                
                elif "NotFamilyFriendlyAttraction" in object_val:
                    self.log_activity("not_family_friendly_derived", {
                        "attraction": subject,
                        "reason": "Has age restriction > 12"
                    })
                
                elif "CoastalFamilyDestination" in object_val:
                    self.log_activity("composite_destination_derived", {
                        "destination": subject,
                        "reason": "Coastal city + family-friendly attraction + high rating"
                    })
    
    def run(self):
        """Main execution loop for the collect agent."""
        logger.info("Starting Collect Agent execution")
        
        try:
            # Collect sample enrichments
            self.collect_sample_enrichments()
            
            # Monitor for derived facts
            self.monitor_derived_facts()
            
            # Check for contradictions
            consensus_facts = self.get_consensus_facts()
            if consensus_facts:
                logger.info(f"Found {len(consensus_facts)} consensus facts")
                self.log_activity("consensus_facts_retrieved", {
                    "count": len(consensus_facts)
                })
            
            logger.info("Collect Agent execution completed")
            
        except Exception as e:
            logger.error(f"Error in Collect Agent execution: {e}")
            self.log_activity("execution_error", {"error": str(e)})


if __name__ == "__main__":
    # Test the collect agent
    import time
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create and run the agent
    agent = CollectAgent()
    
    # Wait a moment for the gateway to be ready
    time.sleep(2)
    
    # Run the agent
    agent.run()
