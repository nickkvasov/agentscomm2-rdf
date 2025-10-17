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
from ..ontology.fuseki_client import FusekiClient

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
        
        # Initialize Fuseki client
        self.fuseki_client = FusekiClient(self.fuseki_endpoint)
        
        # Initialize components with FusekiClient
        self.ontology = TourismOntology(self.fuseki_client)
        self.shacl_shapes = TourismSHACLShapes(self.fuseki_client)
        self.reasoning_engine = TourismReasoningEngine(self.fuseki_client)
        
        # Load ontology and shapes into Fuseki (required)
        if not self._load_ontology_to_fuseki():
            raise RuntimeError("Failed to load ontology into Fuseki - Fuseki is required for operation")
        
        # Agent credentials and permissions
        self.agent_credentials: Dict[str, Dict[str, Any]] = {}
        
        # Metrics tracking
        self.metrics = MetricsData()
        
        # Alert system
        self.alerts: List[AlertData] = []
        
        # Provenance tracking
        self.provenance: List[ProvenanceData] = []
        
        logger.info("Validator Gateway initialized")
    
    def _load_ontology_to_fuseki(self):
        """Load ontology, shapes, and rules into Fuseki."""
        try:
            import os
            
            # Test Fuseki connection first
            if not self.fuseki_client.test_connection():
                logger.error("❌ Cannot connect to Fuseki - Fuseki is required")
                return False
            
            # Get ontology directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            ontology_dir = os.path.join(project_root, "ontology")
            
            success = True
            
            # Load ontology
            ontology_file = os.path.join(ontology_dir, "tourism_ontology.ttl")
            if os.path.exists(ontology_file):
                if not self.fuseki_client.load_ontology(ontology_file):
                    logger.error(f"❌ Failed to load ontology: {ontology_file}")
                    success = False
            else:
                logger.error(f"❌ Ontology file not found: {ontology_file}")
                success = False
            
            # Load SHACL shapes
            shapes_file = os.path.join(ontology_dir, "tourism_shacl_shapes.ttl")
            if os.path.exists(shapes_file):
                if not self.fuseki_client.load_shacl_shapes(shapes_file):
                    logger.error(f"❌ Failed to load SHACL shapes: {shapes_file}")
                    success = False
            else:
                logger.error(f"❌ SHACL shapes file not found: {shapes_file}")
                success = False
            
            # Load reasoning rules
            rules_file = os.path.join(ontology_dir, "tourism_reasoning_rules.ttl")
            if os.path.exists(rules_file):
                if not self.fuseki_client.load_reasoning_rules(rules_file):
                    logger.error(f"❌ Failed to load reasoning rules: {rules_file}")
                    success = False
            else:
                logger.error(f"❌ Reasoning rules file not found: {rules_file}")
                success = False
            
            if success:
                logger.info("✅ Loaded all ontology components into Fuseki")
            else:
                logger.error("❌ Failed to load some ontology components into Fuseki")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to load ontology into Fuseki: {e}")
            return False
    
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
            
            # Build agent-specific merged view (Agent Staging + Consensus + Main)
            merged_graph = self._build_agent_merged_view(
                agent_id=request.agent_id,
                staging_graph=staging_graph, 
                session_id=request.session_id
            )
            
            # Run agent-level consistency validation
            agent_consistency_result = self._validate_agent_consistency(
                agent_id=request.agent_id,
                staging_graph=staging_graph,
                merged_graph=merged_graph
            )
            
            if not agent_consistency_result["is_consistent"]:
                errors = []
                for issue in agent_consistency_result["consistency_issues"]:
                    errors.append(ValidationError(
                        error_type=ValidationErrorType.LOGIC_CONTRADICTION,
                        message=f"Agent {request.agent_id} consistency violation: {issue.get('message', 'Consistency violation')}",
                        focus_node=issue.get("entity"),
                        details=issue
                    ))
                
                self._update_metrics(success=False, error_type="AGENT_CONSISTENCY_VIOLATION")
                return ValidationResponse(
                    success=False,
                    message=f"Agent {request.agent_id} consistency validation failed",
                    errors=errors,
                    agent_id=request.agent_id
                )
            
            # Run SHACL validation
            shacl_result = self.shacl_shapes.get_validation_report(merged_graph)
            
            if not shacl_result["conforms"]:
                errors = []
                for violation in shacl_result["violations"]:
                    errors.append(ValidationError(
                        error_type=ValidationErrorType.SHACL_VIOLATION,
                        message=f"Agent {request.agent_id} SHACL violation: {violation.get('message', 'SHACL validation failed')}",
                        focus_node=violation.get("focus_node"),
                        property_path=violation.get("path"),
                        severity=violation.get("severity", "error"),
                        details=violation
                    ))
                
                self._update_metrics(success=False, error_type="SHACL_VIOLATION")
                return ValidationResponse(
                    success=False,
                    message=f"Agent {request.agent_id} SHACL validation failed",
                    errors=errors,
                    agent_id=request.agent_id
                )
            
            # Run forward-chaining reasoning
            reasoning_result = self.reasoning_engine.run_reasoning(merged_graph)
            
            # Check for contradictions
            if reasoning_result["contradictions"]:
                errors = []
                for contradiction in reasoning_result["contradictions"]:
                    errors.append(ValidationError(
                        error_type=ValidationErrorType.LOGIC_CONTRADICTION,
                        message=f"Agent {request.agent_id} contradiction: {contradiction.get('message', 'Logic contradiction detected')}",
                        focus_node=contradiction.get("entity"),
                        details=contradiction
                    ))
                
                self._update_metrics(success=False, error_type="LOGIC_CONTRADICTION")
                return ValidationResponse(
                    success=False,
                    message=f"Agent {request.agent_id} logic contradiction detected",
                    errors=errors,
                    contradictions=reasoning_result["contradictions"],
                    agent_id=request.agent_id
                )
            
            # Validate consistency
            consistency_result = self.reasoning_engine.validate_consistency(merged_graph)
            
            if not consistency_result["is_consistent"]:
                errors = []
                for issue in consistency_result["consistency_issues"]:
                    errors.append(ValidationError(
                        error_type=ValidationErrorType.LOGIC_CONTRADICTION,
                        message=f"Agent {request.agent_id} consistency violation: {issue.get('message', 'Consistency violation')}",
                        focus_node=issue.get("entity"),
                        details=issue
                    ))
                
                self._update_metrics(success=False, error_type="LOGIC_CONTRADICTION")
                return ValidationResponse(
                    success=False,
                    message=f"Agent {request.agent_id} consistency validation failed",
                    errors=errors,
                    agent_id=request.agent_id
                )
            
            # Success - prepare response
            processing_time = (time.time() - start_time) * 1000
            
            # Track provenance
            self._track_provenance(request, reasoning_result["derived_facts"])
            
            # Update metrics
            self._update_metrics(success=True, processing_time=processing_time)
            
            return ValidationResponse(
                success=True,
                message=f"Agent {request.agent_id} validation successful",
                derived_facts=self._format_derived_facts(reasoning_result["derived_facts"]),
                reasoning_iterations=reasoning_result["iterations"],
                processing_time_ms=processing_time,
                agent_id=request.agent_id
            )
            
        except Exception as e:
            logger.error(f"Agent {request.agent_id} validation error: {e}")
            self._update_metrics(success=False, error_type="SYSTEM_ERROR", agent_id=request.agent_id)
            return ValidationResponse(
                success=False,
                message=f"Agent {request.agent_id} system error: {str(e)}",
                agent_id=request.agent_id,
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
            
            # CRITICAL: Check consensus/main graph consistency before final commit
            consensus_consistency_result = self._validate_consensus_main_consistency(
                session_id=request.session_id,
                consensus_graph_uri=consensus_graph_uri
            )
            
            if not consensus_consistency_result["is_consistent"]:
                # Rollback consensus commit if consistency check fails
                self._rollback_consensus_commit(consensus_graph_uri)
                
                errors = []
                for issue in consensus_consistency_result["consistency_issues"]:
                    errors.append(ValidationError(
                        error_type=ValidationErrorType.LOGIC_CONTRADICTION,
                        message=f"Consensus/Main consistency violation: {issue.get('message', 'Consistency violation')}",
                        focus_node=issue.get("entity"),
                        details=issue
                    ))
                
                return ValidationResponse(
                    success=False,
                    message="Consensus/Main graph consistency validation failed",
                    errors=errors
                )
            
            # Clear staging only after successful consistency check
            self._clear_staging(request.staging_graph)
            
            # Create message notification
            self._create_message_notification(request, validation_result.derived_facts)
            
            return ValidationResponse(
                success=True,
                message="Data committed successfully with consensus/main consistency validation",
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
    
    def _build_agent_merged_view(self, agent_id: str, staging_graph: Graph, session_id: str) -> Graph:
        """Build agent-specific merged view: Agent Staging + Consensus + Main."""
        merged = Graph()
        
        # Add main graph (read-only)
        main_data = self._get_main_data()
        if main_data:
            merged += main_data
        
        # Add consensus graph for session
        consensus_data = self._get_consensus_data(session_id)
        if consensus_data:
            merged += consensus_data
        
        # Add agent's staging data
        merged += staging_graph
        
        logger.info(f"Built merged view for agent {agent_id}: {len(merged)} triples")
        return merged
    
    def _validate_agent_consistency(self, agent_id: str, staging_graph: Graph, merged_graph: Graph) -> Dict[str, Any]:
        """
        Validate agent-specific consistency against consensus and main graphs.
        
        Args:
            agent_id: ID of the agent
            staging_graph: Agent's staging data
            merged_graph: Combined view (staging + consensus + main)
            
        Returns:
            Consistency validation result
        """
        logger.info(f"Validating agent {agent_id} consistency")
        
        consistency_issues = []
        
        # Check for conflicts with existing consensus data
        consensus_conflicts = self._check_consensus_conflicts(agent_id, staging_graph, merged_graph)
        consistency_issues.extend(consensus_conflicts)
        
        # Check for conflicts with main graph data
        main_conflicts = self._check_main_graph_conflicts(agent_id, staging_graph, merged_graph)
        consistency_issues.extend(main_conflicts)
        
        # Check for agent-specific contradictions
        agent_contradictions = self._check_agent_contradictions(agent_id, staging_graph, merged_graph)
        consistency_issues.extend(agent_contradictions)
        
        return {
            "is_consistent": len(consistency_issues) == 0,
            "consistency_issues": consistency_issues,
            "agent_id": agent_id,
            "total_issues": len(consistency_issues)
        }
    
    def _check_consensus_conflicts(self, agent_id: str, staging_graph: Graph, merged_graph: Graph) -> List[Dict[str, Any]]:
        """Check for conflicts between agent staging and consensus data."""
        conflicts = []
        
        # Check for conflicting ratings
        rating_conflicts = self._check_rating_conflicts(agent_id, staging_graph, merged_graph)
        conflicts.extend(rating_conflicts)
        
        # Check for conflicting amenities
        amenity_conflicts = self._check_amenity_conflicts(agent_id, staging_graph, merged_graph)
        conflicts.extend(amenity_conflicts)
        
        return conflicts
    
    def _check_main_graph_conflicts(self, agent_id: str, staging_graph: Graph, merged_graph: Graph) -> List[Dict[str, Any]]:
        """Check for conflicts between agent staging and main graph data."""
        conflicts = []
        
        # Check for conflicting class assignments
        class_conflicts = self._check_class_conflicts(agent_id, staging_graph, merged_graph)
        conflicts.extend(class_conflicts)
        
        return conflicts
    
    def _check_agent_contradictions(self, agent_id: str, staging_graph: Graph, merged_graph: Graph) -> List[Dict[str, Any]]:
        """Check for contradictions within agent's own data."""
        contradictions = []
        
        # Check for self-contradictory facts in agent's staging
        self_contradictions = self._check_self_contradictions(agent_id, staging_graph)
        contradictions.extend(self_contradictions)
        
        return contradictions
    
    def _check_rating_conflicts(self, agent_id: str, staging_graph: Graph, merged_graph: Graph) -> List[Dict[str, Any]]:
        """Check for conflicting ratings between agent and consensus."""
        conflicts = []
        
        # Find entities with ratings in both staging and consensus
        query = """
        SELECT ?entity ?staging_rating ?consensus_rating
        WHERE {
            ?entity tourism:hasRating ?staging_rating .
            ?entity tourism:hasRating ?consensus_rating .
            FILTER(?staging_rating != ?consensus_rating)
        }
        """
        
        for row in merged_graph.query(query):
            entity = str(row.entity)
            staging_rating = float(row.staging_rating)
            consensus_rating = float(row.consensus_rating)
            
            # Only flag significant conflicts (difference > 1.0)
            if abs(staging_rating - consensus_rating) > 1.0:
                conflicts.append({
                    "type": "RATING_CONFLICT",
                    "entity": entity,
                    "agent_id": agent_id,
                    "staging_rating": staging_rating,
                    "consensus_rating": consensus_rating,
                    "message": f"Agent {agent_id} rating {staging_rating} conflicts with consensus rating {consensus_rating} for {entity}"
                })
        
        return conflicts
    
    def _check_amenity_conflicts(self, agent_id: str, staging_graph: Graph, merged_graph: Graph) -> List[Dict[str, Any]]:
        """Check for conflicting amenities between agent and consensus."""
        conflicts = []
        
        # This would check for contradictory amenities (e.g., "FamilyFriendly" vs "NotFamilyFriendly")
        # Implementation depends on specific business rules
        
        return conflicts
    
    def _check_class_conflicts(self, agent_id: str, staging_graph: Graph, merged_graph: Graph) -> List[Dict[str, Any]]:
        """Check for conflicting class assignments."""
        conflicts = []
        
        # Check for disjoint class violations
        query = """
        SELECT ?entity ?class1 ?class2
        WHERE {
            ?entity rdf:type ?class1 .
            ?entity rdf:type ?class2 .
            ?class1 owl:disjointWith ?class2 .
        }
        """
        
        for row in merged_graph.query(query):
            entity = str(row.entity)
            class1 = str(row.class1)
            class2 = str(row.class2)
            
            conflicts.append({
                "type": "DISJOINT_CLASS_VIOLATION",
                "entity": entity,
                "agent_id": agent_id,
                "conflicting_classes": [class1, class2],
                "message": f"Agent {agent_id} assigned {entity} to disjoint classes {class1} and {class2}"
            })
        
        return conflicts
    
    def _check_self_contradictions(self, agent_id: str, staging_graph: Graph) -> List[Dict[str, Any]]:
        """Check for contradictions within agent's own staging data."""
        contradictions = []
        
        # Check for entities marked as contradictions by SWRL rules
        for entity, predicate, obj in staging_graph.triples((None, RDF.type, TOURISM.Contradiction)):
            contradictions.append({
                "type": "SELF_CONTRADICTION",
                "entity": str(entity),
                "agent_id": agent_id,
                "message": f"Agent {agent_id} created contradictory entity {entity}"
            })
        
        return contradictions
    
    def _validate_consensus_main_consistency(self, session_id: str, consensus_graph_uri: str) -> Dict[str, Any]:
        """
        Validate consistency between consensus graph and main graph before final commit.
        
        This is the CRITICAL step that was missing - checking if consensus data
        is consistent with the main graph before committing to main.
        
        Args:
            session_id: Session ID
            consensus_graph_uri: URI of the consensus graph
            
        Returns:
            Consistency validation result
        """
        logger.info(f"Validating consensus/main consistency for session {session_id}")
        
        try:
            # Get consensus data
            consensus_data = self._get_consensus_data(session_id)
            if not consensus_data:
                return {
                    "is_consistent": True,
                    "consistency_issues": [],
                    "message": "No consensus data to validate"
                }
            
            # Get main graph data
            main_data = self._get_main_data()
            if not main_data:
                return {
                    "is_consistent": True,
                    "consistency_issues": [],
                    "message": "No main graph data to validate against"
                }
            
            # Build merged view: Consensus + Main
            merged_graph = Graph()
            merged_graph += main_data
            merged_graph += consensus_data
            
            logger.info(f"Built consensus/main merged view: {len(merged_graph)} triples")
            
            # Run comprehensive consistency validation
            consistency_issues = []
            
            # 1. Check for conflicts between consensus and main
            consensus_main_conflicts = self._check_consensus_main_conflicts(consensus_data, main_data, merged_graph)
            consistency_issues.extend(consensus_main_conflicts)
            
            # 2. Run SWRL reasoning on merged graph
            reasoning_result = self.reasoning_engine.run_reasoning(merged_graph)
            
            # 3. Check for contradictions in merged graph
            if reasoning_result["contradictions"]:
                for contradiction in reasoning_result["contradictions"]:
                    consistency_issues.append({
                        "type": "CONSENSUS_MAIN_CONTRADICTION",
                        "entity": contradiction.get("entity"),
                        "message": f"Consensus/Main contradiction: {contradiction.get('message', 'Logical contradiction')}",
                        "details": contradiction
                    })
            
            # 4. Run final consistency validation
            final_consistency = self.reasoning_engine.validate_consistency(merged_graph)
            if not final_consistency["is_consistent"]:
                for issue in final_consistency["consistency_issues"]:
                    consistency_issues.append({
                        "type": "FINAL_CONSISTENCY_VIOLATION",
                        "entity": issue.get("entity"),
                        "message": f"Final consistency violation: {issue.get('message', 'Consistency violation')}",
                        "details": issue
                    })
            
            return {
                "is_consistent": len(consistency_issues) == 0,
                "consistency_issues": consistency_issues,
                "session_id": session_id,
                "total_issues": len(consistency_issues)
            }
            
        except Exception as e:
            logger.error(f"Error validating consensus/main consistency: {e}")
            return {
                "is_consistent": False,
                "consistency_issues": [{
                    "type": "VALIDATION_ERROR",
                    "message": f"Consensus/Main validation error: {str(e)}"
                }],
                "session_id": session_id,
                "total_issues": 1
            }
    
    def _check_consensus_main_conflicts(self, consensus_data: Graph, main_data: Graph, merged_graph: Graph) -> List[Dict[str, Any]]:
        """Check for conflicts between consensus and main graph data."""
        conflicts = []
        
        # Check for conflicting ratings between consensus and main
        rating_conflicts = self._check_consensus_main_rating_conflicts(consensus_data, main_data, merged_graph)
        conflicts.extend(rating_conflicts)
        
        # Check for conflicting class assignments
        class_conflicts = self._check_consensus_main_class_conflicts(consensus_data, main_data, merged_graph)
        conflicts.extend(class_conflicts)
        
        return conflicts
    
    def _check_consensus_main_rating_conflicts(self, consensus_data: Graph, main_data: Graph, merged_graph: Graph) -> List[Dict[str, Any]]:
        """Check for rating conflicts between consensus and main graphs."""
        conflicts = []
        
        # Find entities with ratings in both consensus and main
        query = """
        SELECT ?entity ?consensus_rating ?main_rating
        WHERE {
            ?entity tourism:hasRating ?consensus_rating .
            ?entity tourism:hasRating ?main_rating .
            FILTER(?consensus_rating != ?main_rating)
        }
        """
        
        for row in merged_graph.query(query):
            entity = str(row.entity)
            consensus_rating = float(row.consensus_rating)
            main_rating = float(row.main_rating)
            
            # Flag significant conflicts (difference > 1.0)
            if abs(consensus_rating - main_rating) > 1.0:
                conflicts.append({
                    "type": "CONSENSUS_MAIN_RATING_CONFLICT",
                    "entity": entity,
                    "consensus_rating": consensus_rating,
                    "main_rating": main_rating,
                    "message": f"Consensus rating {consensus_rating} conflicts with main graph rating {main_rating} for {entity}"
                })
        
        return conflicts
    
    def _check_consensus_main_class_conflicts(self, consensus_data: Graph, main_data: Graph, merged_graph: Graph) -> List[Dict[str, Any]]:
        """Check for class conflicts between consensus and main graphs."""
        conflicts = []
        
        # Check for disjoint class violations in merged graph
        query = """
        SELECT ?entity ?class1 ?class2
        WHERE {
            ?entity rdf:type ?class1 .
            ?entity rdf:type ?class2 .
            ?class1 owl:disjointWith ?class2 .
        }
        """
        
        for row in merged_graph.query(query):
            entity = str(row.entity)
            class1 = str(row.class1)
            class2 = str(row.class2)
            
            conflicts.append({
                "type": "CONSENSUS_MAIN_CLASS_CONFLICT",
                "entity": entity,
                "conflicting_classes": [class1, class2],
                "message": f"Consensus/Main merged graph has disjoint class violation: {entity} is both {class1} and {class2}"
            })
        
        return conflicts
    
    def _rollback_consensus_commit(self, consensus_graph_uri: str):
        """Rollback consensus commit if consistency validation fails."""
        try:
            # Clear the consensus graph
            self._clear_staging(consensus_graph_uri)
            logger.info(f"Rolled back consensus commit for {consensus_graph_uri}")
        except Exception as e:
            logger.error(f"Failed to rollback consensus commit: {e}")
    
    def _get_main_data(self) -> Optional[Graph]:
        """Get main graph data."""
        try:
            return self.fuseki_client.get_graph_data(self.fuseki_client.main_graph)
        except:
            return None
    
    def _get_consensus_data(self, session_id: str) -> Optional[Graph]:
        """Get consensus graph data for session."""
        try:
            consensus_uri = f"{self.fuseki_client.consensus_graph}/{session_id}"
            return self.fuseki_client.get_graph_data(consensus_uri)
        except:
            return None
    
    def _get_staging_data(self, staging_graph_uri: str) -> Optional[Graph]:
        """Get staging data."""
        try:
            return self.fuseki_client.get_graph_data(staging_graph_uri)
        except:
            return None
    
    def _commit_to_consensus(self, data: Graph, consensus_uri: str):
        """Commit data to consensus graph."""
        try:
            self.fuseki_client.add_data_to_graph(data, consensus_uri)
            logger.info(f"✅ Committed data to consensus graph: {consensus_uri}")
        except Exception as e:
            logger.error(f"❌ Failed to commit to consensus: {e}")
    
    def _clear_staging(self, staging_uri: str):
        """Clear staging graph."""
        try:
            self.fuseki_client.clear_graph(staging_uri)
            logger.info(f"✅ Cleared staging graph: {staging_uri}")
        except Exception as e:
            logger.error(f"❌ Failed to clear staging: {e}")
    
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
