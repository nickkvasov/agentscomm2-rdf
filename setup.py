#!/usr/bin/env python3
"""
Setup script for Multi-Agent Collaboration POC

This script sets up the development environment and installs dependencies.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def setup_environment():
    """Setup the development environment."""
    print("🚀 Setting up Multi-Agent Collaboration POC Environment")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create virtual environment if it doesn't exist
    if not Path("venv").exists():
        print("📦 Creating virtual environment...")
        if not run_command("python3 -m venv venv", "Virtual environment creation"):
            return False
    else:
        print("✓ Virtual environment already exists")
    
    # Activate virtual environment and install dependencies
    print("📦 Installing dependencies...")
    
    # Determine the correct pip path
    if os.name == 'nt':  # Windows
        pip_path = "venv/Scripts/pip"
    else:  # Unix-like
        pip_path = "venv/bin/pip"
    
    # Upgrade pip
    if not run_command(f"{pip_path} install --upgrade pip", "Pip upgrade"):
        return False
    
    # Install requirements
    if not run_command(f"{pip_path} install -r requirements.txt", "Dependencies installation"):
        return False
    
    # Create necessary directories
    print("📁 Creating directory structure...")
    directories = [
        "data/main", "data/consensus", "data/staging", "data/quarantine",
        "logs", "reports", "src/ontology", "src/agents", "src/gateway", 
        "src/tests", "src/utils"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✓ Directory structure created")
    
    # Create __init__.py files
    init_files = [
        "src/__init__.py",
        "src/ontology/__init__.py", 
        "src/agents/__init__.py",
        "src/gateway/__init__.py",
        "src/tests/__init__.py",
        "src/utils/__init__.py"
    ]
    
    for init_file in init_files:
        Path(init_file).touch()
    
    print("✓ Python package structure created")
    
    return True

def verify_installation():
    """Verify that the installation is working."""
    print("\n🔍 Verifying installation...")
    
    # Test imports
    test_imports = [
        "rdflib",
        "pyshacl", 
        "fastapi",
        "uvicorn",
        "pydantic",
        "requests"
    ]
    
    for module in test_imports:
        try:
            __import__(module)
            print(f"✓ {module} imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import {module}: {e}")
            return False
    
    # Test ontology creation
    try:
        sys.path.insert(0, 'src')
        from ontology.tourism_ontology import TourismOntology
        from ontology.shacl_shapes import TourismSHACLShapes
        from ontology.reasoning_rules import TourismReasoningEngine
        
        ontology = TourismOntology()
        shapes = TourismSHACLShapes()
        engine = TourismReasoningEngine()
        
        print("✓ Core components imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to import core components: {e}")
        return False

def main():
    """Main setup function."""
    print("🎯 Multi-Agent Collaboration POC Setup")
    print("=" * 50)
    
    # Setup environment
    if not setup_environment():
        print("❌ Setup failed")
        return False
    
    # Verify installation
    if not verify_installation():
        print("❌ Installation verification failed")
        return False
    
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("""
    Next steps:
    
    1. Run the demo:
       python simple_demo.py
       
    2. Or run with Docker:
       ./docker-setup.sh
       
    3. Run tests:
       python src/tests/test_runner.py
       
    4. Start the gateway server:
       python src/gateway/main.py
    """)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
