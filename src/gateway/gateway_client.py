"""
Gateway Client for interacting with the Validator Gateway API.

This client provides a Python interface to the FastAPI gateway service,
allowing local applications to use the gateway container instead of
direct local processing.
"""

import requests
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class GatewayResponse:
    """Response from gateway API."""
    success: bool
    data: Dict[str, Any]
    errors: list = None

class GatewayClient:
    """Client for interacting with the Validator Gateway API."""
    
    def __init__(self, gateway_url: str = "http://localhost:8000"):
        """Initialize the gateway client."""
        self.gateway_url = gateway_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> GatewayResponse:
        """Make a request to the gateway API."""
        url = f"{self.gateway_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            result = response.json()
            
            return GatewayResponse(
                success=True,
                data=result
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Gateway request failed: {e}")
            return GatewayResponse(
                success=False,
                data={},
                errors=[str(e)]
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return GatewayResponse(
                success=False,
                data={},
                errors=[str(e)]
            )
    
    def health_check(self) -> GatewayResponse:
        """Check gateway health."""
        return self._make_request('GET', '/health')
    
    def validate_staging_write(self, agent_id: str, session_id: str, 
                              target_graph: str, rdf_payload: str, 
                              operation: str = "write") -> GatewayResponse:
        """Validate a staging write request."""
        data = {
            "agent_id": agent_id,
            "session_id": session_id,
            "target_graph": target_graph,
            "rdf_payload": rdf_payload,
            "operation": operation
        }
        return self._make_request('POST', '/validate', data)
    
    def staging_write(self, agent_id: str, staging_graph: str, 
                     rdf_data: str, operation: str = "write") -> GatewayResponse:
        """Write data to staging graph."""
        data = {
            "agent_id": agent_id,
            "staging_graph": staging_graph,
            "rdf_data": rdf_data,
            "operation": operation
        }
        return self._make_request('POST', '/staging/write', data)
    
    def commit_staging_data(self, agent_id: str, session_id: str, 
                          staging_graph: str) -> GatewayResponse:
        """Commit staging data to consensus."""
        data = {
            "agent_id": agent_id,
            "session_id": session_id,
            "staging_graph": staging_graph
        }
        return self._make_request('POST', '/commit', data)
    
    def query_knowledge_graph(self, query: str, graph_uri: str = None) -> GatewayResponse:
        """Execute SPARQL query against knowledge graph."""
        data = {
            "query": query,
            "graph_uri": graph_uri
        }
        return self._make_request('POST', '/query', data)
    
    def get_metrics(self) -> GatewayResponse:
        """Get gateway metrics."""
        return self._make_request('GET', '/metrics')
    
    def get_alerts(self) -> GatewayResponse:
        """Get current alerts."""
        return self._make_request('GET', '/alerts')
    
    def get_provenance(self, agent_id: str = None) -> GatewayResponse:
        """Get provenance data."""
        endpoint = f"/provenance?agent_id={agent_id}" if agent_id else "/provenance"
        return self._make_request('GET', endpoint)
    
    def register_agent(self, agent_id: str, api_key: str, 
                      permissions: list = None) -> GatewayResponse:
        """Register a new agent."""
        data = {
            "agent_id": agent_id,
            "api_key": api_key,
            "permissions": permissions or []
        }
        return self._make_request('POST', '/agents/register', data)
    
    def is_available(self) -> bool:
        """Check if the gateway is available."""
        response = self.health_check()
        return response.success and response.data.get('status') == 'healthy'
