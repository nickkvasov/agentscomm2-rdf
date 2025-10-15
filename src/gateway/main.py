"""
FastAPI application for the Validator Gateway.

This module provides the REST API endpoints for the validator gateway service.
"""

import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.gateway.validator_gateway import ValidatorGateway
from src.gateway.models import (
    ValidationRequest, ValidationResponse, StagingWriteRequest, 
    CommitRequest, QueryRequest, MetricsData, AlertData
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global gateway instance
gateway: ValidatorGateway = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global gateway
    # Initialize gateway
    gateway = ValidatorGateway()
    
    # Register sample agents for testing
    gateway.register_agent("agent_ingest", "key_ingest_123", ["read", "write_staging"])
    gateway.register_agent("agent_collect", "key_collect_456", ["read", "write_staging"])
    gateway.register_agent("agent_reason", "key_reason_789", ["read", "write_staging"])
    
    logger.info("Validator Gateway started")
    yield
    
    logger.info("Validator Gateway stopped")

# Create FastAPI application
app = FastAPI(
    title="Validator Gateway API",
    description="API for multi-agent collaboration with RDF knowledge graph validation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_gateway() -> ValidatorGateway:
    """Dependency to get the gateway instance."""
    if gateway is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gateway not initialized"
        )
    return gateway

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Validator Gateway API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "gateway_initialized": gateway is not None
    }

@app.post("/validate", response_model=ValidationResponse)
async def validate_staging_write(
    request: ValidationRequest,
    gateway: ValidatorGateway = Depends(get_gateway)
):
    """
    Validate a staging write request.
    
    This endpoint validates RDF data against SHACL shapes and runs
    forward-chaining reasoning to detect contradictions.
    """
    try:
        result = gateway.validate_staging_write(request)
        return result
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )

@app.post("/staging/write")
async def staging_write(
    request: StagingWriteRequest,
    gateway: ValidatorGateway = Depends(get_gateway)
):
    """
    Write data to staging graph.
    
    This endpoint allows agents to write data to their private staging graphs.
    """
    try:
        # Authenticate agent
        if not gateway.authenticate_agent(request.agent_id, "dummy_key"):  # Simplified auth
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
        
        # Convert to validation request and validate
        validation_request = ValidationRequest(
            agent_id=request.agent_id,
            session_id="default",  # Simplified session handling
            target_graph=request.staging_graph,
            rdf_payload=request.rdf_data,
            operation=request.operation
        )
        
        result = gateway.validate_staging_write(validation_request)
        
        if result.success:
            # Write to staging (simplified implementation)
            return {
                "success": True,
                "message": "Data written to staging",
                "staging_graph": request.staging_graph
            }
        else:
            return {
                "success": False,
                "message": "Validation failed",
                "errors": result.errors
            }
            
    except Exception as e:
        logger.error(f"Staging write error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Staging write failed: {str(e)}"
        )

@app.post("/commit", response_model=ValidationResponse)
async def commit_staging_data(
    request: CommitRequest,
    gateway: ValidatorGateway = Depends(get_gateway)
):
    """
    Commit validated staging data to consensus graph.
    
    This endpoint commits validated data from staging to the consensus graph.
    """
    try:
        result = gateway.commit_staging_data(request)
        return result
    except Exception as e:
        logger.error(f"Commit error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Commit failed: {str(e)}"
        )

@app.post("/query")
async def query_knowledge_graph(
    request: QueryRequest,
    gateway: ValidatorGateway = Depends(get_gateway)
):
    """
    Execute SPARQL query against the knowledge graph.
    
    This endpoint allows agents to query the knowledge graph using SPARQL.
    """
    try:
        result = gateway.query_knowledge_graph(request)
        return result
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}"
        )

@app.get("/metrics", response_model=MetricsData)
async def get_metrics(gateway: ValidatorGateway = Depends(get_gateway)):
    """Get gateway metrics."""
    return gateway.get_metrics()

@app.get("/alerts")
async def get_alerts(gateway: ValidatorGateway = Depends(get_gateway)):
    """Get current alerts."""
    return gateway.get_alerts()

@app.get("/provenance")
async def get_provenance(
    agent_id: str = None,
    gateway: ValidatorGateway = Depends(get_gateway)
):
    """Get provenance data."""
    return gateway.get_provenance(agent_id)

@app.post("/agents/register")
async def register_agent(
    agent_id: str,
    api_key: str,
    permissions: list = None,
    gateway: ValidatorGateway = Depends(get_gateway)
):
    """Register a new agent."""
    try:
        success = gateway.register_agent(agent_id, api_key, permissions)
        if success:
            return {"message": f"Agent {agent_id} registered successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agent registration failed"
            )
    except Exception as e:
        logger.error(f"Agent registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
