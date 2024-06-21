import asyncio

from server.generation_strategies.base_strategy import AbstractGenerationStrategy, StrategyCapability


class DefaultGenerationStrategy(AbstractGenerationStrategy):
    def id(self):
        return "example-strategy"

    def name(self):
        return "Example Strategy"

    def capabilities(self):
        return [StrategyCapability.GENERATOR]

    async def generate(self, url, selector, prompt):
        self.send_progress(f"Fetching {url}...")
        await asyncio.sleep(1)

        self.send_progress(f"Using selector {selector} to extract content...")
        await asyncio.sleep(1)

        self.run_javascript("console.log('Hello from DummyGenerationStrategy!');")
        self.add_css(f"{selector} {{ border: 10px solid red; }}")

        await asyncio.sleep(1)

    def __init__(self):
        super().__init__()
