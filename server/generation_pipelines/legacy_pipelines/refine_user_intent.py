from server.shared.llm import parse_markdown_output, LlmClient, ModelType


def refine_user_intent(user_intent: str) -> str:
    print("Refining user intent...")

    try:
        prompt = f'''
            Your task is to refine the user's intent with a more detailed and engaging description.
            Be creative and imaginative in your response, expanding on the user's initial intent:
            {user_intent}
            
            Begin your response with the enhanced user intent: 
            '''
        client = LlmClient(model=ModelType.GPT_4_OMNI)
        enhanced_user_intent = client.get_completions(prompt, temperature=1.0)

        return enhanced_user_intent

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
