"""
LangGraph-based Multi-Agent System for Tourism Domain

This module implements LLM-powered agents using LangGraph for the multi-agent
collaboration POC system.
"""

import logging
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from datetime import datetime
import asyncio

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

from ..ontology.tourism_ontology import TourismOntology
from ..ontology.shacl_shapes import TourismSHACLShapes
from ..ontology.reasoning_rules import TourismReasoningEngine
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

# Define agent state
class AgentState(TypedDict):
    """State for LangGraph agents."""
    messages: Annotated[List[BaseMessage], "List of messages in conversation"]
    current_agent: str
    session_id: str
    knowledge_graph: Dict[str, Any]
    derived_facts: List[Dict[str, Any]]
    contradictions: List[Dict[str, Any]]
    agent_memory: Dict[str, Any]

class TourismLangGraphAgents:
    """LangGraph-based multi-agent system for tourism domain."""
    
    def __init__(self, llm_provider: str = "openai", api_key: str = None):
        """
        Initialize LangGraph agents.
        
        Args:
            llm_provider: LLM provider ("openai" or "anthropic")
            api_key: API key for LLM provider
        """
        self.llm_provider = llm_provider
        self.api_key = api_key
        
        # Initialize LLM
        self.llm = self._setup_llm()
        
        # Initialize ontology components
        self.ontology = TourismOntology()
        self.shacl_shapes = TourismSHACLShapes()
        self.reasoning_engine = TourismReasoningEngine()
        
        # Agent configurations
        self.agents = {
            "ingest": self._create_ingest_agent(),
            "collect": self._create_collect_agent(),
            "reason": self._create_reason_agent()
        }
        
        # Create the main workflow
        self.workflow = self._create_workflow()
        
        logger.info("LangGraph agents initialized")
    
    def _setup_llm(self):
        """Setup LLM based on provider."""
        if self.llm_provider == "openai":
            return ChatOpenAI(
                model="gpt-4o-mini",
                api_key=self.api_key,
                temperature=0.1
            )
        elif self.llm_provider == "anthropic":
            return ChatAnthropic(
                model="claude-3-haiku-20240307",
                api_key=self.api_key,
                temperature=0.1
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def _create_ingest_agent(self):
        """Create the ingest agent with LangGraph."""
        
        @tool
        def parse_tourism_data(data: str) -> str:
            """Parse and normalize tourism data to RDF format."""
            try:
                # Use LLM to parse and structure data
                prompt = f"""
                Parse the following tourism data and convert it to RDF Turtle format.
                Use the tourism ontology with classes: City, CoastalCity, Attraction, etc.
                
                Data: {data}
                
                Return only the RDF Turtle format.
                """
                
                response = self.llm.invoke([HumanMessage(content=prompt)])
                return response.content
            except Exception as e:
                logger.error(f"Error parsing tourism data: {e}")
                return f"Error: {str(e)}"
        
        @tool
        def validate_rdf_data(rdf_data: str) -> str:
            """Validate RDF data using SHACL shapes."""
            try:
                from rdflib import Graph
                graph = Graph()
                graph.parse(data=rdf_data, format="turtle")
                
                # Run SHACL validation
                shacl_result = self.shacl_shapes.get_validation_report(graph)
                
                if shacl_result["conforms"]:
                    return "✅ RDF data is valid"
                else:
                    violations = shacl_result["violations"]
                    return f"❌ Validation failed: {len(violations)} violations found"
                    
            except Exception as e:
                return f"❌ Validation error: {str(e)}"
        
        def ingest_agent_node(state: AgentState) -> AgentState:
            """Ingest agent node."""
            messages = state["messages"]
            last_message = messages[-1]
            
            # Create system prompt for ingest agent
            system_prompt = """
            You are an Ingest Agent for a tourism knowledge graph system.
            Your role is to:
            1. Parse and normalize tourism data from various sources
            2. Convert data to RDF format using the tourism ontology
            3. Validate data quality using SHACL shapes
            4. Ensure data follows the tourism domain model
            
            Available tools:
            - parse_tourism_data: Parse raw data to RDF
            - validate_rdf_data: Validate RDF using SHACL
            
            Always provide structured RDF output and validation results.
            """
            
            # Create prompt with context
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}")
            ])
            
            # Get LLM response
            response = self.llm.invoke(prompt.format_messages(input=last_message.content))
            
            # Update state
            state["messages"].append(AIMessage(content=response.content))
            state["current_agent"] = "ingest"
            
            return state
        
        return ingest_agent_node
    
    def _create_collect_agent(self):
        """Create the collect agent with LangGraph."""
        
        @tool
        def enrich_attraction_data(attraction_uri: str, enrichment_data: str) -> str:
            """Enrich attraction data with additional information."""
            try:
                # Use LLM to structure enrichment data
                prompt = f"""
                Enrich the attraction {attraction_uri} with the following data:
                {enrichment_data}
                
                Return RDF Turtle format with the enrichment.
                """
                
                response = self.llm.invoke([HumanMessage(content=prompt)])
                return response.content
            except Exception as e:
                return f"Error: {str(e)}"
        
        @tool
        def detect_data_quality_issues(rdf_data: str) -> str:
            """Detect potential data quality issues."""
            try:
                from rdflib import Graph
                graph = Graph()
                graph.parse(data=rdf_data, format="turtle")
                
                # Check for common issues
                issues = []
                
                # Check for missing ratings
                query = """
                SELECT ?attraction WHERE {
                    ?attraction rdf:type tourism:Attraction .
                    FILTER NOT EXISTS { ?attraction tourism:hasRating ?rating }
                }
                """
                
                results = graph.query(query)
                if results:
                    issues.append("Missing ratings for attractions")
                
                # Check for missing amenities
                query = """
                SELECT ?attraction WHERE {
                    ?attraction rdf:type tourism:Attraction .
                    FILTER NOT EXISTS { ?attraction tourism:hasAmenity ?amenity }
                }
                """
                
                results = graph.query(query)
                if results:
                    issues.append("Missing amenities for attractions")
                
                if issues:
                    return f"⚠️ Data quality issues: {'; '.join(issues)}"
                else:
                    return "✅ Data quality looks good"
                    
            except Exception as e:
                return f"❌ Quality check error: {str(e)}"
        
        def collect_agent_node(state: AgentState) -> AgentState:
            """Collect agent node."""
            messages = state["messages"]
            last_message = messages[-1]
            
            system_prompt = """
            You are a Collect Agent for a tourism knowledge graph system.
            Your role is to:
            1. Enrich existing data with additional information
            2. Collect complementary facts about tourism entities
            3. Detect and report data quality issues
            4. Suggest improvements to the knowledge graph
            
            Available tools:
            - enrich_attraction_data: Add enrichment data
            - detect_data_quality_issues: Check data quality
            
            Focus on data enrichment and quality improvement.
            """
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}")
            ])
            
            response = self.llm.invoke(prompt.format_messages(input=last_message.content))
            
            state["messages"].append(AIMessage(content=response.content))
            state["current_agent"] = "collect"
            
            return state
        
        return collect_agent_node
    
    def _create_reason_agent(self):
        """Create the reason agent with LangGraph."""
        
        @tool
        def analyze_composite_destinations(knowledge_graph: Dict[str, Any]) -> str:
            """Analyze knowledge graph for composite destinations."""
            try:
                # Use reasoning engine to find composites
                from rdflib import Graph
                graph = Graph()
                
                # Build graph from knowledge_graph data
                for triple in knowledge_graph.get("triples", []):
                    graph.add(triple)
                
                # Run reasoning
                reasoning_result = self.reasoning_engine.run_reasoning(graph)
                
                composites = []
                for fact in reasoning_result["derived_facts"]:
                    if "CoastalFamilyDestination" in str(fact[2]):
                        composites.append(str(fact[0]))
                
                if composites:
                    return f"🎯 Found {len(composites)} composite destinations: {composites}"
                else:
                    return "No composite destinations found"
                    
            except Exception as e:
                return f"❌ Analysis error: {str(e)}"
        
        @tool
        def detect_contradictions(knowledge_graph: Dict[str, Any]) -> str:
            """Detect logical contradictions in the knowledge graph."""
            try:
                from rdflib import Graph
                graph = Graph()
                
                for triple in knowledge_graph.get("triples", []):
                    graph.add(triple)
                
                # Run contradiction detection
                reasoning_result = self.reasoning_engine.run_reasoning(graph)
                contradictions = reasoning_result["contradictions"]
                
                if contradictions:
                    return f"⚠️ Found {len(contradictions)} contradictions: {contradictions}"
                else:
                    return "✅ No contradictions detected"
                    
            except Exception as e:
                return f"❌ Contradiction detection error: {str(e)}"
        
        def reason_agent_node(state: AgentState) -> AgentState:
            """Reason agent node."""
            messages = state["messages"]
            last_message = messages[-1]
            
            system_prompt = """
            You are a Reason Agent for a tourism knowledge graph system.
            Your role is to:
            1. Analyze the knowledge graph for higher-level patterns
            2. Detect logical contradictions and inconsistencies
            3. Identify composite entities and relationships
            4. Provide insights and recommendations
            
            Available tools:
            - analyze_composite_destinations: Find composite entities
            - detect_contradictions: Check for logical conflicts
            
            Focus on reasoning, analysis, and insight generation.
            """
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}")
            ])
            
            response = self.llm.invoke(prompt.format_messages(input=last_message.content))
            
            state["messages"].append(AIMessage(content=response.content))
            state["current_agent"] = "reason"
            
            return state
        
        return reason_agent_node
    
    def _create_workflow(self):
        """Create the main LangGraph workflow."""
        
        # Create the workflow
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("ingest", self.agents["ingest"])
        workflow.add_node("collect", self.agents["collect"])
        workflow.add_node("reason", self.agents["reason"])
        
        # Add edges
        workflow.add_edge("ingest", "collect")
        workflow.add_edge("collect", "reason")
        workflow.add_edge("reason", END)
        
        # Set entry point
        workflow.set_entry_point("ingest")
        
        return workflow.compile()
    
    async def run_collaboration(self, initial_data: str, session_id: str = None) -> Dict[str, Any]:
        """
        Run the multi-agent collaboration workflow.
        
        Args:
            initial_data: Initial tourism data to process
            session_id: Session identifier
            
        Returns:
            Collaboration results
        """
        if session_id is None:
            session_id = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize state
        initial_state = AgentState(
            messages=[HumanMessage(content=initial_data)],
            current_agent="ingest",
            session_id=session_id,
            knowledge_graph={},
            derived_facts=[],
            contradictions=[],
            agent_memory={}
        )
        
        try:
            # Run the workflow
            result = await self.workflow.ainvoke(initial_state)
            
            # Extract results
            collaboration_result = {
                "session_id": session_id,
                "messages": [msg.content for msg in result["messages"]],
                "final_agent": result["current_agent"],
                "knowledge_graph": result["knowledge_graph"],
                "derived_facts": result["derived_facts"],
                "contradictions": result["contradictions"],
                "success": True
            }
            
            logger.info(f"Collaboration completed for session {session_id}")
            return collaboration_result
            
        except Exception as e:
            logger.error(f"Collaboration failed: {e}")
            return {
                "session_id": session_id,
                "error": str(e),
                "success": False
            }
    
    def run_sync_collaboration(self, initial_data: str, session_id: str = None) -> Dict[str, Any]:
        """Synchronous version of run_collaboration."""
        return asyncio.run(self.run_collaboration(initial_data, session_id))


def create_langgraph_agents(llm_provider: str = "openai", api_key: str = None) -> TourismLangGraphAgents:
    """Create LangGraph-based tourism agents."""
    return TourismLangGraphAgents(llm_provider, api_key)


if __name__ == "__main__":
    # Test the LangGraph agents
    import os
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        exit(1)
    
    # Create agents
    agents = create_langgraph_agents("openai", api_key)
    
    # Test data
    test_data = """
    Dubai is a coastal city in the UAE. The Dubai Aquarium is a major attraction 
    with a playground, rating 4.6, entry fee 25 AED.
    """
    
    # Run collaboration
    result = agents.run_sync_collaboration(test_data)
    print("Collaboration Result:")
    print(result)
