import threading
from typing import Callable, Dict, Optional

import keyboard


class HotkeyManager:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._current_hotkeys: Dict[str, str] = {}
        self._hotkey_refs: Dict[str, int] = {}

    @property
    def current_hotkey(self) -> Optional[str]:
        return self.get_hotkey("toggle")

    def get_hotkey(self, action: str) -> Optional[str]:
        with self._lock:
            return self._current_hotkeys.get(action)

    def bind(self, action: str, hotkey: str, callback: Callable[[], None]) -> None:
        normalized = hotkey.lower().strip()
        with self._lock:
            existing_ref = self._hotkey_refs.get(action)
            if existing_ref is not None:
                keyboard.remove_hotkey(existing_ref)
                del self._hotkey_refs[action]

            hotkey_ref = keyboard.add_hotkey(normalized, callback, suppress=False)
            self._hotkey_refs[action] = hotkey_ref
            self._current_hotkeys[action] = normalized

    def stop(self) -> None:
        with self._lock:
            for hotkey_ref in self._hotkey_refs.values():
                keyboard.remove_hotkey(hotkey_ref)
            self._hotkey_refs.clear()
            self._current_hotkeys.clear()
