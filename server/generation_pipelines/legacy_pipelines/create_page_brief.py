from typing import List

from server.shared.llm import parse_markdown_output, LlmClient, ModelType


def create_page_brief(markdown_contents: List[str], user_intent: str) -> str:
    print("Creating page brief...")
    print(f"User intent: {user_intent}")

    try:
        prompt = f'''
            You are an experienced copywriter tasked with creating a marketing brief for a new web page. 
            Your task is to create a concise and compelling overview that encapsulates the key elements of the content.
            
            Below is the markdown content extracted from various documents:
        
            {"\n\n".join(markdown_contents)}
        
            The goal is to craft a brief that highlights the main points and objectives of the content, aligning with the user's intent:
        
            {user_intent}
        
            Please ensure that:
            - The brief is clear, concise, and engaging 
            - The key features and benefits are emphasized
            - The tone and style are appropriate for the target audience
            - The brief captures the essence and purpose of the content
            - The brief sets the stage for the user's experience
            
            Begin your response with the crafted marketing brief:
            '''
        client = LlmClient(model=ModelType.GPT_4_OMNI)
        page_brief = client.get_completions(prompt, temperature=0.0)

        return page_brief

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
