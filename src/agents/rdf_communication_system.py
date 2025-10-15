#!/usr/bin/env python3
"""
RDF Communication System for Multi-Agent Collaboration

This module implements a comprehensive RDF-based communication system where
all agent interactions happen through RDF graphs with clear level separation:
- Agent Staging Graphs (private agent workspaces)
- Consensus Graph (validated collaboration state)
- Main Graph (curated, production-ready facts)
- Communication RDF (agent-to-agent messages)
"""

import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL
from SPARQLWrapper import SPARQLWrapper, JSON

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define namespaces
TOURISM = Namespace("http://example.org/tourism#")
AGENT = Namespace("http://example.org/agents#")
COMM = Namespace("http://example.org/communication#")
SESSION = Namespace("http://example.org/sessions#")

class RDFCommunicationSystem:
    """RDF-based communication system for multi-agent collaboration."""
    
    def __init__(self, fuseki_endpoint: str = "http://localhost:3030/ds"):
        """
        Initialize the RDF communication system.
        
        Args:
            fuseki_endpoint: Fuseki SPARQL endpoint URL
        """
        self.fuseki_endpoint = fuseki_endpoint
        self.sparql = SPARQLWrapper(fuseki_endpoint)
        self.sparql.setReturnFormat(JSON)
        
        # Graph levels
        self.agent_staging_graphs = {}  # Private agent workspaces
        self.consensus_graph = "http://example.org/consensus"
        self.main_graph = "http://example.org/main"
        self.communication_graph = "http://example.org/communication"
        
        # Agent registry
        self.registered_agents = {}
        
        logger.info("RDF Communication System initialized")
    
    def register_agent(self, agent_id: str, agent_type: str, permissions: List[str]) -> bool:
        """
        Register an agent in the system.
        
        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent (ingest, collect, reason)
            permissions: List of permissions (read, write_staging, write_consensus)
        
        Returns:
            bool: True if registration successful
        """
        try:
            # Create agent staging graph
            staging_graph = f"http://example.org/staging/{agent_id}"
            self.agent_staging_graphs[agent_id] = staging_graph
            
            # Register agent metadata
            self.registered_agents[agent_id] = {
                "type": agent_type,
                "permissions": permissions,
                "staging_graph": staging_graph,
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"Agent {agent_id} registered with staging graph {staging_graph}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {e}")
            return False
    
    def create_communication_rdf(self, from_agent: str, to_agent: str, 
                               message_type: str, content: str, 
                               session_id: str) -> str:
        """
        Create RDF representation of agent communication.
        
        Args:
            from_agent: Source agent ID
            to_agent: Target agent ID
            message_type: Type of message (request, response, notification)
            content: Message content
            session_id: Session identifier
        
        Returns:
            str: RDF serialization of the communication
        """
        try:
            # Create communication graph
            comm_graph = Graph()
            comm_graph.bind("comm", COMM)
            comm_graph.bind("agent", AGENT)
            comm_graph.bind("session", SESSION)
            
            # Generate unique message ID
            message_id = f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            message_uri = COMM[message_id]
            
            # Create communication RDF
            comm_graph.add((message_uri, RDF.type, COMM.Message))
            comm_graph.add((message_uri, COMM.fromAgent, AGENT[from_agent]))
            comm_graph.add((message_uri, COMM.toAgent, AGENT[to_agent]))
            comm_graph.add((message_uri, COMM.messageType, Literal(message_type)))
            comm_graph.add((message_uri, COMM.content, Literal(content)))
            comm_graph.add((message_uri, COMM.sessionId, SESSION[session_id]))
            comm_graph.add((message_uri, COMM.timestamp, Literal(datetime.now().isoformat())))
            comm_graph.add((message_uri, COMM.status, Literal("sent")))
            
            # Serialize to RDF
            rdf_content = comm_graph.serialize(format="turtle")
            
            logger.info(f"Created communication RDF from {from_agent} to {to_agent}")
            return rdf_content
            
        except Exception as e:
            logger.error(f"Failed to create communication RDF: {e}")
            return ""
    
    def write_to_staging(self, agent_id: str, rdf_data: str, 
                        operation: str = "write") -> Dict[str, Any]:
        """
        Write RDF data to agent's staging graph.
        
        Args:
            agent_id: Agent identifier
            rdf_data: RDF data to write
            operation: Operation type (write, update, delete)
        
        Returns:
            Dict: Result of the operation
        """
        try:
            if agent_id not in self.registered_agents:
                return {"success": False, "error": "Agent not registered"}
            
            staging_graph = self.agent_staging_graphs[agent_id]
            
            # Create SPARQL UPDATE query
            update_query = f"""
            INSERT DATA {{
                GRAPH <{staging_graph}> {{
                    {rdf_data}
                }}
            }}
            """
            
            # Execute update
            self.sparql.setQuery(update_query)
            self.sparql.setMethod("POST")
            result = self.sparql.query()
            
            # Log the operation
            logger.info(f"Agent {agent_id} wrote to staging graph {staging_graph}")
            
            return {
                "success": True,
                "staging_graph": staging_graph,
                "operation": operation,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to write to staging for agent {agent_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def read_from_staging(self, agent_id: str, query: str) -> Dict[str, Any]:
        """
        Read RDF data from agent's staging graph.
        
        Args:
            agent_id: Agent identifier
            query: SPARQL query
        
        Returns:
            Dict: Query results
        """
        try:
            if agent_id not in self.registered_agents:
                return {"success": False, "error": "Agent not registered"}
            
            staging_graph = self.agent_staging_graphs[agent_id]
            
            # Modify query to target staging graph
            modified_query = f"""
            SELECT * WHERE {{
                GRAPH <{staging_graph}> {{
                    {query}
                }}
            }}
            """
            
            # Execute query
            self.sparql.setQuery(modified_query)
            self.sparql.setMethod("GET")
            result = self.sparql.query().convert()
            
            return {
                "success": True,
                "results": result,
                "staging_graph": staging_graph
            }
            
        except Exception as e:
            logger.error(f"Failed to read from staging for agent {agent_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def promote_to_consensus(self, agent_id: str, rdf_data: str, 
                           validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Promote validated RDF data from staging to consensus graph.
        
        Args:
            agent_id: Agent identifier
            rdf_data: Validated RDF data
            validation_result: Validation results
        
        Returns:
            Dict: Result of the promotion
        """
        try:
            if not validation_result.get("success", False):
                return {"success": False, "error": "Data not validated"}
            
            staging_graph = self.agent_staging_graphs[agent_id]
            
            # Create promotion RDF with provenance
            promotion_rdf = f"""
            @prefix prov: <http://www.w3.org/ns/prov#> .
            @prefix agent: <http://example.org/agents#> .
            @prefix session: <http://example.org/sessions#> .
            
            <{rdf_data}>
                prov:wasAttributedTo agent:{agent_id} ;
                prov:generatedAtTime "{datetime.now().isoformat()}" ;
                prov:wasGeneratedBy <http://example.org/validation> .
            """
            
            # Move data from staging to consensus
            move_query = f"""
            WITH <{staging_graph}>
            DELETE {{
                ?s ?p ?o .
            }}
            INSERT {{
                GRAPH <{self.consensus_graph}> {{
                    ?s ?p ?o .
                    {promotion_rdf}
                }}
            }}
            WHERE {{
                ?s ?p ?o .
            }}
            """
            
            # Execute move operation
            self.sparql.setQuery(move_query)
            self.sparql.setMethod("POST")
            result = self.sparql.query()
            
            logger.info(f"Promoted data from {agent_id} staging to consensus")
            
            return {
                "success": True,
                "from_staging": staging_graph,
                "to_consensus": self.consensus_graph,
                "validation_result": validation_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to promote to consensus for agent {agent_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def promote_to_main(self, rdf_data: str, consensus_validation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Promote validated RDF data from consensus to main graph.
        
        Args:
            rdf_data: RDF data to promote
            consensus_validation: Consensus validation results
        
        Returns:
            Dict: Result of the promotion
        """
        try:
            if not consensus_validation.get("success", False):
                return {"success": False, "error": "Consensus validation failed"}
            
            # Create final promotion RDF
            final_promotion_rdf = f"""
            @prefix prov: <http://www.w3.org/ns/prov#> .
            @prefix main: <http://example.org/main#> .
            
            <{rdf_data}>
                prov:wasAttributedTo <http://example.org/consensus> ;
                prov:generatedAtTime "{datetime.now().isoformat()}" ;
                prov:wasGeneratedBy <http://example.org/consensus_validation> ;
                main:status "production_ready" .
            """
            
            # Move data from consensus to main
            move_query = f"""
            WITH <{self.consensus_graph}>
            DELETE {{
                ?s ?p ?o .
            }}
            INSERT {{
                GRAPH <{self.main_graph}> {{
                    ?s ?p ?o .
                    {final_promotion_rdf}
                }}
            }}
            WHERE {{
                ?s ?p ?o .
            }}
            """
            
            # Execute move operation
            self.sparql.setQuery(move_query)
            self.sparql.setMethod("POST")
            result = self.sparql.query()
            
            logger.info("Promoted data from consensus to main graph")
            
            return {
                "success": True,
                "from_consensus": self.consensus_graph,
                "to_main": self.main_graph,
                "consensus_validation": consensus_validation,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to promote to main: {e}")
            return {"success": False, "error": str(e)}
    
    def query_communication_graph(self, session_id: str = None, 
                                agent_id: str = None) -> Dict[str, Any]:
        """
        Query the communication graph for agent messages.
        
        Args:
            session_id: Filter by session ID
            agent_id: Filter by agent ID
        
        Returns:
            Dict: Communication query results
        """
        try:
            # Build query filters
            filters = []
            if session_id:
                filters.append(f'?msg comm:sessionId session:{session_id}')
            if agent_id:
                filters.append(f'(?msg comm:fromAgent agent:{agent_id} || ?msg comm:toAgent agent:{agent_id})')
            
            filter_clause = " && ".join(filters) if filters else "true"
            
            # Query communication graph
            query = f"""
            SELECT ?msg ?fromAgent ?toAgent ?messageType ?content ?timestamp ?status
            WHERE {{
                GRAPH <{self.communication_graph}> {{
                    ?msg rdf:type comm:Message ;
                         comm:fromAgent ?fromAgent ;
                         comm:toAgent ?toAgent ;
                         comm:messageType ?messageType ;
                         comm:content ?content ;
                         comm:timestamp ?timestamp ;
                         comm:status ?status .
                    FILTER({filter_clause})
                }}
            }}
            ORDER BY ?timestamp
            """
            
            self.sparql.setQuery(query)
            self.sparql.setMethod("GET")
            result = self.sparql.query().convert()
            
            return {
                "success": True,
                "results": result,
                "communication_graph": self.communication_graph
            }
            
        except Exception as e:
            logger.error(f"Failed to query communication graph: {e}")
            return {"success": False, "error": str(e)}
    
    def get_graph_status(self) -> Dict[str, Any]:
        """
        Get status of all graph levels.
        
        Returns:
            Dict: Status of all graphs
        """
        try:
            status = {
                "agent_staging_graphs": {},
                "consensus_graph": self.consensus_graph,
                "main_graph": self.main_graph,
                "communication_graph": self.communication_graph,
                "registered_agents": len(self.registered_agents)
            }
            
            # Count triples in each graph
            for agent_id, staging_graph in self.agent_staging_graphs.items():
                count_query = f"""
                SELECT (COUNT(*) as ?count)
                WHERE {{
                    GRAPH <{staging_graph}> {{
                        ?s ?p ?o .
                    }}
                }}
                """
                
                self.sparql.setQuery(count_query)
                self.sparql.setMethod("GET")
                result = self.sparql.query().convert()
                
                status["agent_staging_graphs"][agent_id] = {
                    "graph": staging_graph,
                    "triple_count": result["results"]["bindings"][0]["count"]["value"]
                }
            
            return {"success": True, "status": status}
            
        except Exception as e:
            logger.error(f"Failed to get graph status: {e}")
            return {"success": False, "error": str(e)}
    
    def validate_graph_consistency(self) -> Dict[str, Any]:
        """
        Validate consistency across all graph levels.
        
        Returns:
            Dict: Consistency validation results
        """
        try:
            # Check for contradictions between graphs
            consistency_query = f"""
            SELECT ?entity ?property ?value1 ?value2 ?graph1 ?graph2
            WHERE {{
                GRAPH ?graph1 {{
                    ?entity ?property ?value1 .
                }}
                GRAPH ?graph2 {{
                    ?entity ?property ?value2 .
                }}
                FILTER(?value1 != ?value2)
                FILTER(?graph1 != ?graph2)
            }}
            """
            
            self.sparql.setQuery(consistency_query)
            self.sparql.setMethod("GET")
            result = self.sparql.query().convert()
            
            contradictions = result["results"]["bindings"]
            
            return {
                "success": True,
                "contradictions_found": len(contradictions),
                "contradictions": contradictions,
                "consistency_status": "consistent" if len(contradictions) == 0 else "inconsistent"
            }
            
        except Exception as e:
            logger.error(f"Failed to validate graph consistency: {e}")
            return {"success": False, "error": str(e)}

class RDFAgent:
    """Base class for RDF-based agents."""
    
    def __init__(self, agent_id: str, agent_type: str, 
                 communication_system: RDFCommunicationSystem):
        """
        Initialize an RDF-based agent.
        
        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent (ingest, collect, reason)
            communication_system: RDF communication system instance
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.comm_system = communication_system
        
        # Register agent
        permissions = ["read", "write_staging"]
        if agent_type == "reason":
            permissions.append("write_consensus")
        
        self.comm_system.register_agent(agent_id, agent_type, permissions)
        
        logger.info(f"RDF Agent {agent_id} ({agent_type}) initialized")
    
    def send_message(self, to_agent: str, message_type: str, 
                    content: str, session_id: str) -> str:
        """
        Send a message to another agent via RDF communication.
        
        Args:
            to_agent: Target agent ID
            message_type: Type of message
            content: Message content
            session_id: Session identifier
        
        Returns:
            str: RDF serialization of the communication
        """
        return self.comm_system.create_communication_rdf(
            self.agent_id, to_agent, message_type, content, session_id
        )
    
    def write_to_staging(self, rdf_data: str, operation: str = "write") -> Dict[str, Any]:
        """Write RDF data to agent's staging graph."""
        return self.comm_system.write_to_staging(
            self.agent_id, rdf_data, operation
        )
    
    def read_from_staging(self, query: str) -> Dict[str, Any]:
        """Read RDF data from agent's staging graph."""
        return self.comm_system.read_from_staging(self.agent_id, query)
    
    def promote_to_consensus(self, rdf_data: str, 
                           validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Promote validated data to consensus graph."""
        return self.comm_system.promote_to_consensus(
            self.agent_id, rdf_data, validation_result
        )
