"""
Validator Gateway Service

This module implements the core validator gateway that enforces validation
and reasoning before committing agent writes to the knowledge graph.
"""

import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL
from SPARQLWrapper import SPARQLWrapper, JSON

from .models import (
    ValidationRequest, ValidationResponse, ValidationError, ValidationErrorType,
    StagingWriteRequest, CommitRequest, QueryRequest, MetricsData, AlertData, ProvenanceData
)
from ..ontology.tourism_ontology import TourismOntology
from ..ontology.shacl_shapes import TourismSHACLShapes
from ..ontology.reasoning_rules import TourismReasoningEngine

logger = logging.getLogger(__name__)

# Define namespaces
TOURISM = Namespace("http://example.org/tourism#")
MSG = Namespace("http://example.org/messages#")

class ValidatorGateway:
    """Validator Gateway for multi-agent collaboration system."""
    
    def __init__(self, fuseki_endpoint: str = None):
        """
        Initialize the validator gateway.
        
        Args:
            fuseki_endpoint: Fuseki SPARQL endpoint URL
        """
        import os
        self.fuseki_endpoint = fuseki_endpoint or os.getenv('FUSEKI_ENDPOINT', 'http://localhost:3030/ds')
        self.sparql = SPARQLWrapper(self.fuseki_endpoint)
        self.sparql.setReturnFormat(JSON)
        
        # Initialize components
        self.ontology = TourismOntology()
        self.shacl_shapes = TourismSHACLShapes()
        self.reasoning_engine = TourismReasoningEngine()
        
        # Agent credentials and permissions
        self.agent_credentials: Dict[str, Dict[str, Any]] = {}
        
        # Metrics tracking
        self.metrics = MetricsData()
        
        # Alert system
        self.alerts: List[AlertData] = []
        
        # Provenance tracking
        self.provenance: List[ProvenanceData] = []
        
        logger.info("Validator Gateway initialized")
    
    def register_agent(self, agent_id: str, api_key: str, permissions: List[str] = None) -> bool:
        """
        Register a new agent with the gateway.
        
        Args:
            agent_id: Unique agent identifier
            api_key: API key for authentication
            permissions: List of agent permissions
            
        Returns:
            True if registration successful, False otherwise
        """
        if permissions is None:
            permissions = ["read", "write_staging"]
        
        self.agent_credentials[agent_id] = {
            "api_key": api_key,
            "permissions": permissions,
            "created_at": datetime.utcnow(),
            "active": True
        }
        
        logger.info(f"Registered agent: {agent_id}")
        return True
    
    def authenticate_agent(self, agent_id: str, api_key: str) -> bool:
        """
        Authenticate an agent.
        
        Args:
            agent_id: Agent identifier
            api_key: API key
            
        Returns:
            True if authentication successful, False otherwise
        """
        if agent_id not in self.agent_credentials:
            return False
        
        credentials = self.agent_credentials[agent_id]
        return (credentials["api_key"] == api_key and 
                credentials["active"] and
                "read" in credentials["permissions"])
    
    def validate_staging_write(self, request: ValidationRequest) -> ValidationResponse:
        """
        Validate a staging write request.
        
        Args:
            request: Validation request
            
        Returns:
            Validation response with results
        """
        start_time = time.time()
        
        try:
            # Authenticate agent
            if not self._authenticate_request(request.agent_id):
                return ValidationResponse(
                    success=False,
                    message="Authentication failed",
                    errors=[ValidationError(
                        error_type=ValidationErrorType.SHACL_VIOLATION,
                        message="Invalid agent credentials"
                    )]
                )
            
            # Parse RDF payload
            staging_graph = Graph()
            try:
                staging_graph.parse(data=request.rdf_payload, format="turtle")
            except Exception as e:
                return ValidationResponse(
                    success=False,
                    message="Invalid RDF format",
                    errors=[ValidationError(
                        error_type=ValidationErrorType.SHACL_VIOLATION,
                        message=f"RDF parsing error: {str(e)}"
                    )]
                )
            
            # Build merged view (Staging + Consensus + Main)
            merged_graph = self._build_merged_view(staging_graph, request.session_id)
            
            # Run SHACL validation
            shacl_result = self.shacl_shapes.get_validation_report(merged_graph)
            
            if not shacl_result["conforms"]:
                errors = []
                for violation in shacl_result["violations"]:
                    errors.append(ValidationError(
                        error_type=ValidationErrorType.SHACL_VIOLATION,
                        message=violation.get("message", "SHACL validation failed"),
                        focus_node=violation.get("focus_node"),
                        property_path=violation.get("path"),
                        severity=violation.get("severity", "error"),
                        details=violation
                    ))
                
                self._update_metrics(success=False, error_type="SHACL_VIOLATION")
                return ValidationResponse(
                    success=False,
                    message="SHACL validation failed",
                    errors=errors
                )
            
            # Run forward-chaining reasoning
            reasoning_result = self.reasoning_engine.run_reasoning(merged_graph)
            
            # Check for contradictions
            if reasoning_result["contradictions"]:
                errors = []
                for contradiction in reasoning_result["contradictions"]:
                    errors.append(ValidationError(
                        error_type=ValidationErrorType.LOGIC_CONTRADICTION,
                        message=contradiction.get("message", "Logic contradiction detected"),
                        focus_node=contradiction.get("entity"),
                        details=contradiction
                    ))
                
                self._update_metrics(success=False, error_type="LOGIC_CONTRADICTION")
                return ValidationResponse(
                    success=False,
                    message="Logic contradiction detected",
                    errors=errors,
                    contradictions=reasoning_result["contradictions"]
                )
            
            # Validate consistency
            consistency_result = self.reasoning_engine.validate_consistency(merged_graph)
            
            if not consistency_result["is_consistent"]:
                errors = []
                for issue in consistency_result["consistency_issues"]:
                    errors.append(ValidationError(
                        error_type=ValidationErrorType.LOGIC_CONTRADICTION,
                        message=issue.get("message", "Consistency violation"),
                        focus_node=issue.get("entity"),
                        details=issue
                    ))
                
                self._update_metrics(success=False, error_type="LOGIC_CONTRADICTION")
                return ValidationResponse(
                    success=False,
                    message="Consistency validation failed",
                    errors=errors
                )
            
            # Success - prepare response
            processing_time = (time.time() - start_time) * 1000
            
            # Track provenance
            self._track_provenance(request, reasoning_result["derived_facts"])
            
            # Update metrics
            self._update_metrics(success=True, processing_time=processing_time)
            
            return ValidationResponse(
                success=True,
                message="Validation successful",
                derived_facts=self._format_derived_facts(reasoning_result["derived_facts"]),
                reasoning_iterations=reasoning_result["iterations"],
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            self._update_metrics(success=False, error_type="SYSTEM_ERROR")
            return ValidationResponse(
                success=False,
                message=f"System error: {str(e)}",
                errors=[ValidationError(
                    error_type=ValidationErrorType.SHACL_VIOLATION,
                    message="Internal system error"
                )]
            )
    
    def commit_staging_data(self, request: CommitRequest) -> ValidationResponse:
        """
        Commit validated staging data to consensus graph.
        
        Args:
            request: Commit request
            
        Returns:
            Validation response
        """
        try:
            # Authenticate agent
            if not self._authenticate_request(request.agent_id):
                return ValidationResponse(
                    success=False,
                    message="Authentication failed"
                )
            
            # Get staging data
            staging_data = self._get_staging_data(request.staging_graph)
            if not staging_data:
                return ValidationResponse(
                    success=False,
                    message="No staging data found"
                )
            
            # Validate before commit
            validation_request = ValidationRequest(
                agent_id=request.agent_id,
                session_id=request.session_id,
                target_graph=request.staging_graph,
                rdf_payload=staging_data.serialize(format="turtle")
            )
            
            validation_result = self.validate_staging_write(validation_request)
            
            if not validation_result.success:
                return validation_result
            
            # Commit to consensus graph
            consensus_graph_uri = f"http://example.org/consensus/{request.session_id}"
            self._commit_to_consensus(staging_data, consensus_graph_uri)
            
            # Clear staging
            self._clear_staging(request.staging_graph)
            
            # Create message notification
            self._create_message_notification(request, validation_result.derived_facts)
            
            return ValidationResponse(
                success=True,
                message="Data committed successfully",
                derived_facts=validation_result.derived_facts
            )
            
        except Exception as e:
            logger.error(f"Commit error: {e}")
            return ValidationResponse(
                success=False,
                message=f"Commit failed: {str(e)}"
            )
    
    def query_knowledge_graph(self, request: QueryRequest) -> Dict[str, Any]:
        """
        Execute SPARQL query against the knowledge graph.
        
        Args:
            request: Query request
            
        Returns:
            Query results
        """
        try:
            self.sparql.setQuery(request.query)
            results = self.sparql.query().convert()
            return {
                "success": True,
                "results": results,
                "format": request.format
            }
        except Exception as e:
            logger.error(f"Query error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _authenticate_request(self, agent_id: str) -> bool:
        """Authenticate agent request."""
        return agent_id in self.agent_credentials and self.agent_credentials[agent_id]["active"]
    
    def _build_merged_view(self, staging_graph: Graph, session_id: str) -> Graph:
        """Build merged view of staging + consensus + main graphs."""
        merged = Graph()
        
        # Add main graph (read-only)
        main_data = self._get_main_data()
        if main_data:
            merged += main_data
        
        # Add consensus graph for session
        consensus_data = self._get_consensus_data(session_id)
        if consensus_data:
            merged += consensus_data
        
        # Add staging data
        merged += staging_graph
        
        return merged
    
    def _get_main_data(self) -> Optional[Graph]:
        """Get main graph data."""
        try:
            query = """
            CONSTRUCT { ?s ?p ?o }
            WHERE {
                GRAPH <http://example.org/main> {
                    ?s ?p ?o
                }
            }
            """
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
            # Convert results to Graph (simplified)
            return Graph()
        except:
            return None
    
    def _get_consensus_data(self, session_id: str) -> Optional[Graph]:
        """Get consensus graph data for session."""
        try:
            query = f"""
            CONSTRUCT {{ ?s ?p ?o }}
            WHERE {{
                GRAPH <http://example.org/consensus/{session_id}> {{
                    ?s ?p ?o
                }}
            }}
            """
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
            return Graph()
        except:
            return None
    
    def _get_staging_data(self, staging_graph_uri: str) -> Optional[Graph]:
        """Get staging data."""
        try:
            query = f"""
            CONSTRUCT {{ ?s ?p ?o }}
            WHERE {{
                GRAPH <{staging_graph_uri}> {{
                    ?s ?p ?o
                }}
            }}
            """
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
            return Graph()
        except:
            return None
    
    def _commit_to_consensus(self, data: Graph, consensus_uri: str):
        """Commit data to consensus graph."""
        # Implementation would use SPARQL UPDATE
        pass
    
    def _clear_staging(self, staging_uri: str):
        """Clear staging graph."""
        # Implementation would use SPARQL UPDATE
        pass
    
    def _create_message_notification(self, request: CommitRequest, derived_facts: List[Dict]):
        """Create message notification for other agents."""
        # Create message in message graph
        pass
    
    def _track_provenance(self, request: ValidationRequest, derived_facts: List[Tuple]):
        """Track provenance of derived facts."""
        for fact in derived_facts:
            provenance = ProvenanceData(
                fact_id=f"fact_{len(self.provenance)}",
                source_agent=request.agent_id,
                session_id=request.session_id,
                fact_type="derived",
                graph_uri=request.target_graph
            )
            self.provenance.append(provenance)
    
    def _format_derived_facts(self, facts: List[Tuple]) -> List[Dict[str, Any]]:
        """Format derived facts for response."""
        formatted = []
        for fact in facts:
            formatted.append({
                "subject": str(fact[0]),
                "predicate": str(fact[1]),
                "object": str(fact[2])
            })
        return formatted
    
    def _update_metrics(self, success: bool, error_type: str = None, processing_time: float = 0):
        """Update metrics data."""
        self.metrics.total_requests += 1
        
        if success:
            self.metrics.successful_validations += 1
        else:
            self.metrics.failed_validations += 1
            
            if error_type == "SHACL_VIOLATION":
                self.metrics.shacl_violations += 1
            elif error_type == "LOGIC_CONTRADICTION":
                self.metrics.logic_contradictions += 1
        
        if processing_time > 0:
            # Update average processing time
            total_time = self.metrics.average_processing_time_ms * (self.metrics.total_requests - 1)
            self.metrics.average_processing_time_ms = (total_time + processing_time) / self.metrics.total_requests
    
    def get_metrics(self) -> MetricsData:
        """Get current metrics."""
        return self.metrics
    
    def get_alerts(self) -> List[AlertData]:
        """Get current alerts."""
        return self.alerts
    
    def get_provenance(self, agent_id: str = None) -> List[ProvenanceData]:
        """Get provenance data, optionally filtered by agent."""
        if agent_id:
            return [p for p in self.provenance if p.source_agent == agent_id]
        return self.provenance
