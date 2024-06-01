from flask import Flask, Response, request
from flask_cors import CORS
from lib.llm import (get_text_and_image_completions, parse_markdown_output, create_prompt_from_template)
from lib.scraper import get_html_and_screenshot
import os
import asyncio
import nest_asyncio
import threading
import queue

nest_asyncio.apply()

app = Flask(__name__)
CORS(app)


def async_to_sync(func):
    """Helper function to run async functions in a synchronous context."""
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper


def generate_variations(original_url, preview_url, project_dir, selector, variation_index, status_queue):
    print(f"Generating variation {variation_index}...")
    """Function to generate variations of HTML and CSS"""
    os.makedirs(f"{project_dir}/generated", exist_ok=True)
    os.makedirs(f"{project_dir}/screenshots", exist_ok=True)

    async def async_task():
        status_queue.put('Getting the HTML and screenshot of the original page...')
        original_html, original_screenshot = await get_html_and_screenshot(original_url, selector)

        status_queue.put('Running the assessment...')
        goals = [
            "Improve conversion rate",
            "Make the styles more consistent with the brand",
            "Improve the overall look and feel of the form"
        ]
        assessment_prompt = create_prompt_from_template(
            "prompts/assessment.txt",
            goals=goals,
            html=original_html.strip()
        )
        instructions = get_text_and_image_completions(assessment_prompt, image_data=original_screenshot)
        status_queue.put(f"Instructions: {instructions}")

        status_queue.put('Generating CSS variation...')
        generation_prompt = create_prompt_from_template(
            "prompts/generation.txt",
            instructions=instructions,
            html=original_html.strip()
        )
        raw_output = get_text_and_image_completions(generation_prompt, image_data=original_screenshot)
        parsed_output = parse_markdown_output(raw_output)
        with open(project_dir + f'/generated/style{variation_index}.css', 'w') as text_file:
            text_file.write('\n'.join(parsed_output['css']))

        status_queue.put("Sleeping for 3 seconds...")
        await asyncio.sleep(2)

        status_queue.put('Getting the HTML and screenshot of the preview page...')
        generated_html, generated_screenshot = await get_html_and_screenshot(preview_url + '?toggleStyle' + str(variation_index), selector)
        with open(project_dir + f'/screenshots/preview{variation_index}.png', 'wb') as image_file:
            image_file.write(generated_screenshot)

        status_queue.put('Assessing the quality of the generated styles...')
        verification_prompt = create_prompt_from_template(
            "prompts/verification.txt",
            html=generated_html.strip()
        )
        adjustments = get_text_and_image_completions(verification_prompt, image_data=generated_screenshot)
        status_queue.put(f"Adjustments: {adjustments}")

        status_queue.put('Applying adjustments...')
        adjustment_prompt = create_prompt_from_template(
            "prompts/adjustment.txt",
            adjustments=adjustments,
            html=generated_html.strip()
        )
        raw_output = get_text_and_image_completions(adjustment_prompt, image_data=generated_screenshot)
        parsed_output = parse_markdown_output(raw_output)

        with open(project_dir + f'/generated/style{variation_index}.css', 'w') as text_file:
            text_file.write('\n'.join(parsed_output['css']))

        final_html, final_screenshot = await get_html_and_screenshot(preview_url + '?toggleStyle' + str(variation_index), selector)
        with open(project_dir + f'/screenshots/generated{variation_index}.png', 'wb') as image_file:
            image_file.write(final_screenshot)

        print(f"Variation {variation_index} generated.")

        status_queue.put("Done.")

    asyncio.run(async_task())


@app.route('/generate')
def generate():
    original_url = request.args.get('originalUrl')
    preview_url = request.args.get('previewUrl')
    project_dir = request.args.get('projectDir')
    selector = request.args.get('selector')
    variation_index = request.args.get('variationIndex')

    print(f"Original URL: {original_url}")
    print(f"Preview URL: {preview_url}")
    print(f"Project directory: {project_dir}")
    print(f"Selector: {selector}")
    print(f"Variation index: {variation_index}")

    status_queue = queue.Queue()

    thread = threading.Thread(target=generate_variations, args=(original_url, preview_url, project_dir, selector, variation_index, status_queue))
    thread.start()

    def status_stream():
        while True:
            message = status_queue.get()
            if message == "Done.":
                yield f"data: {message}\n\n"
                break
            yield f"data: {message}\n\n"

    return Response(status_stream(), mimetype='text/event-stream')


@app.route('/deleteGeneratedStyles')
def delete_generated_styles():
    project_dir = request.args.get('projectDir')
    os.system(f"rm -rf {project_dir}/generated")
    os.makedirs(f"{project_dir}/generated", exist_ok=True)
    return "Deleted generated styles."


if __name__ == '__main__':
    app.run(
        host="localhost",
        port=4000,
        debug=True,
        threaded=True
    )
