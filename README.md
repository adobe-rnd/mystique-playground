# Mystique Playground

A playground and toolkit for the Mystique project.

## Setup

1. Create a `.env` file in the root directory with the following content:
   ```shell
   echo "AZURE_OPENAI_API_KEY=..." > .env
   echo "AZURE_OPENAI_ENDPOINT=https://openai-west-us-tsaplin.openai.azure.com/" >> .env
   ```

1. Create and activate a virtual environment:
    ```shell
    python3 -m venv venv
    source venv/bin/activate
    ```

1. Install the required packages:
    ```shell
    pip install -r requirements.txt
    cd ui && npm install
    ```

1. Build the dashboard overlay:
    ```shell
    ./build.sh
    ```

## Running the Application

To start the application, run the following command:

```shell
./start.sh https://main--wknd--hlxsites.hlx.page/
```

## Adding a New Generation Strategy

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
- **`add_css`**: To add CSS classes to the page.
- **`add_javascript`**: To add JavaScript code to the page.

