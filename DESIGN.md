# Mezjeb Agent Design Document

## Overview
Mezjeb is an agentic workflow system designed to handle data import, processing, and export tasks with LLM-enhanced decision-making. The agent will provide a foundation for building data-centric workflows that can be extended with a frontend for visualization and interaction.

## Core Components

### 1. Agent Architecture
```
Mezjeb Agent Core
├── Data Integration Layer
│   ├── Importers (JSON, CSV, Excel)
│   └── Exporters (JSON, CSV, Excel)
├── Data Processing Layer
│   ├── Transformers (cleaning, filtering, aggregation)
│   └── Validators (schema, constraints)
├── Data Storage Layer
│   └── Session Database (SQLite, etc.)
├── LLM Reasoning Engine
│   ├── Prompt Templates
│   ├── Tool Use Framework
│   └── Context Management
├── Tool Orchestrator
│   ├── Async Task Scheduler
│   ├── Retry/Timeout Handler
│   └── State Manager
└── API Interface
    ├── CLI (current)
    └── Planned: REST/WebSocket for frontend
```

### 2. Data Integration Tools
- **Importers**:
  - JSON: Handle nested structures, streaming for large files
  - CSV: Dialect detection, chunked reading, type inference
  - Excel: Multiple sheet support, cell formatting preservation
- **Exporters**:
  - Same formats with configurable serialization options
  - Support for appending vs. overwriting
  - Compression options (gzip, zip)

### 3. Data Processing Tools
- **Transformers**:
  - Column operations (rename, drop, cast)
  - Row operations (filter, sample, sort)
  - Aggregations (groupby, pivot, window functions)
  - Data cleaning (deduplication, missing value handling)
  - Text processing (regex, tokenization)
- **Validators**:
  - Schema validation (JSON Schema, pandas DataFrame schemas)
  - Constraint checking (ranges, enums, regex patterns)
  - Custom validation rules

### 4. Data Storage Layer
- **Session Database**:
  - Lightweight database (SQLite by default) for storing intermediate data during a session
  - Decoupled from agent logic via repository pattern
  - Supports pluggable backends (SQLite, PostgreSQL, in-memory for testing)
  - Each session gets a unique database or schema
  - Tables for: raw imports, processed datasets, workflow metadata
- **Repository Pattern**:
  - Abstract base class for data access
  - Concrete implementations for each database type
  - Agent and tools depend on the abstraction, not concrete DB

### 5. LLM Integration
- **Tool Use Pattern**:
  - Agent exposes data tools as callable functions for the LLM
  - LLM decides which tools to use based on task description
  - Structured output parsing for reliable tool invocation
- **Context Management**:
  - Conversation history for multi-step workflows
  - Data summary/context passing between steps
  - Token-efficient data representation (schema + samples)
- **Prompt Engineering**:
  - Task-specific templates for data operations
  - Few-shot examples for common data tasks
  - Error handling and recovery prompts

### 5. Orchestration & Reliability
- **Async Execution**: Non-blocking I/O for file operations and LLM calls
- **Retry Mechanism**: Exponential backoff with jitter for transient failures
- **Timeouts**: Configurable per-operation timeouts
- **State Persistence**: Intermediate results saved to avoid reprocessing
- **Progress Reporting**: Structured logging and metrics

## POC Implementation Plan

### Phase 1: Foundation (Weeks 1-2)
1. **Data Integration Core**:
   - Implement JSON importer/exporter (using built-in `json`)
   - Implement CSV importer/exporter (using `pandas` or `csv` module)
   - Basic error handling and logging

2. **Data Storage Layer**:
   - Design repository pattern for data access
   - Implement SQLite backend for session storage
   - Create base classes for importers/exporters to use storage

3. **Agent Framework**:
   - Refine existing `Agent` class with better tool registration
   - Add async tool execution framework
   - Implement structured logging with correlation IDs

4. **LLM Interface**:
   - Create abstract LLM provider interface
   - Implement mock LLM for testing
   - Design tool calling schema

### Phase 2: Data Processing & Storage Integration (Weeks 3-4)
1. **Processing Toolkit**:
   - Implement core transformation functions (filter, map, aggregate)
   - Add data validation utilities
   - Create composable processing pipelines
   - Implement processing tools that read/write from session database

2. **Integration**:
   - Connect processing tools to agent tool registry
   - Implement data buffering via session database (not in memory)
   - Add performance profiling
   - Ensure tools use the storage repository abstraction

### Phase 3: LLM-Agent Loop (Weeks 5-6)
1. **Reasoning Engine**:
   - Implement prompt construction from task description
   - Create tool selection mechanism
   - Add output parsing and validation

2. **Workflow Execution**:
   - Implement multi-step task decomposition
   - Add state management for long-running workflows (using session database)
   - Create error recovery and retry logic
   - Store workflow steps and intermediate results in session database

### Phase 4: POC Validation (Week 7)
1. **Test Scenarios**:
   - Data cleaning pipeline (CSV -> clean -> CSV)
   - Data transformation (JSON -> aggregate -> Excel)
   - LLM-guided workflow (user describes goal, agent executes)

2. **Performance Benchmarks**:
   - Memory usage with large datasets
   - LLM token efficiency
   - Concurrent workflow handling

3. **Documentation & Examples**:
   - User guide for basic operations
   - Example workflows
   - API reference

## Technical Stack Decisions

### Core Libraries
- **Data Handling**: `pandas` (for its rich functionality) or `polars` (for performance)
- **Async**: Built-in `asyncio` with potential migration to `trio` or `anyio`
- **LLM Provider**: Abstract interface to support multiple backends (OpenAI, Anthropic, local)
- **Configuration**: `pydantic` for settings management
- **Logging**: `structlog` (already integrated)
- **Database**: `sqlite3` (built-in) for initial implementation, with SQLAlchemy ORM as optional abstraction layer

### File Format Support
- **JSON**: Standard library `json` + `orjson` for performance
- **CSV**: `pandas`/`csv` + `fastcsv` for large files
- **Excel**: `openpyxl` or `xlrd` (read) / `xlsxwriter` (write)

### Testing Strategy
- Unit tests for individual tools
- Integration tests for data pipelines
- Mock-based tests for LLM interactions
- Property-based testing for data transformations
- Database tests using temporary SQLite databases

## Extension Points
1. **Plugin System**: Dynamic tool registration
2. **Storage Backends**: Pluggable persistence (SQLite, PostgreSQL, S3, etc.)
3. **LLM Providers**: Easy swap of different language models
4. **Visualization Hooks**: Callbacks for frontend integration
5. **Security**: Pluggable authentication and encryption
6. **Database Abstraction**: Easy to swap storage backends via repository pattern

## Risks & Mitigations
- **LLM Cost/Performance**: Implement caching, batching, and fallback to rule-based
- **Data Privacy**: Ensure no data leaves system without explicit consent
- **Scalability**: Design for streaming and chunked processing
- **Complexity**: Keep core agent simple; complexity in tool implementations

## Code Snippets and Examples

### 1. Agent Tool Registration (in `src/mezjeb/agent.py`)
```python
# In the Agent class __init__ or a setup method
from .tools.data import JsonImporter, CsvImporter, DataFrameTransformer

class Agent:
    def __init__(self):
        self.tools = {
            "json_import": JsonImporter(),
            "csv_import": CsvImporter(),
            "transform_data": DataFrameTransformer(),
            # ... other tools
        }

    async def execute_tool(self, tool_name: str, tool_args: dict) -> Any:
        """Execute a registered tool by name."""
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")
        return await tool.execute(**tool_args)
```

### 2. JSON Importer Example (in `src/mezjeb/tools/data.py`)
```python
import json
from typing import Any, Dict
from pathlib import Path

class JsonImporter:
    async def execute(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Import JSON file and return as dictionary."""
        path = Path(file_path)
        with path.open('r') as f:
            data = json.load(f)
        # Optionally apply kwargs like 'jq'-style filtering
        return data

    # For large files, we might use a generator or chunked reading
    # but for simplicity, we load entirely here.
```

### 3. LLM Tool Use Example (in `src/mezjeb/llm/reasoning.py`)
```python
from typing import List, Dict
import json

class LlmReasoningEngine:
    def __init__(self, agent: Agent, llm_provider):
        self.agent = agent
        self.llm = llm_provider

    async def solve_task(self, task_description: str) -> Any:
        """Use LLM to decide which tools to run to accomplish the task."""
        # Step 1: Describe available tools to the LLM
        tools_description = self._get_tools_description()
        
        # Step 2: Construct prompt
        prompt = f"""
        Task: {task_description}
        
        Available tools:
        {tools_description}
        
        Respond with a JSON object specifying the tool to use and its arguments.
        Example: {{"tool": "json_import", "args": {{"file_path": "data.json"}}}}
        If you need multiple steps, return a list of such objects.
        """
        
        # Step 3: Get LLM response
        response = await self.llm.generate(prompt)
        plan = self._parse_llm_response(response)
        
        # Step 4: Execute the plan
        results = []
        for step in plan:
            tool_name = step["tool"]
            tool_args = step["args"]
            result = await self.agent.execute_tool(tool_name, tool_args)
            results.append(result)
            
            # Optionally update context for next step
            self._update_context(result)
        
        return results

    def _get_tools_description(self) -> str:
        # Generate a string description of each tool's purpose and args
        pass
    
    def _parse_llm_response(self, response: str) -> List[Dict]:
        # Parse the LLM's JSON output into a list of steps
        pass
```

### 4. Async Tool Execution with Retries (enhancing existing `agent.py`)
```python
# We already have retry logic in the agent, but here's how we might
# enhance it for data tools that might need specific retry conditions

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import asyncio

class Agent:
    # ... existing code ...

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((IOError, ValueError)),  # retry on file/value errors
    )
    async def execute_tool_with_retry(self, tool_name: str, tool_args: dict) -> Any:
        """Execute a tool with retry logic for transient errors."""
        return await self._execute_tool(tool_name, tool_args)

    async def _execute_tool(self, tool_name: str, tool_args: dict) -> Any:
        # Actual tool execution (calling the tool's execute method)
        tool = self.tools[tool_name]
        return await tool.execute(**tool_args)

    # The public execute_tool method would wrap the retry method with timeout
    async def execute_tool(self, tool_name: str, tool_args: dict, timeout: float = 30.0) -> Any:
        try:
            return await asyncio.wait_for(
                self.execute_tool_with_retry(tool_name, tool_args),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.error(f"Tool {tool_name} timed out after {timeout}s")
            raise TimeoutError(f"Tool execution exceeded {timeout}s")
```

### 5. Example Workflow: CSV to Cleaned JSON
```python
# This would be a test or example script showing how to use the agent
import asyncio
from mezjeb.agent import Agent
from mezjeb.llm.reasoning import LlmReasoningEngine
from mezjeb.llm.mock import MockLlmProvider  # for testing

async def main():
    agent = Agent()
    llm = MockLlmProvider()  # In production, use OpenAIProvider, etc.
    reasoning_engine = LlmReasoningEngine(agent, llm)
    
    # Task: "Load the CSV file at 'data/sales.csv', remove rows with missing values,
    # convert the 'amount' column to float, and save as JSON"
    result = await reasoning_engine.solve_task(
        "Load sales.csv, clean missing values, convert amount to float, save as cleaned_sales.json"
    )
    
    print("Workflow completed. Result:", result)

if __name__ == "__main__":
    asyncio.run(main())
```

## Where to Update Code Summary

| Feature                        | File to Modify                          | What to Add/Change                                                                 |
|--------------------------------|-----------------------------------------|------------------------------------------------------------------------------------|
| New Data Tool (importer/exporter) | `src/mezjeb/tools/data.py`             | Implement a new class with an `async execute` method                               |
| Agent Tool Registry            | `src/mezjeb/agent.py` (Agent.__init__)  | Add new tool instance to `self.tools` dictionary                                   |
| LLM Integration                | `src/mezjeb/llm/reasoning.py`          | Implement LlmReasoningEngine to interact with agent tools                          |
| Async Execution Enhancements   | `src/mezjeb/agent.py`                  | Refine retry/timeout logic if needed for specific tool types                       |
| Configuration                  | `src/mezjeb/config.py` (if created)    | Add settings for file paths, LLM parameters, etc.                                  |
| CLI Commands                   | `src/mezjeb/__init__.py` (main)        | Add commands to run agent with specific tasks                                      |

## Immediate Next Steps for Implementation
1. Create `src/mezjeb/tools/` directory and implement `JsonImporter` and `CsvImporter`
2. Update `src/mezjeb/agent.py` to register these tools in the Agent's `__init__`
3. Create a mock LLM provider (`src/mezjeb/llm/mock.py`) for testing
4. Implement basic LLM reasoning loop in `src/mezjeb/llm/reasoning.py`
5. Write a test scenario in `tests/test_workflow.py` for a CSV-to-JSON cleaning task

These code snippets illustrate exactly where and how to extend the current scaffold to support your data integration and LLM-agentic workflow requirements.