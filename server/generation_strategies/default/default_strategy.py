import asyncio

from server.generation_strategies.base_strategy import AbstractGenerationStrategy


class DefaultGenerationStrategy(AbstractGenerationStrategy):
    def id(self):
        return "default"

    def name(self):
        return "Default Generation Strategy"

    async def generate(self, status_queue, selector):
        print("Generating...")
        status_queue.put("Starting...")
        await asyncio.sleep(1)
        print("Generating...")
        status_queue.put("Generating...")
        await asyncio.sleep(1)
        status_queue.put("Done.")


        # print(f"Generating variation {variation_index}...")
        # """Function to generate variations of HTML and CSS"""
        # os.makedirs(f"{project_dir}/generated", exist_ok=True)
        # os.makedirs(f"{project_dir}/screenshots", exist_ok=True)

        # async def async_task():
        #     status_queue.put('Getting the HTML and screenshot of the original page...')
        #     original_html, original_screenshot = await get_html_and_screenshot(original_url, selector)
        #
        #     status_queue.put('Running the assessment...')
        #     goals = [
        #         "Improve conversion rate",
        #         "Make the styles more consistent with the brand",
        #         "Improve the overall look and feel of the form"
        #     ]
        #     assessment_prompt = create_prompt_from_template(
        #         "prompts/assessment.txt",
        #         goals=goals,
        #         html=original_html.strip()
        #     )
        #     instructions = get_text_and_image_completions(assessment_prompt, image_data=original_screenshot)
        #     status_queue.put(f"Instructions: {instructions}")
        #
        #     status_queue.put('Generating CSS variation...')
        #     generation_prompt = create_prompt_from_template(
        #         "prompts/generation.txt",
        #         instructions=instructions,
        #         html=original_html.strip()
        #     )
        #     raw_output = get_text_and_image_completions(generation_prompt, image_data=original_screenshot)
        #     parsed_output = parse_markdown_output(raw_output)
        #     with open(project_dir + f'/generated/style{variation_index}.css', 'w') as text_file:
        #         text_file.write('\n'.join(parsed_output['css']))
        #
        #     status_queue.put("Sleeping for 3 seconds...")
        #     await asyncio.sleep(2)
        #
        #     status_queue.put('Getting the HTML and screenshot of the preview page...')
        #     generated_html, generated_screenshot = await get_html_and_screenshot(preview_url + '?toggleStyle' + str(variation_index), selector)
        #     with open(project_dir + f'/screenshots/preview{variation_index}.png', 'wb') as image_file:
        #         image_file.write(generated_screenshot)
        #
        #     status_queue.put('Assessing the quality of the generated styles...')
        #     verification_prompt = create_prompt_from_template(
        #         "prompts/verification.txt",
        #         html=generated_html.strip()
        #     )
        #     adjustments = get_text_and_image_completions(verification_prompt, image_data=generated_screenshot)
        #     status_queue.put(f"Adjustments: {adjustments}")
        #
        #     status_queue.put('Applying adjustments...')
        #     adjustment_prompt = create_prompt_from_template(
        #         "prompts/adjustment.txt",
        #         adjustments=adjustments,
        #         html=generated_html.strip()
        #     )
        #     raw_output = get_text_and_image_completions(adjustment_prompt, image_data=generated_screenshot)
        #     parsed_output = parse_markdown_output(raw_output)
        #
        #     with open(project_dir + f'/generated/style{variation_index}.css', 'w') as text_file:
        #         text_file.write('\n'.join(parsed_output['css']))
        #
        #     final_html, final_screenshot = await get_html_and_screenshot(preview_url + '?toggleStyle' + str(variation_index), selector)
        #     with open(project_dir + f'/screenshots/generated{variation_index}.png', 'wb') as image_file:
        #         image_file.write(final_screenshot)
        #
        #     print(f"Variation {variation_index} generated.")
        #
        #     status_queue.put("Done.")

    def __init__(self):
        super().__init__()
