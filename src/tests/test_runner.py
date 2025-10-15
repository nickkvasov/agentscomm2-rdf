"""
Test Runner for Multi-Agent Collaboration POC

This module provides a simple test runner to execute all test scenarios
and generate reports.
"""

import sys
import os
import logging
import time
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from test_scenarios import TestScenarios

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test_results.log')
        ]
    )

def run_ontology_tests():
    """Run ontology and reasoning tests."""
    logger = logging.getLogger(__name__)
    logger.info("Running ontology and reasoning tests")
    
    try:
        from ontology.tourism_ontology import TourismOntology, create_sample_data
        from ontology.shacl_shapes import TourismSHACLShapes
        from ontology.reasoning_rules import TourismReasoningEngine
        
        # Test ontology creation
        ontology = TourismOntology()
        logger.info("✓ Tourism ontology created successfully")
        
        # Test SHACL shapes
        shapes = TourismSHACLShapes()
        logger.info("✓ SHACL shapes created successfully")
        
        # Test reasoning engine
        engine = TourismReasoningEngine()
        logger.info("✓ Reasoning engine created successfully")
        
        # Test with sample data
        sample_data = create_sample_data()
        reasoning_result = engine.run_reasoning(sample_data)
        
        logger.info(f"✓ Reasoning completed: {reasoning_result['iterations']} iterations")
        logger.info(f"✓ Derived facts: {len(reasoning_result['derived_facts'])}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Ontology tests failed: {e}")
        return False

def run_test_scenarios():
    """Run the main test scenarios."""
    logger = logging.getLogger(__name__)
    logger.info("Running POC test scenarios")
    
    try:
        test_scenarios = TestScenarios()
        results = test_scenarios.run_all_scenarios()
        
        # Generate report
        report = test_scenarios.generate_test_report()
        
        # Print results
        print("\n" + "="*60)
        print("MULTI-AGENT COLLABORATION POC - TEST RESULTS")
        print("="*60)
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Successful: {report['summary']['successful_tests']}")
        print(f"Failed: {report['summary']['failed_tests']}")
        print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        
        print("\nDetailed Results:")
        for test_name, result in report['test_results'].items():
            status = "✓ PASS" if result.get('success', False) else "✗ FAIL"
            print(f"  {test_name:25} {status}")
            
            if not result.get('success', False) and 'error' in result:
                print(f"    Error: {result['error']}")
        
        if report['recommendations']:
            print("\nRecommendations:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "="*60)
        
        return report['summary']['success_rate'] > 80  # 80% success rate threshold
        
    except Exception as e:
        logger.error(f"✗ Test scenarios failed: {e}")
        return False

def main():
    """Main test runner function."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Multi-Agent Collaboration POC Tests")
    logger.info("="*60)
    
    all_passed = True
    
    # Test 1: Ontology and Reasoning
    logger.info("\n1. Testing Ontology and Reasoning Components")
    logger.info("-" * 50)
    if not run_ontology_tests():
        all_passed = False
    
    # Test 2: POC Scenarios
    logger.info("\n2. Testing POC Scenarios")
    logger.info("-" * 50)
    if not run_test_scenarios():
        all_passed = False
    
    # Final results
    logger.info("\n" + "="*60)
    if all_passed:
        logger.info("✓ ALL TESTS PASSED - POC is ready for demonstration")
        print("\n🎉 SUCCESS: All tests passed! The POC system is ready.")
    else:
        logger.error("✗ SOME TESTS FAILED - Review and fix issues")
        print("\n❌ FAILURE: Some tests failed. Please review the results.")
    
    logger.info("="*60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
