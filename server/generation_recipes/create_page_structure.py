from typing import List

from server.shared.llm import parse_markdown_output, LlmClient, ModelType


def create_page_structure(markdown_content: str, user_intent: str) -> str:
    prompt = f'''
        You are an experienced web developer with a strong background in content management and page structuring.
        
        Below is the markdown content of the page:
    
        {markdown_content}
    
        The goal is create the structure of the web page that aligns with the following user intent:
    
        {user_intent}
        
        The typical structure of the web page is:
        - Header
        - Navigation Bar
        - Hero Section or Banner or Carousel
        - Main Content Area with the list of sections
        - Sections may include:
            - Text
            - Cards
        - Footer

        Output format:
        - JSON with the structure of the web page
        - Each section should have: 
            - a type of component (e.g. header, footer, section, etc.)
            - content (e.g. text, image, etc.)
            - the list of child components (if any)
            - layout hints (if any)
            - styling hints (if any)
        '''
    client = LlmClient(model=ModelType.GPT_4_OMNI)
    llm_response = client.get_completions(prompt, temperature=0.0)

    return parse_markdown_output(llm_response, lang='json')
