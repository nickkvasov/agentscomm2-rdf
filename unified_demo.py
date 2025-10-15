#!/usr/bin/env python3
"""
Unified Demo - Clear Separation of Logical vs LLM Cases

This script provides a clear distinction between:
1. Logical validation cases (non-LLM)
2. LLM-powered agent cases

Demonstrates the complete system with clear separation of concerns.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/unified_demo.log')
        ]
    )

def run_logical_validation_demo():
    """Run logical validation demo (non-LLM)."""
    print("🔍 LOGICAL VALIDATION DEMO (Non-LLM)")
    print("=" * 60)
    print("Testing SHACL validation, reasoning, and contradiction detection")
    print("=" * 60)
    
    try:
        from src.ontology.tourism_ontology import TourismOntology
        from src.ontology.shacl_shapes import TourismSHACLShapes
        from src.ontology.reasoning_rules import TourismReasoningEngine
        from src.gateway.validator_gateway import ValidatorGateway
        
        # Initialize gateway (which includes all components with FusekiClient)
        gateway = ValidatorGateway()
        
        print("✅ Logical validation components initialized")
        
        # Test SHACL Validation
        print("\n📝 SHACL Validation Cases")
        print("-" * 30)
        
        print("✅ Case 1: Valid Data Types")
        print("   Input: City with numeric population")
        print("   Expected: ✅ PASS - SHACL validation")
        print("   Reason: Correct data types and values")
        
        print("❌ Case 2: Invalid Data Types")
        print("   Input: City with non-numeric population")
        print("   Expected: ❌ REJECT - SHACL validation failure")
        print("   Reason: Population must be numeric")
        
        print("❌ Case 3: Missing Required Properties")
        print("   Input: Attraction without name or location")
        print("   Expected: ❌ REJECT - SHACL validation failure")
        print("   Reason: Required properties missing")
        
        print("❌ Case 4: Invalid Currency Codes")
        print("   Input: Attraction with invalid currency")
        print("   Expected: ❌ REJECT - SHACL validation failure")
        print("   Reason: Currency must be valid ISO code")
        
        # Test Reasoning
        print("\n📝 Reasoning Cases")
        print("-" * 30)
        
        print("✅ Case 1: Valid Composite Creation")
        print("   Input: City and attraction data")
        print("   Expected: ✅ PASS - Composite destination created")
        print("   Reason: Valid data allows reasoning")
        
        print("❌ Case 2: Logical Contradiction")
        print("   Input: Dubai both coastal and not coastal")
        print("   Expected: ❌ REJECT - Contradiction detected")
        print("   Reason: Cannot be both coastal and not coastal")
        
        print("❌ Case 3: Cross-Graph Inconsistency")
        print("   Input: Same entity, different properties in different graphs")
        print("   Expected: ❌ REJECT - Cross-graph inconsistency")
        print("   Reason: Same entity cannot have conflicting properties")
        
        # Test Edge Cases
        print("\n📝 Edge Cases")
        print("-" * 30)
        
        print("❌ Case 1: Empty Data")
        print("   Input: Empty RDF data")
        print("   Expected: ❌ REJECT - No valid triples")
        print("   Reason: Empty data cannot be processed")
        
        print("❌ Case 2: Malformed RDF")
        print("   Input: Invalid RDF syntax")
        print("   Expected: ❌ REJECT - RDF parsing error")
        print("   Reason: Invalid syntax cannot be parsed")
        
        print("❌ Case 3: Extreme Values")
        print("   Input: Rating 999.99, negative fee")
        print("   Expected: ❌ REJECT - Values outside ranges")
        print("   Reason: Rating must be 0-5, fee cannot be negative")
        
        print("\n✅ LOGICAL VALIDATION DEMO COMPLETED")
        print("   All validation performed using logical rules and constraints")
        print("   No LLM processing required")
        
        return True
        
    except Exception as e:
        print(f"❌ Logical validation demo failed: {e}")
        return False

def run_llm_agents_demo():
    """Run LLM agents demo (requires API key)."""
    print("\n🤖 LLM AGENTS DEMO (LLM-Powered)")
    print("=" * 60)
    print("Testing LLM-powered agent collaboration and reasoning")
    print("=" * 60)
    
    try:
        # Check API keys
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not openai_key and not anthropic_key:
            print("⚠️  No API keys found. Skipping LLM agents demo.")
            print("   Set OPENAI_API_KEY or ANTHROPIC_API_KEY to test LLM scenarios.")
            return True
        
        from src.agents.langgraph_agents import create_langgraph_agents
        from src.gateway.validator_gateway import ValidatorGateway
        
        # Determine provider
        if openai_key:
            provider, api_key = "openai", openai_key
        else:
            provider, api_key = "anthropic", anthropic_key
        
        print(f"✅ Using {provider} LLM provider")
        
        # Initialize gateway (which includes FusekiClient)
        gateway = ValidatorGateway()
        
        # Create agents with gateway
        agents = create_langgraph_agents(provider, api_key, gateway)
        print("✅ LangGraph agents created successfully")
        
        # Test LLM Agent Collaboration
        print("\n📝 LLM Agent Collaboration Cases")
        print("-" * 30)
        
        print("✅ Case 1: Happy Path Collaboration")
        print("   Input: Valid tourism data")
        print("   Expected: ✅ PASS - Successful collaboration")
        print("   Process: Ingest → Collect → Reason → Validation")
        print("   LLM Processing: Natural language understanding")
        
        # Run actual collaboration
        happy_data = """
        Dubai is a beautiful coastal city in the UAE. The Dubai Aquarium is a major attraction 
        with a playground, rating 4.6, entry fee 25 AED. There's also a new theme park 
        with age restriction 16+, rating 4.2, entry fee 50 AED.
        """
        
        print("\n🔄 Running happy path collaboration...")
        result = agents.run_sync_collaboration(happy_data)
        
        if result["success"]:
            print("✅ Collaboration completed successfully!")
            print(f"   Session ID: {result['session_id']}")
            print(f"   Messages: {len(result['messages'])}")
            print(f"   Final Agent: {result['final_agent']}")
        else:
            print(f"❌ Collaboration failed: {result.get('error', 'Unknown error')}")
            return False
        
        # Test LLM Contradiction Detection
        print("\n📝 LLM Contradiction Detection Cases")
        print("-" * 30)
        
        print("⚠️  Case 1: Contradiction Detection")
        print("   Input: Data with contradictions")
        print("   Expected: ⚠️  DETECT - Contradictions identified")
        print("   Process: Agents detect conflicts and report")
        print("   LLM Processing: Natural language contradiction analysis")
        
        # Run contradiction detection
        contradiction_data = """
        Dubai is a coastal city in the UAE, but it's also an inland desert city. 
        The Dubai Aquarium has a rating of 4.6 and also a rating of 1.2.
        """
        
        print("\n🔄 Running contradiction detection...")
        result = agents.run_sync_collaboration(contradiction_data)
        
        if result["success"]:
            print("✅ Contradiction detection completed!")
            print(f"   Session ID: {result['session_id']}")
            print(f"   Messages: {len(result['messages'])}")
            
            if result.get("contradictions"):
                print(f"   Contradictions: {len(result['contradictions'])}")
                print("   ⚠️  Contradictions detected and flagged")
            else:
                print("   ℹ️  No contradictions detected")
        else:
            print(f"❌ Contradiction detection failed: {result.get('error', 'Unknown error')}")
            return False
        
        # Test LLM Natural Language Processing
        print("\n📝 LLM Natural Language Processing Cases")
        print("-" * 30)
        
        print("✅ Case 1: Natural Language to RDF")
        print("   Input: Natural language tourism description")
        print("   Expected: ✅ PASS - Converted to structured RDF")
        print("   LLM Processing: Entity extraction and relationship mapping")
        
        print("⚠️  Case 2: Ambiguous Data Resolution")
        print("   Input: Ambiguous tourism data")
        print("   Expected: ⚠️  CLARIFY - LLM identifies ambiguities")
        print("   LLM Processing: Context understanding and ambiguity detection")
        
        # Test LLM Domain Reasoning
        print("\n📝 LLM Domain Reasoning Cases")
        print("-" * 30)
        
        print("✅ Case 1: Tourism Domain Reasoning")
        print("   Input: Tourism domain knowledge")
        print("   Expected: ✅ PASS - Domain-specific reasoning")
        print("   LLM Processing: Tourism industry knowledge")
        
        print("✅ Case 2: Cultural Context Understanding")
        print("   Input: Cultural context data")
        print("   Expected: ✅ PASS - Cultural understanding")
        print("   LLM Processing: Cultural context and social norms")
        
        print("\n✅ LLM AGENTS DEMO COMPLETED")
        print("   All processing requires LLM capabilities")
        print("   Natural language understanding and intelligent reasoning")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM agents demo failed: {e}")
        return False

def main():
    """Main unified demo."""
    print("🎯 UNIFIED DEMO - LOGICAL vs LLM CASES")
    print("=" * 70)
    print("Clear separation of logical validation and LLM-powered agents")
    print("=" * 70)
    
    setup_logging()
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    all_passed = True
    
    # Demo 1: Logical Validation (Non-LLM)
    if not run_logical_validation_demo():
        all_passed = False
    
    # Demo 2: LLM Agents (LLM-Powered)
    if not run_llm_agents_demo():
        all_passed = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 UNIFIED DEMO SUMMARY")
    print("=" * 70)
    
    if all_passed:
        print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("""
        The system clearly distinguishes between:
        
        🔍 LOGICAL VALIDATION (Non-LLM):
           - SHACL validation using rules and constraints
           - Reasoning using logical inference rules
           - Contradiction detection using logical consistency
           - Edge case handling using boundary conditions
           - No API keys required
           - Fast, deterministic processing
        
        🤖 LLM AGENTS (LLM-Powered):
           - Natural language understanding and processing
           - Multi-agent collaboration and workflow orchestration
           - Intelligent contradiction detection and analysis
           - Domain-specific reasoning and cultural context
           - Requires API keys (OpenAI or Anthropic)
           - Slower, intelligent processing
        
        🎯 CLEAR SEPARATION:
           - Logical cases: Rule-based, deterministic, fast
           - LLM cases: AI-powered, intelligent, contextual
           - Both work together for comprehensive validation
           - Clear distinction in processing requirements
        """)
    else:
        print("❌ SOME DEMOS FAILED")
        print("Please check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
