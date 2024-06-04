from abc import abstractmethod, ABC
from enum import Enum
import json


class Action(Enum):
    PROGRESS = 'progress'
    ERROR = 'error'
    DONE = 'done'


class StatusMessage:
    def __init__(self, action, payload = None):
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

    """
    The unique identifier of the strategy.
    """
    @abstractmethod
    def id(self):
        pass

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    async def generate(self, url, selector):
        pass

    def run_javascript(self, javascript):
        self._javascript_injections.append(javascript)

    def run_javascript_when_selector_available(self, selector, javascript):
        self.run_javascript(f"""
            const observer = new MutationObserver(mutations => {{
                if (document.querySelector('{selector}')) {{
                    {javascript}
                    observer.disconnect();
                    callback();
                }}
            }});
            observer.observe(document.body, {{ childList: true, subtree: true }});
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
