"""
Validator Gateway module for the multi-agent collaboration system.

This module provides the gateway service that validates and processes
agent requests before committing them to the knowledge graph.
"""

from .validator_gateway import ValidatorGateway
from .models import ValidationRequest, ValidationResponse, ValidationError

__all__ = ['ValidatorGateway', 'ValidationRequest', 'ValidationResponse', 'ValidationError']
