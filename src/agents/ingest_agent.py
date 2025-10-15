"""
Ingest Agent for the multi-agent collaboration system.

This agent is responsible for ingesting and normalizing tourism data
from various sources and converting it to RDF format.
"""

import logging
from typing import Dict, List, Any, Optional
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD

from .base_agent import BaseAgent

# Define namespaces
TOURISM = Namespace("http://example.org/tourism#")

logger = logging.getLogger(__name__)

class IngestAgent(BaseAgent):
    """Agent responsible for ingesting and normalizing tourism data."""
    
    def __init__(self, agent_id: str = "agent_ingest", gateway_url: str = "http://localhost:8000"):
        """Initialize the ingest agent."""
        super().__init__(agent_id, gateway_url)
        self.data_sources = []
        self.normalized_data = []
        
        logger.info(f"Initialized Ingest Agent: {agent_id}")
    
    def add_data_source(self, source_type: str, source_data: Dict[str, Any]):
        """
        Add a data source for ingestion.
        
        Args:
            source_type: Type of data source (e.g., 'city', 'attraction')
            source_data: Raw data from the source
        """
        self.data_sources.append({
            "type": source_type,
            "data": source_data,
            "timestamp": self.session_id
        })
        
        logger.info(f"Added data source: {source_type}")
    
    def normalize_city_data(self, city_data: Dict[str, Any]) -> Graph:
        """
        Normalize city data to RDF.
        
        Args:
            city_data: Raw city data
            
        Returns:
            Normalized RDF graph
        """
        graph = Graph()
        graph.bind("tourism", TOURISM)
        
        city_id = city_data.get("id", "unknown")
        city_uri = TOURISM[f"City_{city_id}"]
        
        # Add city type
        if city_data.get("is_coastal", False):
            graph.add((city_uri, RDF.type, TOURISM.CoastalCity))
        else:
            graph.add((city_uri, RDF.type, TOURISM.City))
        
        # Add city properties
        if "name" in city_data:
            graph.add((city_uri, TOURISM.hasName, Literal(city_data["name"])))
        
        if "country" in city_data:
            country_uri = TOURISM[f"Country_{city_data['country']}"]
            graph.add((country_uri, RDF.type, TOURISM.Country))
            graph.add((country_uri, TOURISM.hasName, Literal(city_data["country"])))
            graph.add((city_uri, TOURISM.inCountry, country_uri))
        
        if "is_coastal" in city_data:
            graph.add((city_uri, TOURISM.isCoastal, Literal(city_data["is_coastal"])))
        
        return graph
    
    def normalize_attraction_data(self, attraction_data: Dict[str, Any]) -> Graph:
        """
        Normalize attraction data to RDF.
        
        Args:
            attraction_data: Raw attraction data
            
        Returns:
            Normalized RDF graph
        """
        graph = Graph()
        graph.bind("tourism", TOURISM)
        
        attraction_id = attraction_data.get("id", "unknown")
        attraction_uri = TOURISM[f"Attraction_{attraction_id}"]
        
        # Add attraction type
        graph.add((attraction_uri, RDF.type, TOURISM.Attraction))
        
        # Add attraction properties
        if "name" in attraction_data:
            graph.add((attraction_uri, TOURISM.hasName, Literal(attraction_data["name"])))
        
        if "city" in attraction_data:
            city_uri = TOURISM[f"City_{attraction_data['city']}"]
            graph.add((attraction_uri, TOURISM.locatedIn, city_uri))
        
        if "rating" in attraction_data:
            rating = float(attraction_data["rating"])
            if 0 <= rating <= 5:
                graph.add((attraction_uri, TOURISM.hasRating, Literal(rating)))
        
        if "entry_fee" in attraction_data:
            fee_data = attraction_data["entry_fee"]
            if "amount" in fee_data:
                graph.add((attraction_uri, TOURISM.hasEntryFeeAmount, Literal(float(fee_data["amount"]))))
            if "currency" in fee_data:
                graph.add((attraction_uri, TOURISM.hasEntryFeeCurrency, Literal(fee_data["currency"])))
        
        if "min_age" in attraction_data:
            graph.add((attraction_uri, TOURISM.hasMinAge, Literal(int(attraction_data["min_age"]))))
        
        if "amenities" in attraction_data:
            for amenity in attraction_data["amenities"]:
                graph.add((attraction_uri, TOURISM.hasAmenity, Literal(amenity)))
        
        return graph
    
    def process_data_sources(self) -> List[Graph]:
        """
        Process all data sources and normalize them.
        
        Returns:
            List of normalized RDF graphs
        """
        normalized_graphs = []
        
        for source in self.data_sources:
            try:
                if source["type"] == "city":
                    graph = self.normalize_city_data(source["data"])
                    normalized_graphs.append(graph)
                    
                elif source["type"] == "attraction":
                    graph = self.normalize_attraction_data(source["data"])
                    normalized_graphs.append(graph)
                    
                else:
                    logger.warning(f"Unknown source type: {source['type']}")
                    
            except Exception as e:
                logger.error(f"Error processing data source: {e}")
                continue
        
        self.normalized_data = normalized_graphs
        logger.info(f"Processed {len(normalized_graphs)} data sources")
        
        return normalized_graphs
    
    def validate_and_commit(self, graph: Graph) -> bool:
        """
        Validate and commit a normalized graph.
        
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
            
            logger.info("Successfully validated and committed data")
            return True
            
        except Exception as e:
            logger.error(f"Error in validate_and_commit: {e}")
            return False
    
    def ingest_sample_data(self):
        """Ingest sample tourism data for testing."""
        logger.info("Ingesting sample data")
        
        # Sample city data
        dubai_data = {
            "id": "dubai",
            "name": "Dubai",
            "country": "UAE",
            "is_coastal": True
        }
        self.add_data_source("city", dubai_data)
        
        # Sample attraction data
        aquarium_data = {
            "id": "dubai_aquarium",
            "name": "Dubai Aquarium",
            "city": "dubai",
            "rating": 4.6,
            "entry_fee": {
                "amount": 25.0,
                "currency": "AED"
            },
            "amenities": ["Playground", "Restaurant", "Parking"]
        }
        self.add_data_source("attraction", aquarium_data)
        
        # Process and commit data
        normalized_graphs = self.process_data_sources()
        
        for graph in normalized_graphs:
            success = self.validate_and_commit(graph)
            if success:
                self.log_activity("data_ingested", {
                    "graph_size": len(graph),
                    "triples": list(graph)
                })
    
    def run(self):
        """Main execution loop for the ingest agent."""
        logger.info("Starting Ingest Agent execution")
        
        try:
            # Ingest sample data
            self.ingest_sample_data()
            
            # Check for derived facts
            derived_facts = self.get_derived_facts()
            if derived_facts:
                logger.info(f"Found {len(derived_facts)} derived facts")
                self.log_activity("derived_facts_detected", {
                    "count": len(derived_facts),
                    "facts": derived_facts
                })
            
            # Check consensus facts
            consensus_facts = self.get_consensus_facts()
            if consensus_facts:
                logger.info(f"Found {len(consensus_facts)} consensus facts")
                self.log_activity("consensus_facts_retrieved", {
                    "count": len(consensus_facts)
                })
            
            logger.info("Ingest Agent execution completed")
            
        except Exception as e:
            logger.error(f"Error in Ingest Agent execution: {e}")
            self.log_activity("execution_error", {"error": str(e)})


if __name__ == "__main__":
    # Test the ingest agent
    import time
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create and run the agent
    agent = IngestAgent()
    
    # Wait a moment for the gateway to be ready
    time.sleep(2)
    
    # Run the agent
    agent.run()
