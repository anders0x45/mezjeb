# mezjeb

An agent project scaffolded with uv and ruff, featuring async tool execution with retries and timeouts, structured logging, and a pytest suite with a mocked LLM.

## Features

- Async tool execution using asyncio
- Retry logic with exponential backoff (tenacity)
- Timeout handling (asyncio.wait_for)
- Structured logging (structlog)
- Testing with pytest and mocked dependencies
- Modern Python tooling: uv, ruff, ty

## Installation

```bash
uv sync --all-groups
```

## Usage

```bash
uv run python -m mezjeb.agent
```

## Running Tests

```bash
uv run pytest
```