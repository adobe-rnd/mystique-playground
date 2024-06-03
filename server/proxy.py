import os

import requests
from flask import Flask, request, Response

from server.db import JsCodeInjections

DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:4000/dashboard/index.js")


class ProxyServer:
    def __init__(self, target_url):
        self.site_name = target_url

        self.app = Flask(__name__ + "_proxy")
        self.setup_routes()

        self.injections = JsCodeInjections()

    def setup_routes(self):
        @self.app.route("/", defaults={'path': ''}, methods=['GET', 'POST'])
        @self.app.route("/<path:path>", methods=['GET', 'POST'])
        def proxy(path):
            variation_id = request.args.get('variationId')
            return self.handle_request(path, variation_id)

    def handle_request(self, path, variation_id):
        url = f"{self.site_name}/{path}"

        response = requests.request(
            method=request.method,
            url=url,
            headers={key: value for key, value in request.headers if key.lower() != 'host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )

        excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
        headers = [(name, value) for (name, value) in response.raw.headers.items() if name.lower() not in excluded_headers]

        content = response.content

        if path == "" and 'text/html' in response.headers.get('Content-Type', ''):
            if variation_id is not None:
                print(f"Injecting variation {variation_id}")
                injection = self.injections.get_injection_by_id(variation_id)
                if injection:
                    print("Injecting custom script")
                    content = content.replace(b'</head>', f'<script>{injection[1]}</script></head>'.encode('utf-8'))
            else:
                print("Injecting dashboard script")
                script = f'''
                <script>
                document.addEventListener('DOMContentLoaded', () => {{
                    const url = '{DASHBOARD_URL}';
                    const script = document.createElement('script');
                    script.src = url;
                    script.type = 'text/javascript';
                    script.async = true;
                    script.crossOrigin = 'anonymous';
                    document.head.appendChild(script);
                }});
                </script>
                '''
                content = content.replace(b'</head>', script.encode('utf-8') + b'</head>')

        response = Response(content, response.status_code, headers)
        return response

    def run(self, host="0.0.0.0", port=4001):
        self.app.run(host=host, port=port)
