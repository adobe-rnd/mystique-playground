import argparse
import threading
import time
import webbrowser

from server.api import APIServer
from server.proxy import ProxyServer

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start API and Proxy Servers")
    parser.add_argument('--url', type=str, required=True, help='URL for the ProxyServer')
    args = parser.parse_args()
    url = args.url

    threads = [threading.Thread(target=APIServer(url).run),
               threading.Thread(target=ProxyServer(url).run)]

    for thread in threads:
        thread.start()

    webbrowser.open(f"http://localhost:4001?cacheBuster={int(time.time())}")

    for thread in threads:
        thread.join()
