"""
Base Agent class for multi-agent collaboration system.

This module provides the base functionality that all agents inherit from.
"""

import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL

# Define namespaces
TOURISM = Namespace("http://example.org/tourism#")
MSG = Namespace("http://example.org/messages#")

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base class for all agents in the collaboration system."""
    
    def __init__(self, agent_id: str, gateway_url: str = "http://localhost:8000"):
        """
        Initialize the base agent.
        
        Args:
            agent_id: Unique identifier for this agent
            gateway_url: URL of the validator gateway
        """
        self.agent_id = agent_id
        self.gateway_url = gateway_url
        self.session_id = f"session_{agent_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        self.staging_graph = f"http://example.org/staging/{agent_id}"
        
        # Agent's local knowledge graph
        self.local_graph = Graph()
        self.local_graph.bind("tourism", TOURISM)
        self.local_graph.bind("msg", MSG)
        
        logger.info(f"Initialized agent: {agent_id}")
    
    def send_staging_write(self, rdf_data: str, operation: str = "add") -> Dict[str, Any]:
        """
        Send data to staging graph via the gateway.
        
        Args:
            rdf_data: RDF data in Turtle format
            operation: Operation type ('add' or 'remove')
            
        Returns:
            Response from the gateway
        """
        try:
            url = f"{self.gateway_url}/staging/write"
            payload = {
                "agent_id": self.agent_id,
                "session_id": self.session_id,
                "staging_graph": self.staging_graph,
                "rdf_data": rdf_data,
                "operation": operation
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Staging write result: {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Staging write failed: {e}")
            return {"success": False, "error": str(e)}
    
    def validate_data(self, rdf_data: str) -> Dict[str, Any]:
        """
        Validate data through the gateway.
        
        Args:
            rdf_data: RDF data to validate
            
        Returns:
            Validation result
        """
        try:
            url = f"{self.gateway_url}/validate"
            payload = {
                "agent_id": self.agent_id,
                "session_id": self.session_id,
                "target_graph": self.staging_graph,
                "rdf_payload": rdf_data,
                "operation": "add",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Validation result: {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Validation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def commit_data(self) -> Dict[str, Any]:
        """
        Commit staged data to consensus graph.
        
        Returns:
            Commit result
        """
        try:
            url = f"{self.gateway_url}/commit"
            payload = {
                "agent_id": self.agent_id,
                "session_id": self.session_id,
                "staging_graph": self.staging_graph
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Commit result: {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Commit failed: {e}")
            return {"success": False, "error": str(e)}
    
    def query_knowledge_graph(self, sparql_query: str, graph_uri: str = None) -> Dict[str, Any]:
        """
        Query the knowledge graph.
        
        Args:
            sparql_query: SPARQL query string
            graph_uri: Optional graph URI to query
            
        Returns:
            Query results
        """
        try:
            url = f"{self.gateway_url}/query"
            payload = {
                "query": sparql_query,
                "graph_uri": graph_uri,
                "format": "json"
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Query result: {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Query failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_consensus_facts(self) -> List[Dict[str, Any]]:
        """
        Get facts from the consensus graph.
        
        Returns:
            List of consensus facts
        """
        query = """
        SELECT ?s ?p ?o
        WHERE {
            GRAPH <http://example.org/consensus> {
                ?s ?p ?o
            }
        }
        """
        
        result = self.query_knowledge_graph(query)
        if result.get("success"):
            return result.get("results", {}).get("bindings", [])
        return []
    
    def get_derived_facts(self) -> List[Dict[str, Any]]:
        """
        Get derived facts from reasoning.
        
        Returns:
            List of derived facts
        """
        query = """
        SELECT ?s ?p ?o
        WHERE {
            GRAPH <http://example.org/consensus> {
                ?s ?p ?o .
                ?s rdf:type ?type .
                FILTER(?type IN (tourism:CoastalAttraction, tourism:FamilyFriendlyAttraction, 
                               tourism:NotFamilyFriendlyAttraction, tourism:CoastalFamilyDestination))
            }
        }
        """
        
        result = self.query_knowledge_graph(query)
        if result.get("success"):
            return result.get("results", {}).get("bindings", [])
        return []
    
    def create_message(self, intent: str, about: str, payload: Graph = None) -> str:
        """
        Create an inter-agent message.
        
        Args:
            intent: Intent description
            about: Subject of the message
            payload: Optional RDF payload
            
        Returns:
            Message in RDF format
        """
        message_graph = Graph()
        message_graph.bind("msg", MSG)
        message_graph.bind("tourism", TOURISM)
        
        message_id = MSG[f"message_{self.agent_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"]
        
        message_graph.add((message_id, RDF.type, MSG.Intent))
        message_graph.add((message_id, MSG.fromAgent, Literal(self.agent_id)))
        message_graph.add((message_id, MSG.timestamp, Literal(datetime.utcnow().isoformat())))
        message_graph.add((message_id, MSG.about, URIRef(about)))
        
        if payload:
            message_graph.add((message_id, MSG.payloadGraph, payload))
        
        return message_graph.serialize(format="turtle")
    
    def add_to_local_graph(self, subject: URIRef, predicate: URIRef, object: Any):
        """Add a triple to the local graph."""
        self.local_graph.add((subject, predicate, object))
        logger.debug(f"Added to local graph: {subject} {predicate} {object}")
    
    def get_local_graph_turtle(self) -> str:
        """Get the local graph serialized as Turtle."""
        return self.local_graph.serialize(format="turtle")
    
    def clear_local_graph(self):
        """Clear the local graph."""
        self.local_graph = Graph()
        self.local_graph.bind("tourism", TOURISM)
        self.local_graph.bind("msg", MSG)
        logger.info("Cleared local graph")
    
    def log_activity(self, activity: str, details: Dict[str, Any] = None):
        """Log agent activity."""
        log_data = {
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "activity": activity,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if details:
            log_data.update(details)
        
        logger.info(f"Agent activity: {log_data}")
    
    def run(self):
        """
        Main agent execution loop.
        
        This method should be overridden by specific agent implementations.
        """
        raise NotImplementedError("Subclasses must implement the run method")
