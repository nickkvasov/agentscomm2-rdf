# LangGraph Multi-Agent Collaboration POC

This document describes the LangGraph-based implementation of the Multi-Agent Collaboration POC system with LLM integration.

## 🤖 LangGraph Architecture

The system uses LangGraph to orchestrate LLM-powered agents that collaborate through the RDF knowledge graph:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Ingest Agent   │    │  Collect Agent  │    │  Reason Agent   │
│  (LLM-powered)  │    │  (LLM-powered)  │    │  (LLM-powered)  │
│                 │    │                 │    │                 │
│ • Parse data    │───▶│ • Enrich data   │───▶│ • Analyze data  │
│ • Normalize RDF │    │ • Add ratings   │    │ • Detect patterns│
│ • Validate      │    │ • Add amenities │    │ • Find composites│
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                        ┌────────▼────────┐
                        │ Validator       │
                        │ Gateway         │
                        │                 │
                        │ • SHACL validation│
                        │ • Reasoning     │
                        │ • Consistency   │
                        │ • Commit control│
                        └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │ Apache Jena     │
                        │ Fuseki          │
                        │                 │
                        │ • SPARQL server │
                        │ • TDB2 storage  │
                        │ • Named graphs  │
                        └─────────────────┘
```

## 🧠 LLM Integration

### Supported Providers

- **OpenAI**: GPT-4o-mini (default)
- **Anthropic**: Claude-3-haiku

### Agent Capabilities

Each agent is powered by an LLM with specialized prompts and tools:

1. **Ingest Agent**:
   - Parses raw tourism data
   - Converts to RDF format
   - Validates using SHACL shapes
   - Uses tourism ontology

2. **Collect Agent**:
   - Enriches existing data
   - Detects data quality issues
   - Suggests improvements
   - Adds complementary facts

3. **Reason Agent**:
   - Analyzes knowledge graph patterns
   - Detects contradictions
   - Identifies composite entities
   - Provides insights

## 🚀 Quick Start

### Prerequisites

1. **API Keys**: Set one of the following:
   ```bash
   export OPENAI_API_KEY="your-openai-key"
   # OR
   export ANTHROPIC_API_KEY="your-anthropic-key"
   ```

2. **Dependencies**: Install LangGraph dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Demo

1. **LangGraph Demo**:
   ```bash
   python langgraph_demo.py
   ```

2. **Simple Demo** (without LLM):
   ```bash
   python simple_demo.py
   ```

3. **Docker Demo**:
   ```bash
   ./docker-setup.sh
   ```

## 🔧 Configuration

### Environment Variables

```bash
# LLM Provider Configuration
OPENAI_API_KEY="your-openai-key"
ANTHROPIC_API_KEY="your-anthropic-key"

# Fuseki Configuration
FUSEKI_ENDPOINT="http://localhost:3030/ds"

# Gateway Configuration
GATEWAY_HOST="localhost"
GATEWAY_PORT="8000"
```

### Agent Configuration

```python
# Create LangGraph agents
agents = create_langgraph_agents(
    llm_provider="openai",  # or "anthropic"
    api_key="your-api-key"
)

# Run collaboration
result = agents.run_sync_collaboration(
    initial_data="Dubai is a coastal city...",
    session_id="session_123"
)
```

## 📊 Agent Workflow

### 1. Ingest Agent

**Input**: Raw tourism data
**Process**: 
- Parse with LLM
- Convert to RDF
- Validate with SHACL
**Output**: Validated RDF data

### 2. Collect Agent

**Input**: Validated RDF data
**Process**:
- Enrich with additional facts
- Check data quality
- Suggest improvements
**Output**: Enriched RDF data

### 3. Reason Agent

**Input**: Enriched RDF data
**Process**:
- Analyze patterns
- Detect contradictions
- Find composite entities
**Output**: Insights and analysis

## 🛠️ Tools and Functions

### Ingest Agent Tools

- `parse_tourism_data(data)`: Parse raw data to RDF
- `validate_rdf_data(rdf_data)`: Validate RDF using SHACL

### Collect Agent Tools

- `enrich_attraction_data(uri, data)`: Enrich attraction data
- `detect_data_quality_issues(rdf_data)`: Check data quality

### Reason Agent Tools

- `analyze_composite_destinations(kg)`: Find composite entities
- `detect_contradictions(kg)`: Check for logical conflicts

## 📝 Example Usage

```python
from src.agents.langgraph_agents import create_langgraph_agents

# Create agents
agents = create_langgraph_agents("openai", "your-api-key")

# Test data
data = """
Dubai is a coastal city in the UAE. The Dubai Aquarium is a major attraction 
with a playground, rating 4.6, entry fee 25 AED.
"""

# Run collaboration
result = agents.run_sync_collaboration(data)

# Check results
if result["success"]:
    print(f"Messages: {result['messages']}")
    print(f"Derived Facts: {result['derived_facts']}")
    print(f"Contradictions: {result['contradictions']}")
```

## 🧪 Testing

### Test LangGraph Agents

```bash
python langgraph_demo.py
```

### Test Individual Components

```python
# Test LLM integration
from src.agents.langgraph_agents import TourismLangGraphAgents
agents = TourismLangGraphAgents("openai", "your-key")
response = agents.llm.invoke([{"role": "user", "content": "Hello"}])
```

### Test with Docker

```bash
# Set API keys in environment
export OPENAI_API_KEY="your-key"

# Run with Docker
docker-compose up --build -d
```

## 🔍 Monitoring and Debugging

### Logs

- **Application logs**: `logs/langgraph_demo.log`
- **Agent logs**: Check console output
- **LLM logs**: Enable debug logging

### Debugging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug logging
agents = create_langgraph_agents("openai", "your-key")
```

## 🚀 Production Deployment

### Environment Setup

1. **Set API keys**:
   ```bash
   export OPENAI_API_KEY="your-production-key"
   ```

2. **Configure Fuseki**:
   ```bash
   export FUSEKI_ENDPOINT="http://fuseki:3030/ds"
   ```

3. **Deploy with Docker**:
   ```bash
   docker-compose up --build -d
   ```

### Scaling

- **Multiple agents**: Run multiple agent instances
- **Load balancing**: Use multiple gateway instances
- **Caching**: Implement LLM response caching
- **Rate limiting**: Implement API rate limiting

## 📈 Performance Considerations

### LLM Costs

- **OpenAI**: ~$0.01 per 1K tokens
- **Anthropic**: ~$0.01 per 1K tokens
- **Optimization**: Use smaller models for simple tasks

### Latency

- **LLM calls**: 1-3 seconds per agent
- **Total workflow**: 5-10 seconds
- **Optimization**: Parallel processing, caching

### Memory

- **LangGraph state**: ~1MB per session
- **LLM context**: ~10MB per agent
- **Total**: ~50MB per active session

## 🎯 Next Steps

1. **Add more LLM providers** (Google, Cohere)
2. **Implement agent memory** for conversation history
3. **Add streaming responses** for real-time updates
4. **Implement agent specialization** for different domains
5. **Add human-in-the-loop** capabilities

The LangGraph implementation provides a powerful, LLM-powered multi-agent collaboration system that can be extended and scaled for production use! 🚀
