from flask import Flask, Response, request, jsonify
import requests
from flask_cors import CORS
import traceback
import asyncio
import threading
import queue

from server.playground_db import PlaygroundDatabase
from server.generation_strategies.base_strategy import Action, StatusMessage
from server.playground_strategy_loader import load_generation_strategies

DASHBOARD_URL = "http://localhost:4010/playground.js"


class PlaygroundServer:
    def __init__(self, url):
        self.url = url
        self.app = Flask(__name__)
        CORS(self.app)

        self.injections = PlaygroundDatabase()
        self.generation_strategies = load_generation_strategies()

        self.setup_routes()

    def setup_routes(self):
        self.app.add_url_rule('/ok', view_func=self.ok, methods=['GET'])

        # Toolbox routes
        self.app.add_url_rule('/generate', view_func=self.generate, methods=['GET'])
        self.app.add_url_rule('/getStrategies', view_func=self.get_generation_strategies, methods=['GET'])

        # Proxy routes
        self.app.add_url_rule("/", defaults={'path': ''}, view_func=self.proxy, methods=['GET', 'POST'])
        self.app.add_url_rule("/<path:path>", view_func=self.proxy, methods=['GET', 'POST'])

    @staticmethod
    def ok():
        try:
            print("ok")
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def generate(self):
        selector = request.args.get('selector')
        generation_strategy = request.args.get('strategy')
        prompt = request.args.get('prompt')

        print(f"Selector: {selector}")
        print(f"Generation strategy: {generation_strategy}")
        print(f"Prompt: {prompt}")

        try:
            strategy_cls = next(filter(lambda s: s[0] == generation_strategy, self.generation_strategies))[3]
        except StopIteration:
            raise ValueError(f"Generation strategy with ID {generation_strategy} not found in the list.")

        status_queue = queue.Queue()

        strategy = strategy_cls()
        strategy.set_status_queue(status_queue)

        async def _generate_async():
            try:
                # Show the overlay
                strategy.run_javascript("showOverlay('Applying changes...');")

                await strategy.generate(self.url, selector, prompt=prompt or None)

                # Hide the overlay
                strategy.run_javascript_delayed("hideOverlay();", 6000)

                javascript_injections = strategy.get_javascript_injections()
                css_injections = strategy.get_css_injections()

                injections = []

                if javascript_injections:
                    injections.append("".join(javascript_injections))

                if css_injections:
                    injections.append(f'''
                        console.log("Adding CSS...");
                        const style = document.createElement('style');
                        style.innerHTML = `{''.join(css_injections)}`;
                        document.head.appendChild(style);
                    ''')

                if not injections:
                    injections.append('console.log("No injections to add.");')

                script_content = f'''
                    document.addEventListener('DOMContentLoaded', () => {{
                        {" ".join(injections)}
                    }});
                '''

                variation_id = self.injections.add_injection(script_content)
                status_queue.put(StatusMessage(Action.DONE, variation_id))

            except Exception as e:
                status_queue.put(StatusMessage(Action.ERROR, str(e)))
                print(e)
                print(traceback.format_exc())

        def _generate():
            asyncio.run(_generate_async())

        thread = threading.Thread(target=_generate)
        thread.start()

        def status_stream():
            while True:
                message = status_queue.get()
                if message.action == Action.DONE:
                    yield f"data: {message.to_json()}\n\n"
                    break
                yield f"data: {message.to_json()}\n\n"

        return Response(status_stream(), mimetype='text/event-stream')

    def get_generation_strategies(self):
        strategies = [
            {"id": id, "name": name, "category": category.value}
            for id, name, category, *_ in self.generation_strategies
        ]
        return jsonify(strategies)

    def proxy(self, path):
        variation_id = request.args.get('variationId')
        return self.handle_request(path, variation_id)

    def handle_request(self, path, variation_id):
        url = f"{self.url.rstrip('/')}/{path.lstrip('/')}"

        print(f"Proxying request to {url}")

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

        if 'text/html' in response.headers.get('Content-Type', ''):
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

    def run(self, host="0.0.0.0", port=4000):
        self.app.run(host=host, port=port, debug=True)
