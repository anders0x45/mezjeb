def main() -> None:
    """Entry point for mezjeb CLI."""
    import asyncio

    from .agent import Agent

    async def demo() -> None:
        agent = Agent(default_timeout=2.0, max_retries=2)
        try:
            result = await agent.execute_tool("normal_tool", {"param": "value"})
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")

    asyncio.run(demo())

