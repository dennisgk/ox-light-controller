from pathlib import Path
import json
from lcd_control import LcdControl

class EventEmitter:
    def __init__(self):
        self._events = {}
        
        self.base_path = Path(__file__).resolve().parent
        self.config_path = self.base_path / "config.json"

        with open(self.config_path, "r") as f:
            self.config = json.load(f)

        self.lcd = LcdControl()

    def on(self, event, handler):
        """Subscribe to an event"""
        self._events.setdefault(event, []).append(handler)

    def off(self, event, handler):
        """Unsubscribe"""
        if event in self._events:
            self._events[event].remove(handler)

    def emit(self, event, *args, **kwargs):
        """Trigger event"""
        if event in self._events:
            for handler in self._events[event]:
                handler(*args, **kwargs)

    def update_config(self):
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=4)