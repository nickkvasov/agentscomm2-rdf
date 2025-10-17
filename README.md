# Multi-Agent Collaboration POC

A proof-of-concept implementation of **intelligent agent collaboration** where AI agents work together to build and maintain a shared knowledge base, with automatic validation to ensure consistency and quality.

## 🤔 **The Problem**

### **Why Do We Need Multi-Agent Collaboration?**

Imagine you're building a tourism recommendation system. You have different AI agents that specialize in different tasks:

- **Agent A** finds and processes hotel information
- **Agent B** collects restaurant reviews and ratings  
- **Agent C** analyzes tourist attractions and amenities
- **Agent D** detects contradictions and inconsistencies

**The Challenge**: How do you make these agents work together without creating conflicts, contradictions, or duplicate information?

### **Real-World Scenarios**

#### **Scenario 1: Conflicting Information**
- Agent A says "Hotel X is family-friendly"
- Agent B says "Hotel X is not family-friendly"
- **Problem**: Which agent is correct? How do we resolve this?

#### **Scenario 2: Incomplete Data**
- Agent C finds a new restaurant but has no rating
- Agent D needs ratings to classify restaurants
- **Problem**: How do agents share information and build on each other's work?

#### **Scenario 3: Quality Control**
- Agent A processes 1000 hotels but some have invalid data
- Agent B adds ratings but some are outside valid ranges
- **Problem**: How do we ensure all data meets quality standards?

## 💡 **The Solution: Shared Knowledge Base with Validation**

### **Core Concept: Agents Share a Common "Brain"**

Instead of agents working in isolation, they all contribute to and read from a **shared knowledge base** (like a shared database that understands relationships and meaning).

```
🏗️ MULTI-AGENT COLLABORATION ARCHITECTURE
======================================================================

┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Agent A   │    │   Agent B   │    │   Agent C   │
│ (Hotels)    │    │(Restaurants)│    │(Attractions)│
│             │    │             │    │             │
│ • LLM       │    │ • LLM       │    │ • LLM       │
│ • Domain    │    │ • Domain    │    │ • Domain    │
│   Knowledge │    │   Knowledge │    │   Knowledge │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   STAGING   │    │   STAGING   │    │   STAGING   │
│   GRAPH A   │    │   GRAPH B   │    │   GRAPH C   │
│             │    │             │    │             │
│ • Agent's   │    │ • Agent's   │    │ • Agent's   │
│   proposed  │    │   proposed  │    │   proposed  │
│   changes   │    │   changes   │    │   changes   │
│ • Isolated  │    │ • Isolated  │    │ • Isolated  │
│   workspace │    │   workspace │    │   workspace │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       │                  │                  │
       │  ┌─────────────────────────────────────┐
       │  │        VALIDATOR GATEWAY            │
       │  │                                     │
       │  │ • Agent-level consistency checking  │
       │  │ • Multi-layer validation            │
       │  │ • Rollback mechanism                │
       │  └─────────────────────────────────────┘
       │                  │                  │
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│                CONSENSUS GRAPH                          │
│                                                         │
│ • Validated agent contributions                        │
│ • Agreed-upon knowledge                                │
│ • Pre-commit validation                               │
│ • Collaborative building                              │
└─────────────────────┬───────────────────────────────────┘
                      │
                      │  ┌─────────────────────────────────┐
                      │  │        VALIDATOR GATEWAY        │
                      │  │                                 │
                      │  │ • Consensus/main consistency    │
                      │  │ • Final validation              │
                      │  │ • Rollback if conflicts         │
                      │  └─────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  MAIN GRAPH                            │
│                                                         │
│ • Production knowledge base                            │
│ • All validated facts                                  │
│ • Complete relationships                                │
│ • Reasoning results                                     │
│ • Final authoritative data                             │
└─────────────────────────────────────────────────────────┘

📊 GRAPH LIFECYCLE:
======================================================================
1. STAGING: Agents create isolated workspaces with proposed changes
2. VALIDATION: Staging graphs are validated against consensus + main
3. CONSENSUS: Validated changes accumulate in consensus graph
4. INTEGRATION: Consensus graph is validated against main graph
5. COMMIT: Validated consensus data moves to main graph
6. REASONING: SWRL rules derive new insights in main graph
7. PUBLICATION: Updated knowledge is available to all agents
```

### **Architecture Components Explained**

#### **🤖 LLM Agents with Domain Knowledge**
- **Dynamic Ontology Access**: Each agent has comprehensive access to tourism domain knowledge
- **Precise Classification**: Agents use correct domain classes and properties
- **Context-Aware Processing**: Agents understand tourism domain relationships and constraints

#### **🔍 Validator Gateway (Central Control)**
The Validator Gateway is the **central orchestrator** that ensures data quality and consistency:

**Agent-Level Validation:**
- **Staging Isolation**: Each agent's proposed changes are validated in isolation
- **Consensus Integration**: Agent changes are validated against existing consensus data
- **Main Graph Integration**: Agent changes are validated against the main knowledge base
- **Contradiction Detection**: Detects conflicts between agent contributions

**Consensus/Main Validation:**
- **Pre-Commit Validation**: Consensus graph is validated against main graph before commit
- **Rollback Mechanism**: Failed validations trigger automatic rollback
- **Consistency Assurance**: Ensures consensus and main graphs remain consistent

#### **📊 Staging Graphs (Agent Isolation)**
- **Isolated Processing**: Each agent has its own staging graph for proposed changes
- **Safe Experimentation**: Agents can test changes without affecting others
- **Validation Testing**: Proposed changes are validated before moving to consensus
- **Conflict Prevention**: Isolated validation prevents agent conflicts

#### **🤝 Consensus Graph (Agreed Knowledge)**
- **Validated Contributions**: Contains agent contributions that passed validation
- **Pre-Commit State**: Intermediate state before final commit to main graph
- **Consistency Checking**: Validated against main graph for final consistency
- **Collaborative Building**: Represents agreed-upon knowledge from all agents

#### **🏛️ Main Graph (Production Knowledge)**
- **Authoritative Data**: The final, production knowledge base
- **Complete Relationships**: All validated facts and relationships
- **Reasoning Results**: Includes derived facts from SWRL reasoning
- **Agent Access**: All agents read from and contribute to this graph

### **Key Benefits**

1. **No Conflicts**: All agents see the same information
2. **Quality Control**: Every piece of data is validated before being added
3. **Automatic Reasoning**: The system can detect contradictions and create new insights
4. **Collaborative Intelligence**: Agents build on each other's work
5. **Isolation & Safety**: Agent changes are validated in isolation before integration
6. **Consistency Assurance**: Multi-layer validation ensures data consistency
7. **Rollback Protection**: Failed validations don't corrupt the knowledge base

## 🏗️ **How It Works: The Architecture**

### **Step 1: Agents Process Information with Domain Knowledge**

Each agent takes raw information and converts it into structured facts using comprehensive domain knowledge:

```
Raw Text: "Dubai Aquarium is a family-friendly attraction with a 4.6 rating"
         ↓
Domain-Aware Processing:
- Agent has access to tourism ontology (9 classes, 10 properties)
- Agent understands domain relationships and constraints
- Agent creates precise, domain-compliant RDF
         ↓
Structured Facts:
- tourism:DubaiAquarium rdf:type tourism:Attraction
- tourism:DubaiAquarium tourism:hasRating 4.6
- tourism:DubaiAquarium tourism:hasAmenity "Playground"
- tourism:DubaiAquarium tourism:locatedIn tourism:Dubai
- tourism:DubaiAquarium rdf:type tourism:FamilyFriendlyAttraction (derived)
```

### **Step 2: Multi-Layer Validation Flow**

#### **Layer 1: Agent-Level Validation (Staging)**
```
Agent A proposes changes → Staging Graph A
                        ↓
Validator Gateway:
1. Merge staging + consensus + main graphs
2. Check agent consistency
3. Validate against existing data
4. Detect contradictions
                        ↓
✅ Valid → Move to consensus
❌ Invalid → Reject with detailed feedback
```

#### **Layer 2: Consensus/Main Validation (Pre-Commit)**
```
Consensus Graph (validated agent contributions)
                        ↓
Validator Gateway:
1. Check consensus/main consistency
2. Final validation before commit
3. Rollback if conflicts detected
                        ↓
✅ Valid → Commit to main graph
❌ Invalid → Rollback consensus changes
```

#### **Layer 3: Final Integration (Main Graph)**
```
Main Graph (production knowledge base)
                        ↓
All agents see updated knowledge
Reasoning engine derives new insights
SHACL validation ensures quality
```

### **Step 3: Validation Details**

#### **Check 1: Data Quality (SHACL Validation)**
- Are ratings between 0-5?
- Are required fields present?
- Are data types correct?

#### **Check 2: Logical Consistency (SWRL Reasoning)**
- Does this create contradictions?
- Can we derive new insights?
- Are there conflicting facts?

#### **Check 3: Agent Consistency**
- Does this conflict with what other agents have added?
- Is this consistent with existing knowledge?

### **Step 3: Collaborative Intelligence**

The system automatically:
- **Detects Contradictions**: "Agent A says X is family-friendly, Agent B says X is not family-friendly"
- **Creates New Insights**: "If X is coastal and family-friendly, then X is a coastal family destination"
- **Maintains Quality**: Only valid, consistent information is kept

## 🔧 **Technical Implementation**

### **The Knowledge Base: RDF/OWL**

We use **RDF (Resource Description Framework)** - a standard way to represent knowledge that both humans and machines can understand:

```
Example RDF Facts:
- Dubai rdf:type City
- Dubai isCoastal true
- DubaiAquarium rdf:type Attraction
- DubaiAquarium locatedIn Dubai
- DubaiAquarium hasRating 4.6
```

### **Validation Rules: SHACL**

**SHACL (Shapes Constraint Language)** defines what "good data" looks like:

```
Example SHACL Rules:
- All attractions must have a name
- Ratings must be between 0 and 5
- Cities must have a country
- Entry fees must be positive numbers
```

### **Reasoning Rules: SWRL**

**SWRL (Semantic Web Rule Language)** defines logical relationships:

```
Example SWRL Rules:
- IF attraction has playground AND city is coastal 
  THEN attraction is coastal family destination

- IF attraction is family-friendly AND not family-friendly 
  THEN this is a contradiction
```

### **The Reasoning Engine: Apache Jena**

**Apache Jena** is a powerful reasoning engine that:
- Applies SWRL rules to find new insights
- Detects logical contradictions
- Maintains consistency across all data

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+
- Docker and Docker Compose
- OpenAI API key (for AI agents)

### **Setup and Run**
```bash
# 1. Set up environment
cp env.example .env
# Edit .env with your OpenAI API key

# 2. Start the system
docker-compose up -d

# 3. Initialize the knowledge base
python scripts/init_fuseki.py

# 4. Run the demo
python unified_demo.py
```

## 🧪 **Demo: See It In Action**

The demo shows two types of validation:

### **Logical Validation (No AI Required)**
- ✅ Valid data passes all checks
- ❌ Invalid data is rejected
- ❌ Contradictions are detected
- ❌ Missing information is flagged

### **AI Agent Collaboration**
- 🤖 Agents process natural language
- 🤖 Agents collaborate to build knowledge
- 🤖 Agents detect contradictions intelligently
- 🤖 Agents understand context and meaning

## 📊 **Real Results**

```
🎯 DEMO RESULTS
======================================================================

🔍 LOGICAL VALIDATION (Rule-Based)
============================================================
✅ Valid Data: "Hotel X has rating 4.5" → ACCEPTED
❌ Invalid Data: "Hotel X has rating 6.0" → REJECTED (rating > 5)
❌ Missing Data: "Hotel X" → REJECTED (no rating provided)
❌ Contradiction: "Hotel X is both family and not family-friendly" → REJECTED

🤖 AI AGENT COLLABORATION (LLM-Powered)
============================================================
✅ Natural Language: "Dubai Aquarium is great for families" 
   → Converted to structured facts
✅ Context Understanding: "This place is kid-friendly" 
   → Correctly identified as family-friendly
✅ Contradiction Detection: Agents identify conflicting information
✅ Collaborative Building: Agents build on each other's work
```

## 🧠 **Dynamic Domain Awareness: LLM Agents with Ontology Knowledge**

### **The Challenge: How Do AI Agents Understand Domain Knowledge?**

Traditional AI agents often work with **limited domain knowledge** - they might know basic concepts but lack deep understanding of the specific domain they're working in. This leads to:

#### **❌ Problems with Limited Domain Knowledge**
```
Agent: "I found a great place in Dubai"
System: "What type of place? Hotel? Restaurant? Attraction?"
Agent: "It's a tourist spot with good ratings"
System: "What kind of tourist spot? What amenities does it have?"
Agent: "It's family-friendly and near the coast"
System: "Is it a CoastalAttraction? FamilyFriendlyAttraction? Both?"
```

**Problems:**
- **Vague Descriptions**: Agents use generic terms instead of domain-specific concepts
- **Inconsistent Classification**: Different agents classify the same entity differently
- **Missing Relationships**: Agents don't understand how entities relate to each other
- **Poor RDF Generation**: Generated facts don't follow the domain schema
- **Validation Failures**: Created data doesn't pass domain validation

#### **✅ Our Solution: Dynamic Ontology Knowledge Extraction**

Our system provides LLM agents with **comprehensive, dynamic access to domain knowledge**:

```
🧠 AGENT DOMAIN AWARENESS
======================================================================

📊 ONTOLOGY KNOWLEDGE EXTRACTION
============================================================
✅ Classes: 9 tourism concepts
   - City, CoastalCity, Attraction, CoastalAttraction
   - FamilyFriendlyAttraction, NotFamilyFriendlyAttraction
   - CoastalFamilyDestination, Country, Contradiction

✅ Properties: 10 domain-specific attributes
   - Object Properties: locatedIn, inCountry
   - Datatype Properties: hasName, hasRating, hasAmenity, isCoastal
   - Financial: hasEntryFeeAmount, hasEntryFeeCurrency
   - Demographics: hasMinAge, population

✅ Relationships: Domain/range constraints
   - locatedIn domain: Attraction, range: City
   - hasRating domain: Attraction, range: decimal
   - isCoastal domain: City, range: boolean

✅ Namespace: http://example.org/tourism#
✅ Prefix: tourism
```

### **How Dynamic Domain Awareness Works**

#### **1. Automatic Ontology Extraction**
```python
def _extract_ontology_knowledge(self) -> Dict[str, Any]:
    """Extract comprehensive ontology knowledge for LLM agents."""
    # Extract classes from ontology graph
    classes = extract_classes_from_ontology()
    
    # Extract properties and relationships
    properties = extract_properties_from_ontology()
    relationships = extract_relationships_from_ontology()
    
    return {
        "classes": classes,
        "object_properties": properties["object"],
        "datatype_properties": properties["datatype"],
        "relationships": relationships,
        "namespace": "http://example.org/tourism#",
        "prefix": "tourism"
    }
```

#### **2. Enhanced LLM Prompts with Domain Knowledge**
```python
prompt = f"""
Parse the following tourism data and convert it to RDF Turtle format.

TOURISM ONTOLOGY KNOWLEDGE:
Classes: {', '.join(ontology_info['classes'])}
Object Properties: {', '.join(ontology_info['object_properties'])}
Datatype Properties: {', '.join(ontology_info['datatype_properties'])}
Relationships: {'; '.join(ontology_info['relationships'])}
Namespace: {ontology_info['namespace']}
Prefix: {ontology_info['prefix']}

Use the tourism ontology classes and properties listed above.
Create proper RDF triples with correct subject-predicate-object relationships.

Data: "Dubai is a coastal city with the Burj Khalifa attraction"

Return only the RDF Turtle format.
"""
```

#### **3. Domain-Aware RDF Generation**
**Before (Limited Knowledge):**
```
# Generic, vague RDF
tourism:Place1 rdf:type tourism:Entity .
tourism:Place1 tourism:hasProperty "good" .
tourism:Place1 tourism:hasLocation "Dubai" .
```

**After (Domain-Aware):**
```
# Precise, domain-compliant RDF
tourism:Dubai rdf:type tourism:CoastalCity .
tourism:Dubai tourism:hasName "Dubai" .
tourism:Dubai tourism:isCoastal true .

tourism:BurjKhalifa rdf:type tourism:Attraction .
tourism:BurjKhalifa tourism:hasName "Burj Khalifa" .
tourism:BurjKhalifa tourism:locatedIn tourism:Dubai .
tourism:BurjKhalifa tourism:hasRating 4.9 .
```

### **Key Benefits of Dynamic Domain Awareness**

#### **1. Precise Classification**
- **Correct Classes**: Agents use proper domain classes (CoastalCity, FamilyFriendlyAttraction)
- **Accurate Properties**: Agents use domain-specific properties (hasRating, isCoastal)
- **Valid Relationships**: Agents create correct subject-predicate-object triples

#### **2. Domain Compliance**
- **Schema Validation**: Generated RDF passes SHACL validation
- **Business Rules**: Agents follow tourism domain business logic
- **Consistency**: All agents use the same domain vocabulary

#### **3. Intelligent Understanding**
- **Context Awareness**: Agents understand tourism domain concepts
- **Relationship Recognition**: Agents see how entities relate to each other
- **Pattern Recognition**: Agents identify tourism patterns and trends

#### **4. Quality Assurance**
- **Validation Ready**: Generated data passes all domain validation
- **Consistency Maintained**: All agents use consistent domain terminology
- **Error Prevention**: Domain knowledge prevents common classification errors

### **Real-World Impact**

#### **Before: Generic AI Agents**
```
Input: "Dubai Aquarium is great for families"
Output: Generic RDF with vague classifications
Validation: ❌ Fails domain validation
Quality: ❌ Poor, inconsistent data
```

#### **After: Domain-Aware AI Agents**
```
Input: "Dubai Aquarium is great for families"
Output: Precise RDF using tourism ontology
- tourism:DubaiAquarium rdf:type tourism:Attraction
- tourism:DubaiAquarium tourism:hasAmenity "Playground"
- tourism:DubaiAquarium tourism:locatedIn tourism:Dubai
- tourism:DubaiAquarium rdf:type tourism:FamilyFriendlyAttraction (derived)

Validation: ✅ Passes all domain validation
Quality: ✅ High-quality, domain-compliant data
```

## 🔄 **Multi-Agent Collaboration: Facts-Only Communication**

### **The Key Innovation: Structured Communication**

Most multi-agent systems allow agents to communicate in **free text** (natural language), which creates several problems:

#### **❌ Problems with Free Text Communication**
```
Agent A: "I found a great hotel in Dubai, it's really nice and has good reviews"
Agent B: "What hotel? What reviews? How nice is 'really nice'?"
Agent C: "I also found a hotel, it's the best one, definitely recommend it"
Agent D: "Which hotel is better? How do I compare them?"
```

**Problems:**
- **Ambiguity**: "Great hotel" - which one? What makes it great?
- **Inconsistency**: Different agents use different terms
- **No Validation**: Can't check if information is accurate
- **No Reasoning**: Can't derive new insights from text
- **No Quality Control**: Can't ensure data standards

#### **✅ Our Solution: Facts-Only Communication**

Our system forces agents to communicate only through **structured facts**:

```
Agent A: 
- Hotel_DubaiMarina rdf:type Hotel
- Hotel_DubaiMarina hasRating 4.5
- Hotel_DubaiMarina hasAmenity "Pool"
- Hotel_DubaiMarina locatedIn Dubai

Agent B:
- Hotel_DubaiMarina hasAmenity "Spa"
- Hotel_DubaiMarina hasPrice 250.0
- Hotel_DubaiMarina hasPriceCurrency "USD"

System automatically detects:
- Hotel_DubaiMarina hasAmenity "Pool" AND "Spa"
- Hotel_DubaiMarina is LuxuryHotel (derived from amenities)
```

### **Why Facts-Only Communication Works Better**

#### **1. Unambiguous Information**
- **Clear Structure**: Every fact has a subject, predicate, and object
- **No Interpretation**: "Rating 4.5" is always 4.5, not "good" or "nice"
- **Precise Relationships**: "Hotel X hasAmenity Pool" is unambiguous

#### **2. Automatic Validation**
- **Data Quality**: Every fact is checked against rules
- **Consistency**: System detects conflicting facts automatically
- **Completeness**: Missing required information is flagged

#### **3. Automatic Reasoning**
- **New Insights**: System derives "LuxuryHotel" from amenities
- **Contradiction Detection**: System finds conflicting ratings
- **Pattern Recognition**: System identifies trends and relationships

#### **4. Collaborative Building**
- **Shared Understanding**: All agents see the same structured data
- **Incremental Knowledge**: Each agent adds specific facts
- **Quality Assurance**: Only validated facts are accepted

### **Comparison: Traditional vs Facts-Only**

| **Aspect** | **Traditional Multi-Agent** | **Facts-Only System** |
|------------|------------------------------|----------------------|
| **Communication** | Free text messages | Structured RDF facts |
| **Validation** | Manual review | Automatic validation |
| **Consistency** | Human oversight | Automatic detection |
| **Reasoning** | Limited | Full logical reasoning |
| **Quality** | Variable | Guaranteed standards |
| **Scalability** | Difficult | Easy to scale |

### **Real Example: Hotel Information**

#### **Traditional Approach (Free Text)**
```
Agent A: "Found a nice hotel in Dubai Marina, it's got a pool and spa, 
         rated 4.5 stars, costs around $250 per night"

Agent B: "I also found a hotel in Dubai Marina, it's excellent, 
         has great facilities, highly rated, expensive but worth it"

Agent C: "There's a luxury hotel in Dubai Marina, very expensive, 
         top-notch amenities, perfect for families"
```

**Problems:**
- Which hotel is which?
- What's the exact rating?
- What amenities does it have?
- How do we compare them?

#### **Facts-Only Approach (Structured)**
```
Agent A:
- Hotel_DubaiMarina rdf:type Hotel
- Hotel_DubaiMarina hasRating 4.5
- Hotel_DubaiMarina hasAmenity "Pool"
- Hotel_DubaiMarina hasAmenity "Spa"
- Hotel_DubaiMarina hasPrice 250.0
- Hotel_DubaiMarina hasPriceCurrency "USD"

Agent B:
- Hotel_DubaiMarina hasAmenity "Restaurant"
- Hotel_DubaiMarina hasAmenity "Gym"
- Hotel_DubaiMarina isFamilyFriendly true

Agent C:
- Hotel_DubaiMarina hasAmenity "Concierge"
- Hotel_DubaiMarina hasAmenity "Valet"
- Hotel_DubaiMarina isLuxuryHotel true
```

**Benefits:**
- **Clear Information**: Exact ratings, prices, amenities
- **Automatic Validation**: All facts checked for quality
- **Automatic Reasoning**: System derives "LuxuryHotel" from amenities
- **Collaborative Building**: Each agent adds specific information
- **Quality Assurance**: Only valid, consistent facts are kept

## 🎯 **Key Benefits of This Approach**

### **1. Quality Assurance**
- Every piece of information is validated
- Contradictions are automatically detected
- Data quality is maintained at all times

### **2. Collaborative Intelligence**
- Agents work together, not in isolation
- Each agent builds on others' work
- The whole system is smarter than individual agents

### **3. Automatic Reasoning**
- The system finds new insights automatically
- Relationships are discovered and maintained
- Complex patterns are detected

### **4. Dynamic Domain Awareness**
- **Comprehensive Knowledge**: Agents have full access to domain ontology
- **Precise Classification**: Agents use correct domain classes and properties
- **Schema Compliance**: Generated data passes all domain validation
- **Context Understanding**: Agents understand domain relationships and constraints

### **5. Scalability**
- Add new agents easily
- Add new types of information
- Scale to larger knowledge bases

### **6. Facts-Only Communication**
- **Unambiguous**: No interpretation needed
- **Validated**: Every fact is checked
- **Reasoned**: System derives new insights
- **Collaborative**: Agents build shared knowledge

## 🔧 **Technical Implementation: Dynamic Domain Awareness**

### **How It Works Under the Hood**

#### **1. Ontology Knowledge Extraction**
```python
def _extract_ontology_knowledge(self) -> Dict[str, Any]:
    """Extract comprehensive ontology knowledge for LLM agents."""
    ontology_graph = self.ontology.get_ontology_graph()
    
    # Extract classes from RDF/OWL ontology
    classes = []
    for s, p, o in ontology_graph.triples((None, RDF.type, OWL.Class)):
        if str(s).startswith("http://example.org/tourism#"):
            classes.append(str(s).split("#")[-1])
    
    # Extract properties and relationships
    object_properties = extract_object_properties(ontology_graph)
    datatype_properties = extract_datatype_properties(ontology_graph)
    relationships = extract_domain_range_relationships(ontology_graph)
    
    return {
        "classes": sorted(classes),
        "object_properties": sorted(object_properties),
        "datatype_properties": sorted(datatype_properties),
        "relationships": relationships,
        "namespace": "http://example.org/tourism#",
        "prefix": "tourism"
    }
```

#### **2. Enhanced LLM Prompt Generation**
```python
def _create_enhanced_prompt(self, data: str) -> str:
    """Create LLM prompt with comprehensive domain knowledge."""
    ontology_info = self.ontology_knowledge
    
    return f"""
    Parse the following tourism data and convert it to RDF Turtle format.
    
    TOURISM ONTOLOGY KNOWLEDGE:
    Classes: {', '.join(ontology_info['classes'])}
    Object Properties: {', '.join(ontology_info['object_properties'])}
    Datatype Properties: {', '.join(ontology_info['datatype_properties'])}
    Relationships: {'; '.join(ontology_info['relationships'])}
    Namespace: {ontology_info['namespace']}
    Prefix: {ontology_info['prefix']}
    
    Use the tourism ontology classes and properties listed above.
    Create proper RDF triples with correct subject-predicate-object relationships.
    
    Data: {data}
    
    Return only the RDF Turtle format.
    """
```

#### **3. Domain-Aware Validation**
```python
def validate_domain_compliance(self, rdf_data: str) -> bool:
    """Validate that generated RDF follows domain ontology."""
    # Parse generated RDF
    graph = Graph()
    graph.parse(data=rdf_data, format="turtle")
    
    # Check against SHACL shapes
    shacl_result = self.shacl_shapes.get_validation_report(graph)
    
    # Check against ontology constraints
    ontology_compliance = self._check_ontology_compliance(graph)
    
    return shacl_result["conforms"] and ontology_compliance
```

#### **4. Graph Lifecycle Management**

## 📊 **Graph Architecture: Staging → Consensus → Main**

### **Understanding the Three-Graph System**

Our multi-agent system uses a **three-graph architecture** to ensure data quality, consistency, and safe collaboration:

```
🔄 GRAPH LIFECYCLE
======================================================================

┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   STAGING   │    │  CONSENSUS  │    │    MAIN     │
│   GRAPHS    │───▶│    GRAPH    │───▶│    GRAPH    │
│             │    │             │    │             │
│ • Agent A   │    │ • Validated │    │ • Production│
│ • Agent B   │    │   changes   │    │   knowledge │
│ • Agent C   │    │ • Pre-commit│    │ • Final data│
│             │    │   state     │    │ • Reasoning │
└─────────────┘    └─────────────┘    └─────────────┘
```

### **📋 Staging Graphs: Agent Workspaces**

#### **Purpose**
- **Agent Isolation**: Each agent has its own private workspace
- **Safe Experimentation**: Agents can test changes without affecting others
- **Proposed Changes**: Contains agent's intended contributions
- **Validation Testing**: Changes are validated before moving forward

#### **Lifecycle**
```
1. CREATION
   Agent starts with empty staging graph
   ↓
2. POPULATION
   Agent processes data and adds proposed facts
   ↓
3. VALIDATION
   Staging graph is validated against consensus + main
   ↓
4. DECISION
   ✅ Valid → Move to consensus
   ❌ Invalid → Reject and provide feedback
   ↓
5. CLEANUP
   Staging graph is cleared for next iteration
```

#### **Example Staging Graph (Agent A)**
```turtle
# Agent A's proposed changes
tourism:NewHotel rdf:type tourism:Hotel .
tourism:NewHotel tourism:hasName "Marina Plaza" .
tourism:NewHotel tourism:hasRating 4.2 .
tourism:NewHotel tourism:locatedIn tourism:Dubai .
tourism:NewHotel tourism:hasAmenity "Pool" .
```

### **🤝 Consensus Graph: Agreed Knowledge**

#### **Purpose**
- **Validated Contributions**: Contains agent changes that passed validation
- **Pre-Commit State**: Intermediate state before final commit
- **Collaborative Building**: Represents agreed-upon knowledge from all agents
- **Consistency Checking**: Validated against main graph for final consistency

#### **Lifecycle**
```
1. ACCUMULATION
   Validated changes from multiple agents accumulate
   ↓
2. INTEGRATION
   Changes are integrated with existing consensus data
   ↓
3. VALIDATION
   Consensus graph is validated against main graph
   ↓
4. DECISION
   ✅ Valid → Commit to main graph
   ❌ Invalid → Rollback consensus changes
   ↓
5. COMMIT
   Validated consensus data moves to main graph
```

#### **Example Consensus Graph**
```turtle
# Accumulated validated changes from all agents
tourism:NewHotel rdf:type tourism:Hotel .
tourism:NewHotel tourism:hasName "Marina Plaza" .
tourism:NewHotel tourism:hasRating 4.2 .
tourism:NewHotel tourism:locatedIn tourism:Dubai .
tourism:NewHotel tourism:hasAmenity "Pool" .

tourism:NewRestaurant rdf:type tourism:Restaurant .
tourism:NewRestaurant tourism:hasName "Coastal Bistro" .
tourism:NewRestaurant tourism:hasRating 4.5 .
tourism:NewRestaurant tourism:locatedIn tourism:Dubai .

# Derived facts from reasoning
tourism:NewHotel rdf:type tourism:FamilyFriendlyHotel .
tourism:NewRestaurant rdf:type tourism:CoastalRestaurant .
```

### **🏛️ Main Graph: Production Knowledge**

#### **Purpose**
- **Authoritative Data**: The final, production knowledge base
- **Complete Relationships**: All validated facts and relationships
- **Reasoning Results**: Includes derived facts from SWRL reasoning
- **Agent Access**: All agents read from and contribute to this graph

#### **Lifecycle**
```
1. ACCEPTANCE
   Validated consensus data is accepted
   ↓
2. INTEGRATION
   New data is integrated with existing main graph
   ↓
3. REASONING
   SWRL rules are applied to derive new insights
   ↓
4. VALIDATION
   Final validation ensures no contradictions
   ↓
5. PUBLICATION
   Updated knowledge is available to all agents
```

#### **Example Main Graph**
```turtle
# Complete production knowledge base
tourism:NewHotel rdf:type tourism:Hotel .
tourism:NewHotel tourism:hasName "Marina Plaza" .
tourism:NewHotel tourism:hasRating 4.2 .
tourism:NewHotel tourism:locatedIn tourism:Dubai .
tourism:NewHotel tourism:hasAmenity "Pool" .
tourism:NewHotel rdf:type tourism:FamilyFriendlyHotel .

tourism:NewRestaurant rdf:type tourism:Restaurant .
tourism:NewRestaurant tourism:hasName "Coastal Bistro" .
tourism:NewRestaurant tourism:hasRating 4.5 .
tourism:NewRestaurant tourism:locatedIn tourism:Dubai .
tourism:NewRestaurant rdf:type tourism:CoastalRestaurant .

# All existing knowledge
tourism:Dubai rdf:type tourism:CoastalCity .
tourism:DubaiAquarium rdf:type tourism:Attraction .
tourism:DubaiAquarium tourism:locatedIn tourism:Dubai .
# ... (all other validated facts)
```

### **🔄 Complete Data Flow**

#### **Step 1: Agent Processing**
```
Raw Data → Agent with Domain Knowledge → Staging Graph
```

#### **Step 2: Staging Validation**
```
Staging Graph → Validator Gateway → Validation Result
```

#### **Step 3: Consensus Integration**
```
Valid Staging → Consensus Graph → Integration with Existing Data
```

#### **Step 4: Consensus Validation**
```
Consensus Graph → Validator Gateway → Final Validation
```

#### **Step 5: Main Graph Update**
```
Valid Consensus → Main Graph → Reasoning → Production Knowledge
```

### **Key Benefits of Three-Graph Architecture**

#### **1. Isolation & Safety**
- **Agent Independence**: Each agent works in isolation
- **Safe Experimentation**: Changes don't affect others until validated
- **Conflict Prevention**: Staging prevents agent conflicts

#### **2. Quality Assurance**
- **Multi-Layer Validation**: Data is validated at each stage
- **Consistency Checking**: Each graph is validated against others
- **Rollback Protection**: Failed validations don't corrupt production data

#### **3. Collaborative Intelligence**
- **Incremental Building**: Agents build knowledge incrementally
- **Shared Understanding**: All agents see the same final knowledge
- **Quality Control**: Only validated, consistent data reaches production

#### **4. Scalability**
- **Parallel Processing**: Multiple agents can work simultaneously
- **Efficient Validation**: Only changed data needs validation
- **Easy Rollback**: Failed changes can be easily reverted

### **Key Technical Features**

#### **1. Dynamic Knowledge Extraction**
- **Real-time Ontology Access**: Agents get live ontology knowledge
- **Automatic Updates**: Ontology changes automatically reflected in agent knowledge
- **Fallback Protection**: System works even if dynamic extraction fails

#### **2. Enhanced LLM Integration**
- **Context-Rich Prompts**: LLM prompts include full domain schema
- **Domain-Specific Instructions**: Agents receive domain-specific guidance
- **Validation Integration**: Generated data automatically validated

#### **3. Quality Assurance**
- **Multi-Layer Validation**: SHACL + ontology + reasoning validation
- **Consistency Checking**: Agents maintain domain consistency
- **Error Prevention**: Domain knowledge prevents common mistakes

## 🔮 **Future Possibilities**

This approach can be extended to many domains:

- **Healthcare**: Medical agents collaborating on patient data
- **Legal**: Legal agents analyzing contracts and regulations
- **Finance**: Financial agents monitoring markets and risks
- **Education**: Educational agents creating learning materials

## 📞 **Getting Started**

1. **Run the Demo**: See the system in action
2. **Explore the Code**: Understand how agents work
3. **Add Your Own Agents**: Create agents for your domain
4. **Extend the Knowledge Base**: Add new types of information

## 🎉 **Conclusion**

This system demonstrates how **AI agents can collaborate intelligently** while maintaining **data quality and consistency**. It's not just about individual AI agents - it's about creating a **collaborative intelligence system** where agents work together to build and maintain shared knowledge.

### **Key Innovations:**

1. **Dynamic Domain Awareness**: LLM agents have comprehensive access to domain ontology knowledge, enabling precise classification and domain-compliant data generation.

2. **Facts-Only Communication**: Agents communicate through structured facts rather than free text, ensuring unambiguous, validated, and reasoned information exchange.

3. **Multi-Layer Validation**: Every piece of information is validated through SHACL shapes, ontology constraints, and SWRL reasoning rules.

4. **Collaborative Intelligence**: Agents work together to build shared knowledge, with each agent contributing specific domain expertise while maintaining overall consistency.

The key insight: **Intelligent collaboration requires both AI capabilities AND rigorous validation** to ensure quality and consistency in the shared knowledge base. **Dynamic domain awareness** ensures that AI agents understand and work within the specific domain constraints, while **facts-only communication** ensures that all information exchange is precise, validated, and reasoned.

---

*This is a proof-of-concept that demonstrates the principles of multi-agent collaboration with shared knowledge bases. The technical implementation uses industry standards (RDF, OWL, SHACL, SWRL) and modern AI frameworks (LangGraph, OpenAI) to create a production-ready system.*