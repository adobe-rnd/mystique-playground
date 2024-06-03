import asyncio
import os

from flask import Flask, Response, request, jsonify, make_response, send_from_directory
import threading
import queue

from flask_cors import CORS

from server.db import JsCodeInjections
from server.generation_strategies.base_strategy import Action, StatusMessage
from server.strategy_loader import load_generation_strategies


class APIServer:
    def __init__(self, target_url):
        self.target_url = target_url

        self.generation_strategies = load_generation_strategies()

        self.app = Flask(__name__)
        self._register_routes()
        CORS(self.app)

        self.injections = JsCodeInjections()

    def _register_routes(self):
        self.app.add_url_rule('/dashboard/<path:filename>', view_func=self.dashboard)
        self.app.add_url_rule('/generate', view_func=self.generate)
        self.app.add_url_rule('/getStrategies', view_func=self.get_generation_strategies)

    def generate(self):
        selector = request.args.get('selector')
        generation_strategy = request.args.get('strategy')

        print(f"Selector: {selector}")
        print(f"Generation strategy: {generation_strategy}")

        try:
            strategy_cls = next(filter(lambda s: s[0] == generation_strategy, self.generation_strategies))[2]
        except StopIteration:
            raise ValueError(f"Generation strategy with ID {generation_strategy} not found in the list.")

        status_queue = queue.Queue()

        strategy = strategy_cls()

        strategy.set_status_queue(status_queue)

        async def _generate_async():

            try:
                await strategy.generate(self.target_url, selector)

                javascript_injections = strategy.get_javascript_injections()
                css_injections = strategy.get_css_injections()

                variation_id = self.injections.add_injection(f'''
                    document.addEventListener('DOMContentLoaded', () => {{
                        {"".join(javascript_injections)}
                        const style = document.createElement('style');
                        style.innerHTML = `{"".join(css_injections)}`;
                        document.head.appendChild(style);
                    }});
                ''')

                status_queue.put(StatusMessage(Action.DONE, variation_id))

            except Exception as e:
                status_queue.put(StatusMessage(Action.ERROR, str(e)))

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
        return [
            {"id": id, "name": name}
            for id, name, _ in self.generation_strategies
        ]

    def dashboard(self, filename):
        static_files_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ui', 'dist'))
        return send_from_directory(static_files_path, filename)

    def run(self, host="0.0.0.0", port=4000):
        self.app.run(host=host, port=port)
