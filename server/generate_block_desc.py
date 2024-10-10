#!/usr/bin/env python3
import argparse
import asyncio
import os
import requests
import sys

# Add the project root to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright
from server.shared.llm import LlmClient
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# def list_github_directory_structure(owner, repo, path='', token=''):
#     url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
#     headers = {'Authorization': f'token {token}'}
#     response = requests.get(url, headers=headers)
#
#     if response.status_code == 200:
#         contents = response.json()
#         for item in contents:
#             if item['type'] == 'dir':
#                 # print(f'{item["path"]}/')
#                 list_github_directory_structure(owner, repo, item['path'], token)
#             else:
#                 block_name = path.split('/')[-1]
#                 print(f'{block_name}')
#                 if '.css' in item['download_url']:
#                     block_css = requests.get(item['download_url'], headers=headers)
#                     if block_css.status_code == 200:
#                         block_html = get_block_html('../generated/page_cache.html', block_name)
#                         if block_html is None:
#                             continue
#                         generate_descriptions(block_name, block_html, block_css.text)
#                     else:
#                         print(f'Error reading file: {block_css.status_code}')
#             # break
#     else:
#         print(f'Error: {response.status_code}')

def list_github_directory_structure(owner, repo, path='', token=''):
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
    headers = {'Authorization': f'token {token}'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        contents = response.json()
        block_css = None
        block_js = None

        for item in contents:
            if item['type'] == 'dir':
                list_github_directory_structure(owner, repo, item['path'], token)
            else:
                block_name = path.split('/')[-1]
                print(f'{block_name}')

                if '.css' in item['download_url']:
                    block_css_response = requests.get(item['download_url'], headers=headers)
                    if block_css_response.status_code == 200:
                        block_css = block_css_response.text
                    else:
                        print(f'Error reading CSS file: {block_css_response.status_code}')

                if '.js' in item['download_url']:
                    block_js_response = requests.get(item['download_url'], headers=headers)
                    if block_js_response.status_code == 200:
                        block_js = block_js_response.text
                    else:
                        print(f'Error reading JS file: {block_js_response.status_code}')

                if block_css or block_js:
                    block_html = get_block_html('../generated/page_cache.html', block_name)
                    if block_html is None:
                        continue
                    generate_descriptions(block_name, block_html, block_js, block_css)
    else:
        print(f'Error: {response.status_code}')


# async def get_block_html(url, block_name):
#     with async_playwright() as p:
#         browser = await p.chromium.launch(headless=True)
#         page = await browser.new_page()
#
#         await page.goto(url)
#         await page.wait_for_load_state('networkidle')
#
#         # html_content = page.content()
#
#         # Print the fetched HTML content for debugging
#         # print(html_content)
#         outer_html = None
#
#         div = await page.query_selector(f'div[data-block-name="{block_name}"]')
#         if div:
#             outer_html = await div.evaluate('(element) => element.outerHTML')
#         else:
#             print(f'No div found with data-block-name="{block_name}"')
#
#         await browser.close()
#
#         return outer_html

async def cache_decorated_dom(url, filename):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Navigate to the URL
        await page.goto(url)
        await page.wait_for_load_state('networkidle')

        # Wait for the page to fully load, including dynamic content
        await page.wait_for_selector('body')  # Ensure the body is loaded

        # Extract the fully rendered HTML
        rendered_html = await page.content()

        # Save the HTML to a file
        with open(f'../generated/{filename}', 'w', encoding='utf-8') as f:
            f.write(rendered_html)

        print(f"Saved decorated DOM to {filename}")

        # Close the browser
        await browser.close()


def get_block_html(file_path, block_name):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    div = soup.find('div', {'data-block-name': block_name})

    if div is None:
        div = soup.find('ul', class_=lambda c: c and c.startswith(f'{block_name} block'))
        # div = soup.find(lambda tag: tag.has_attr('class') and any(c.startswith(f'{block_name} block') for c in tag['class']))

    if div:
        print(div.prettify())
    else:
        print(f'No div found with data-block-name="{block_name}"')
        return None

    return div


def generate_descriptions(block, html, js, css):
    js = js or ""

    system_prompt = f"""
        You are an expert frontend developer who has remarkable analytical skills.
    """
    llm = LlmClient(system_prompt=system_prompt)

    user_prompt = f"""
        Your main goal is to infer the purpose of the block and the type of content it can display from the decorated HTML, CSS and JS.
        Also, list only the variant classes (with their descriptions) that can be used to style the outer block differently.
        ---
        {html}
        ---
        {js}
        ---
        {css}
    """

    response = llm.get_completions(user_prompt)

    # Save the proposed changes
    with open(f'./block_descriptions/{block}_description.md', 'w') as f:
        f.write(response)


def main():
    parser = argparse.ArgumentParser(description='Process some URLs and GitHub repository details.')
    parser.add_argument('--repo', type=str, required=True, help='The GitHub repository name')
    parser.add_argument('--url', type=str, required=True, help='The URL to cache the decorated DOM from')
    parser.add_argument('--owner', type=str, default='hlxsites', help='The GitHub repository owner')

    args = parser.parse_args()
    load_dotenv()
    asyncio.run(cache_decorated_dom(args.url, 'page_cache.html'))

    list_github_directory_structure(args.owner, args.repo, path='blocks', token=os.getenv('GITHUB_TOKEN'))


if __name__ == "__main__":
    main()