import argparse
import time

from server.playground_server import PlaygroundServer


def main(url):
    print("Starting Playground...")
    playground_server = PlaygroundServer(url)
    print(f"Proxying {url} at http://localhost:4000?t={int(time.time())}")
    playground_server.run(host='0.0.0.0', port=4000)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the Playground server")
    parser.add_argument('--url', type=str, required=True, help='URL of the website')
    args = parser.parse_args()

    print("Starting server...")
    main(args.url)
