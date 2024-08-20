from typing import List

from server.shared.llm import parse_markdown_output, LlmClient, ModelType


def create_page_narrative(markdown_contents: List[str], page_brief: str, user_intent: str) -> str:
    print("Creating page narrative...")
    print(f"Markdown contents: {markdown_contents}")
    print(f"User intent: {user_intent}")

    try:
        prompt = f'''
            You are an experienced copywriter tasked with creating a narrative for a new web page. 
            Your task is to create a compelling and engaging story that aligns with the user's intent and the provided content.
            
            Below is the markdown content extracted from various documents:
        
            {"\n\n".join(markdown_contents)}
        
            ### User Intent ### 
            {user_intent}
            
            ### Page Brief ###
            {page_brief}

            The goal is to craft a narrative that draws the user in and guides them through the content seamlessly. 
        
            Please ensure that:
            - The narrative is engaging and coherent
            - The story flows naturally and connects with the user's expectations
            - The tone and style match the content and intent
            - The narrative enhances the overall user experience
            - The narrative reflects the core message and values of the content
            
            Begin your response with the crafted narrative:
            '''
        client = LlmClient(model=ModelType.GPT_4_OMNI)
        page_narrative = client.get_completions(prompt, temperature=0.0)

        return page_narrative

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
