# Mystique Playground

A playground and toolkit for the Mystique project.

## Setup

1. Create a `.env` file in the root directory with the following content:
   ```shell
   echo "OPENAI_API_TYPE=azure # azure or openai" > .env
   echo "OPENAI_API_KEY=..." > .env
   echo "AZURE_OPENAI_API_KEY=..." > .env
   echo "AZURE_OPENAI_ENDPOINT=https://openai-west-us-tsaplin.openai.azure.com/" >> .env
   echo "AZURE_OPENAI_DALLE_API_KEY=..." >> .env
   echo "AZURE_OPENAI_DALLE_ENDPOINT=https://openai-east-us-tsaplin.openai.azure.com/" >> .env
   ```

1. Create a virtual environment:
    ```shell
    python3 -m venv venv
    source venv/bin/activate
    ```

1. Install the required packages:
    ```shell
    source venv/bin/activate
    pip install -r requirements.txt
    playwright install
    cd ui && npm install && cd ..
    ```

1. Install the Chrome extension (optional):
    - Open the Extension Management page by navigating to `chrome://extensions`.
    - Enable Developer Mode by clicking the toggle switch next to Developer mode.
    - Click the Load unpacked button and select the `ui` folder.

## Running the Application

To start the `Playground` tool, run the following command:

```shell
source venv/bin/activate
./start.sh https://main--wknd--hlxsites.hlx.page/
```

To use the `Copilot` tool, run the following command:

```shell
source venv/bin/activate
./start.sh
```

To start the `Web Creator` tool, run the following command:
```shell
source venv/bin/activate
./creator.sh
```

## Running tests

To run the tests, execute the following command:

```shell
source venv/bin/activate
python -m unittest discover -s server/tests
```

## Adding a New Generation Strategy to the Playground

To create a new generation strategy, follow these steps:

1. **Create a New Python Class**: This class should extend `AbstractGenerationStrategy`.
2. **Make the Strategy Discoverable**: Place the new class anywhere in the `server/generation_strategies` folder or a subfolder within it.

#### Required Methods

You need to implement three methods in your class:

- **`id`**: A unique identifier for the strategy.
- **`name`**: A human-readable name that will be displayed in the UI.
- **`generate`**: The method where the new content will be generated.

#### The `generate` Method

The `generate` method accepts two arguments:

- **`url`**: The URL of the website.
- **`selector`**: The CSS selector of the block.

#### Useful Methods from the Base Class

You can use the following methods from the base class to enhance your strategy:

- **`send_progress`**: To send a status update to the UI.
- **`replace_html`**: To replace the HTML content of the page.
- **`add_css`**: To add CSS classes to the page.
- **`run_javascript`**: To add JavaScript code to the page.
- **`run_javascript_when_selector_available`**: To run JavaScript code when the selector is available.

#### Useful Utilities 

To interact with the LLM, render pages, and capture screenshots, use the functions available in `llm.py` and `scraper.py`.
