"""Agent module demonstrating async tool execution with retries, timeouts, and structured logging."""

import asyncio
import builtins
import logging
from typing import Any

import structlog
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .tools.json_integration import JsonIntegration

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)

logger = structlog.get_logger()


class ToolExecutionError(Exception):
    """Raised when a tool fails after retries."""


class TimeoutError(Exception):
    """Raised when a tool execution exceeds timeout."""


class Agent:
    """An agent that can execute tools asynchronously with retries and timeouts."""

    def __init__(self, default_timeout: float = 30.0, max_retries: int = 3):
        self.tools = {
            "json_integration": JsonIntegration(),
            # ... other tools
        }
        self.default_timeout = default_timeout
        self.max_retries = max_retries

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ToolExecutionError, asyncio.TimeoutError)),
    )
    async def execute_tool_with_retry(self, tool_name: str, tool_args: dict[str, Any]) -> Any:
        """Execute a tool with retry logic.
        
        This method is decorated with tenacity retry.
        """
        logger.info("Executing tool", tool=tool_name, args=tool_args)
        # Simulate tool execution; replace with actual tool call
        result = await self._execute_tool(tool_name, tool_args)
        logger.info("Tool executed successfully", tool=tool_name, result=result)
        return result

    async def _execute_tool(self, tool_name: str, tool_args: dict[str, Any]) -> Any:
        """Internal tool execution that may raise exceptions."""
        # Example: simulate a tool that sometimes fails
        if tool_name == "failing_tool":
            raise ToolExecutionError("Simulated tool failure")
        # Simulate a timeout
        if tool_name == "slow_tool":
            await asyncio.sleep(5)  # longer than default timeout
            return "slow tool result"
        # Normal tool
        await asyncio.sleep(0.1)
        return f"Result from {tool_name} with args {tool_args}"

    async def execute_tool(
        self, tool_name: str, tool_args: dict[str, Any] | None = None, timeout: float | None = None
    ) -> Any:
        """Execute a tool with timeout and retry logic.
        
        Args:
            tool_name: Name of the tool to execute.
            tool_args: Arguments to pass to the tool.
            timeout: Override default timeout.
            
        Returns:
            Tool result.
            
        Raises:
            ToolExecutionError: If tool fails after retries.
            asyncio.TimeoutError: If tool execution exceeds timeout.
        """
        if tool_args is None:
            tool_args = {}
        timeout = timeout if timeout is not None else self.default_timeout

        try:
            # Wrap the retry-enabled method with timeout
            return await asyncio.wait_for(
                self.execute_tool_with_retry(tool_name, tool_args),
                timeout=timeout,
            )
        except builtins.TimeoutError:
            logger.error("Tool execution timed out", tool=tool_name, timeout=timeout)
            raise TimeoutError(f"Tool {tool_name} exceeded timeout of {timeout}s") from None
        except ToolExecutionError as e:
            logger.error("Tool execution failed after retries", tool=tool_name, error=str(e))
            raise


# Example usage
async def main() -> None:
    agent = Agent(default_timeout=2.0, max_retries=2)
    try:
        result = await agent.execute_tool("normal_tool", {"param": "value"})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

    try:
        result = await agent.execute_tool("failing_tool", {})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

    try:
        result = await agent.execute_tool("slow_tool", {}, timeout=10.0)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
