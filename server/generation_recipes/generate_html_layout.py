from server.component_templates import html_structure
from server.shared.llm import LlmClient, ModelType, parse_markdown_output


def generate_html_layout(markdown_content: str, inferred_css: str, user_intent: str) -> str:
    full_prompt = f'''
            You are a professional web developer tasked with transforming markdown content into a well-structured HTML page layout.
            The page must be composed only of the components defined in the given HTML structure and styled using the provided CSS.
            
            Ensure the layout aligns with the user's intent: {user_intent}.
            
            Convert the following markdown content into a well-structured HTML page layout with the given styles.
        
            CSS:
            
            {inferred_css}
    
            HTML Fragments to Use:
            
            {html_structure}
        
            Markdown Content:
            
            {markdown_content}
    
            '''
    print(full_prompt)
    client = LlmClient(model=ModelType.GPT_4_OMNI)
    llm_response = client.get_completions(full_prompt, temperature=0.0)
    print(llm_response)

    return parse_markdown_output(llm_response, lang='html')
