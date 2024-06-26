from abc import abstractmethod, ABC
from enum import Enum
import json


class StrategyCategory(Enum):
    STABLE = 'Stable'
    EXPERIMENTAL = 'Experimental'


class Action(Enum):
    PROGRESS = 'progress'
    ERROR = 'error'
    DONE = 'done'


class StatusMessage:
    def __init__(self, action, payload=None):
        self.action = action
        self.payload = payload

    def to_json(self):
        return json.dumps({
            'action': self.action.value,
            'payload': self.payload
        })


class AbstractGenerationStrategy(ABC):
    def __init__(self):
        self._status_queue = None
        self._javascript_injections = []
        self._css_injections = []

        # Add CSS for the overlay and spinner
        self.add_css("""
            .overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.3);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
                display: none;
            }
            .overlay .message {
                background-color: rgba(255, 255, 255, 0.6);
                padding: 20px;
                border-radius: 10px;
                font-size: 20px;
                color: black;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .spinner {
                border: 4px solid rgba(255, 255, 255, 0.3);
                border-top: 4px solid #000;
                border-radius: 50%;
                width: 20px;
                height: 20px;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        """)

        # Add JavaScript to show the overlay
        self.run_javascript("""
            function showOverlay(message) {
                let overlay = document.createElement('div');
                overlay.className = 'overlay';
                overlay.innerHTML = '<div class="message"><div class="spinner"></div>' + message + '</div>';
                document.body.appendChild(overlay);
                overlay.style.display = 'flex';
            }

            function hideOverlay() {
                let overlay = document.querySelector('.overlay');
                if (overlay) {
                    overlay.style.display = 'none';
                }
            }
        """)

    """
    The unique identifier of the strategy.
    """
    @abstractmethod
    def id(self):
        pass

    @abstractmethod
    def name(self):
        pass

    def category(self):
        return StrategyCategory.EXPERIMENTAL

    @abstractmethod
    async def generate(self, url, selector, prompt):
        pass

    def run_javascript(self, javascript):
        self._javascript_injections.append(javascript)

    def run_javascript_delayed(self, javascript, delay):
        self.run_javascript(f"""
            setTimeout(() => {{
                {javascript}
            }}, {delay});
        """)

    def run_javascript_when_selector_available(self, selector, javascript):
        self.run_javascript(f"""
            if (document.querySelector('{selector}')) {{    
                setTimeout(() => {{
                    {javascript}
                }}, 3000);
                console.log('Selector found');
            }} else {{
                const observer = new MutationObserver(mutations => {{
                    if (document.querySelector('{selector}')) {{
                        setTimeout(() => {{
                            {javascript}
                        }}, 3000);
                            console.log('Selector found after mutation');
                            observer.disconnect();
                    }}
                }});
                observer.observe(document.body, {{ childList: true, subtree: true }});
                console.log('Waiting for selector...');
            }}
        """)

    def replace_html(self, selector, html):
        self.run_javascript_when_selector_available(selector, f"""
            document.querySelector('{selector}').innerHTML = `{html}`;
            console.log('HTML replaced');
        """)

    def add_css(self, css):
        self._css_injections.append(css)

    def send_progress(self, message):
        self._status_queue.put(StatusMessage(Action.PROGRESS, message))

    def set_status_queue(self, status_queue):
        self._status_queue = status_queue

    def get_javascript_injections(self):
        return self._javascript_injections

    def get_css_injections(self):
        return self._css_injections
