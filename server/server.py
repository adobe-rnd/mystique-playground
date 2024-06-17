import argparse
import threading
import time
import webbrowser

from server.toolbox import ToolboxServer
from server.assistant import AssistantServer
from server.proxy import ProxyServer


def main(url=None):
    # Initialize threads for the servers
    threads = []

    if url:
        threads.append(threading.Thread(target=ToolboxServer(url).run))
        threads.append(threading.Thread(target=ProxyServer(url).run))
    else:
        threads.append(threading.Thread(target=AssistantServer().run))

    # Start all threads
    for thread in threads:
        thread.start()

    # Open the web browser if URL is provided
    if url:
        webbrowser.open(f"http://localhost:4001?t={int(time.time())}")

    # Wait for all threads to complete
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the server")
    parser.add_argument('--url', type=str, help='URL for ProxyServer')
    args = parser.parse_args()

    main(args.url)
