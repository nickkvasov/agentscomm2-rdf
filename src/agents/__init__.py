"""
Agent implementations for the multi-agent collaboration system.

This module provides sample agent implementations that demonstrate
the POC requirements for agent collaboration through RDF knowledge graphs.
"""

from .base_agent import BaseAgent
from .ingest_agent import IngestAgent
from .collect_agent import CollectAgent
from .reason_agent import ReasonAgent

__all__ = ['BaseAgent', 'IngestAgent', 'CollectAgent', 'ReasonAgent']
