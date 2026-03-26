import threading
from typing import Callable, Optional

import keyboard


class HotkeyManager:
    def __init__(self, callback: Callable[[], None]) -> None:
        self._callback = callback
        self._lock = threading.Lock()
        self._current_hotkey: Optional[str] = None
        self._hotkey_ref = None

    @property
    def current_hotkey(self) -> Optional[str]:
        with self._lock:
            return self._current_hotkey

    def bind(self, hotkey: str) -> None:
        normalized = hotkey.lower().strip()
        with self._lock:
            if self._hotkey_ref is not None:
                keyboard.remove_hotkey(self._hotkey_ref)
                self._hotkey_ref = None

            self._hotkey_ref = keyboard.add_hotkey(normalized, self._callback, suppress=False)
            self._current_hotkey = normalized

    def stop(self) -> None:
        with self._lock:
            if self._hotkey_ref is not None:
                keyboard.remove_hotkey(self._hotkey_ref)
                self._hotkey_ref = None
            self._current_hotkey = None
