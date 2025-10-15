"""
Test scenarios for the multi-agent collaboration POC.

This module implements the test scenarios described in the POC document
to validate the system's functionality.
"""

from .test_scenarios import TestScenarios
from .test_happy_path import TestHappyPath
from .test_shape_rejection import TestShapeRejection
from .test_logic_contradiction import TestLogicContradiction
from .test_rescission import TestRescission
from .test_cross_graph_consistency import TestCrossGraphConsistency

__all__ = [
    'TestScenarios',
    'TestHappyPath', 
    'TestShapeRejection',
    'TestLogicContradiction',
    'TestRescission',
    'TestCrossGraphConsistency'
]
