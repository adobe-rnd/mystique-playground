from dataclasses import dataclass

from server.pipeline_step import PipelineStep
from typing import List
from server.shared.llm import LlmClient, ModelType

@dataclass
class StepResult:
    page_content: str

class GeneratePageContentStep(PipelineStep):
    @staticmethod
    def get_unique_id() -> str:
        return "generate_page_content"

    @staticmethod
    def get_name() -> str:
        return "Page Content"

    @staticmethod
    def get_description() -> str:
        return "Generates content for a web page based on the provided inputs."

    async def process(self, text_content: str, user_intent: str, **kwargs) -> StepResult:
        self.push_update("Creating page content...")

        try:
            prompt = f'''
                You are an experienced copywriter tasked with creating content for a new web page. 
                
                Craft content for a web page based on the following information:
                                 
                Text content:                                 
                {text_content}
            
                User intent:
                {user_intent}
            
                Begin your response with the crafted content for the web page.
                '''
            client = LlmClient(model=ModelType.GPT_4_OMNI)
            page_content = client.get_completions(prompt, temperature=0.0)

            return StepResult(page_content=page_content)

        except Exception as e:
            self.push_update(f"An error occurred: {e}")
            raise e
