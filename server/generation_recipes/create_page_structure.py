from typing import List

from server.shared.llm import parse_markdown_output, LlmClient, ModelType


def create_page_structure(markdown_contents: List[str], user_intent: str) -> str:
    prompt = f'''
        You are an experienced web developer with a strong background in content management and page structuring. 
        Your task is to merge markdown content from multiple sources into a cohesive and well-organized markdown document.
        
        Below is the markdown content extracted from various documents:
    
        {"\n\n".join(markdown_contents)}
    
        The goal is to combine this content into a single, logically structured markdown page that aligns with the following user intent:
    
        User Intent: {user_intent}
    
        Please ensure that the final document:
        - Maintains a clear and logical flow
        - Uses appropriate markdown headings to organize sections
        - Ensures consistency in formatting and style
        - Includes any necessary transitions to connect disparate sections smoothly
        - Preserves the original meaning and intent of each section
    
        Begin your response with the merged and structured markdown content:
        '''
    client = LlmClient(model=ModelType.GPT_4_OMNI)
    llm_response = client.get_completions(prompt, temperature=0.0)

    return parse_markdown_output(llm_response, lang='markdown')
