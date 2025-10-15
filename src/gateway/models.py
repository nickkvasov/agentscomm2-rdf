"""
Pydantic models for the validator gateway API.

This module defines the request/response models for the gateway service.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

class ValidationErrorType(str, Enum):
    """Types of validation errors."""
    SHACL_VIOLATION = "SHACL_VIOLATION"
    LOGIC_CONTRADICTION = "LOGIC_CONTRADICTION"
    FUNCTIONAL_PROPERTY_VIOLATION = "FUNCTIONAL_PROPERTY_VIOLATION"
    RANGE_VIOLATION = "RANGE_VIOLATION"
    DOMAIN_VIOLATION = "DOMAIN_VIOLATION"
    DISJOINT_CLASS_VIOLATION = "DISJOINT_CLASS_VIOLATION"

class ValidationRequest(BaseModel):
    """Request model for validation."""
    agent_id: str = Field(..., description="Identifier of the requesting agent")
    session_id: str = Field(..., description="Session identifier")
    target_graph: str = Field(..., description="Target staging graph IRI")
    rdf_payload: str = Field(..., description="RDF data to be validated (Turtle format)")
    operation: str = Field(default="add", description="Operation type: 'add' or 'remove'")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")

class ValidationError(BaseModel):
    """Model for validation errors."""
    error_type: ValidationErrorType = Field(..., description="Type of validation error")
    message: str = Field(..., description="Human-readable error message")
    focus_node: Optional[str] = Field(None, description="Node that caused the error")
    property_path: Optional[str] = Field(None, description="Property path that caused the error")
    severity: str = Field(default="error", description="Error severity level")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional error details")

class ValidationResponse(BaseModel):
    """Response model for validation."""
    success: bool = Field(..., description="Whether validation was successful")
    message: str = Field(..., description="Response message")
    errors: List[ValidationError] = Field(default_factory=list, description="List of validation errors")
    derived_facts: List[Dict[str, Any]] = Field(default_factory=list, description="Facts derived during reasoning")
    contradictions: List[Dict[str, Any]] = Field(default_factory=list, description="Contradictions found")
    reasoning_iterations: int = Field(default=0, description="Number of reasoning iterations")
    processing_time_ms: float = Field(default=0.0, description="Processing time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

class StagingWriteRequest(BaseModel):
    """Request model for staging writes."""
    agent_id: str = Field(..., description="Agent identifier")
    session_id: str = Field(..., description="Session identifier")
    staging_graph: str = Field(..., description="Staging graph IRI")
    rdf_data: str = Field(..., description="RDF data to stage")
    operation: str = Field(default="add", description="Operation type")

class CommitRequest(BaseModel):
    """Request model for committing staged data."""
    agent_id: str = Field(..., description="Agent identifier")
    session_id: str = Field(..., description="Session identifier")
    staging_graph: str = Field(..., description="Staging graph IRI to commit")

class QueryRequest(BaseModel):
    """Request model for SPARQL queries."""
    query: str = Field(..., description="SPARQL query string")
    graph_uri: Optional[str] = Field(None, description="Target graph URI")
    format: str = Field(default="json", description="Response format")

class AgentCredentials(BaseModel):
    """Model for agent authentication credentials."""
    agent_id: str = Field(..., description="Agent identifier")
    api_key: str = Field(..., description="API key for authentication")
    permissions: List[str] = Field(default_factory=list, description="Agent permissions")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")

class MetricsData(BaseModel):
    """Model for metrics data."""
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Metrics timestamp")
    total_requests: int = Field(default=0, description="Total number of requests")
    successful_validations: int = Field(default=0, description="Successful validations")
    failed_validations: int = Field(default=0, description="Failed validations")
    shacl_violations: int = Field(default=0, description="SHACL violations")
    logic_contradictions: int = Field(default=0, description="Logic contradictions")
    average_processing_time_ms: float = Field(default=0.0, description="Average processing time")
    reasoning_iterations_total: int = Field(default=0, description="Total reasoning iterations")
    derived_facts_total: int = Field(default=0, description="Total derived facts")

class AlertData(BaseModel):
    """Model for alert data."""
    alert_id: str = Field(..., description="Unique alert identifier")
    alert_type: str = Field(..., description="Type of alert")
    severity: str = Field(..., description="Alert severity")
    message: str = Field(..., description="Alert message")
    source_agent: str = Field(..., description="Agent that triggered the alert")
    session_id: str = Field(..., description="Session identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Alert timestamp")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional alert details")
    resolved: bool = Field(default=False, description="Whether the alert is resolved")

class ProvenanceData(BaseModel):
    """Model for provenance tracking."""
    fact_id: str = Field(..., description="Unique fact identifier")
    source_agent: str = Field(..., description="Agent that created the fact")
    session_id: str = Field(..., description="Session identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    rule_id: Optional[str] = Field(None, description="Reasoning rule that derived the fact")
    rule_version: Optional[str] = Field(None, description="Version of the reasoning rule")
    fact_type: str = Field(..., description="Type of fact (asserted or derived)")
    graph_uri: str = Field(..., description="Graph where the fact is stored")
