# Mystique Playground

A playground and toolkit for the Mystique project.

## Configuration

1. Create a `.env` file in the root directory with the following content:
    ```shell
    AZURE_OPENAI_API_KEY=...
    AZURE_OPENAI_ENDPOINT=https://openai-west-us-tsaplin.openai.azure.com/
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

## Usage

To start the application, run the following command:

```shell
./start.sh https://main--wknd--hlxsites.hlx.page/
```

