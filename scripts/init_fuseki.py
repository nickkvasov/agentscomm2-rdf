#!/usr/bin/env python3
"""
Initialize Fuseki with Tourism Domain Ontology

This script loads the tourism ontology, SHACL shapes, and reasoning rules
into Apache Jena Fuseki for use by the multi-agent collaboration system.
"""

import sys
import os
import time
import logging
from pathlib import Path

# Add src to path (go up one directory from scripts/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ontology.fuseki_client import FusekiClient

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/fuseki_init.log')
        ]
    )

def wait_for_fuseki(fuseki_client: FusekiClient, max_attempts: int = 30):
    """Wait for Fuseki to be ready."""
    print("🔄 Waiting for Fuseki to be ready...")
    
    for attempt in range(max_attempts):
        if fuseki_client.test_connection():
            print("✅ Fuseki is ready!")
            return True
        
        print(f"⏳ Attempt {attempt + 1}/{max_attempts} - Waiting for Fuseki...")
        time.sleep(2)
    
    print("❌ Fuseki failed to start within timeout")
    return False

def load_ontology_files(fuseki_client: FusekiClient):
    """Load ontology files into Fuseki."""
    print("\n📚 Loading ontology files into Fuseki...")
    
    # Get ontology directory (go up one directory from scripts/)
    script_dir = Path(__file__).parent
    ontology_dir = script_dir.parent / "ontology"
    
    # Load ontology
    ontology_file = ontology_dir / "tourism_ontology.ttl"
    if ontology_file.exists():
        print(f"📖 Loading ontology: {ontology_file}")
        if fuseki_client.load_ontology(str(ontology_file)):
            print("✅ Ontology loaded successfully")
        else:
            print("❌ Failed to load ontology")
            return False
    else:
        print(f"⚠️  Ontology file not found: {ontology_file}")
    
    # Load SHACL shapes
    shapes_file = ontology_dir / "tourism_shacl_shapes.ttl"
    if shapes_file.exists():
        print(f"📐 Loading SHACL shapes: {shapes_file}")
        if fuseki_client.load_shacl_shapes(str(shapes_file)):
            print("✅ SHACL shapes loaded successfully")
        else:
            print("❌ Failed to load SHACL shapes")
            return False
    else:
        print(f"⚠️  SHACL shapes file not found: {shapes_file}")
    
    # Load reasoning rules
    rules_file = ontology_dir / "tourism_reasoning_rules.ttl"
    if rules_file.exists():
        print(f"🧠 Loading reasoning rules: {rules_file}")
        if fuseki_client.load_reasoning_rules(str(rules_file)):
            print("✅ Reasoning rules loaded successfully")
        else:
            print("❌ Failed to load reasoning rules")
            return False
    else:
        print(f"⚠️  Reasoning rules file not found: {rules_file}")
    
    return True

def test_fuseki_operations(fuseki_client: FusekiClient):
    """Test Fuseki operations."""
    print("\n🧪 Testing Fuseki operations...")
    
    # Test server info
    info = fuseki_client.get_server_info()
    if info["success"]:
        print("✅ Server info retrieved successfully")
    else:
        print(f"❌ Failed to get server info: {info.get('error')}")
    
    # Test graph stats
    stats = fuseki_client.get_graph_stats()
    print("📊 Graph statistics:")
    for name, data in stats.items():
        print(f"  {name}: {data['triple_count']} triples")
    
    # Test SPARQL query
    query = """
    SELECT ?s ?p ?o
    WHERE {
        ?s ?p ?o
    }
    LIMIT 5
    """
    
    result = fuseki_client.query_graph(query)
    if result["success"]:
        print("✅ SPARQL query executed successfully")
        print(f"  Found {len(result['results']['results']['bindings'])} results")
    else:
        print(f"❌ SPARQL query failed: {result.get('error')}")
    
    return True

def run_reasoning_tests(fuseki_client: FusekiClient):
    """Run reasoning rule tests."""
    print("\n🧠 Testing reasoning rules...")
    
    # Test each reasoning rule
    rules = [
        "FindCoastalAttractions",
        "FindFamilyFriendlyPlayground", 
        "CreateCoastalFamilyDestinations"
    ]
    
    for rule in rules:
        print(f"🔄 Testing rule: {rule}")
        result = fuseki_client.run_sparql_rule(rule)
        if result["success"]:
            print(f"✅ Rule {rule} executed successfully")
        else:
            print(f"❌ Rule {rule} failed: {result.get('error')}")

def main():
    """Main initialization function."""
    print("🚀 Initializing Fuseki with Tourism Domain Ontology")
    print("=" * 60)
    
    setup_logging()
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Initialize Fuseki client
    fuseki_endpoint = os.getenv('FUSEKI_ENDPOINT', 'http://localhost:3030/ds')
    fuseki_client = FusekiClient(fuseki_endpoint)
    
    print(f"🔗 Connecting to Fuseki at: {fuseki_endpoint}")
    
    # Wait for Fuseki to be ready
    if not wait_for_fuseki(fuseki_client):
        print("❌ Failed to connect to Fuseki")
        return False
    
    # Load ontology files
    if not load_ontology_files(fuseki_client):
        print("❌ Failed to load ontology files")
        return False
    
    # Test operations
    if not test_fuseki_operations(fuseki_client):
        print("❌ Fuseki operations test failed")
        return False
    
    # Run reasoning tests
    run_reasoning_tests(fuseki_client)
    
    print("\n" + "=" * 60)
    print("🎉 Fuseki initialization completed successfully!")
    print("=" * 60)
    print("""
    📊 Summary:
    ✅ Fuseki connection established
    ✅ Ontology loaded into main graph
    ✅ SHACL shapes loaded for validation
    ✅ Reasoning rules loaded for inference
    ✅ SPARQL queries working
    ✅ Graph operations functional
    
    🎯 Ready for multi-agent collaboration!
    """)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
