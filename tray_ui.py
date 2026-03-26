import threading
import tkinter as tk
from tkinter import messagebox
from typing import Callable

import pystray
from PIL import Image, ImageDraw


class TrayApp:
    def __init__(
        self,
        get_hotkeys: Callable[[], dict[str, str]],
        on_change_hotkeys: Callable[[str, str], bool],
        on_toggle: Callable[[], None],
        on_next_track: Callable[[], None],
        on_exit: Callable[[], None],
    ) -> None:
        self._get_hotkeys = get_hotkeys
        self._on_change_hotkeys = on_change_hotkeys
        self._on_toggle = on_toggle
        self._on_next_track = on_next_track
        self._on_exit = on_exit
        self.icon = pystray.Icon(
            "music-hotkey",
            self._build_icon(),
            "Music Hotkey Controller",
            menu=pystray.Menu(
                pystray.MenuItem(self._status_text_toggle, lambda: None, enabled=False),
                pystray.MenuItem(self._status_text_next, lambda: None, enabled=False),
                pystray.MenuItem("Toggle Media Now", self._handle_toggle),
                pystray.MenuItem("Next Track Now", self._handle_next_track),
                pystray.MenuItem("Change Hotkeys", self._show_hotkey_editor),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit", self._handle_exit),
            ),
        )

    def _build_icon(self) -> Image.Image:
        image = Image.new("RGB", (64, 64), "#101828")
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((8, 8, 56, 56), radius=12, fill="#22c55e")
        draw.rectangle((24, 20, 30, 44), fill="#101828")
        draw.rectangle((34, 20, 40, 44), fill="#101828")
        return image

    def _status_text_toggle(self, _item):
        return f"Play/Pause: {self._get_hotkeys().get('toggle', 'unbound')}"

    def _status_text_next(self, _item):
        return f"Next Track: {self._get_hotkeys().get('next_track', 'unbound')}"

    def _handle_toggle(self, _icon, _item) -> None:
        self._on_toggle()

    def _handle_next_track(self, _icon, _item) -> None:
        self._on_next_track()

    def _show_hotkey_editor(self, _icon, _item) -> None:
        thread = threading.Thread(target=self._open_hotkey_window, daemon=True)
        thread.start()

    def _open_hotkey_window(self) -> None:
        root = tk.Tk()
        root.title("Set Hotkeys")
        root.geometry("360x220")
        root.resizable(False, False)

        hint = tk.Label(root, text="Enter hotkeys (example: f6, ctrl+alt+m)")
        hint.pack(pady=(12, 6))

        labels_frame = tk.Frame(root)
        labels_frame.pack(padx=12, pady=(6, 2), fill="x")

        toggle_label = tk.Label(labels_frame, text="Play/Pause Hotkey")
        toggle_label.pack(anchor="w")

        hotkeys = self._get_hotkeys()
        toggle_var = tk.StringVar(value=hotkeys.get("toggle", "f6"))
        toggle_entry = tk.Entry(labels_frame, textvariable=toggle_var, width=35)
        toggle_entry.pack(fill="x")

        next_label = tk.Label(labels_frame, text="Next Track Hotkey")
        next_label.pack(anchor="w", pady=(8, 0))

        next_var = tk.StringVar(value=hotkeys.get("next_track", "f7"))
        next_entry = tk.Entry(labels_frame, textvariable=next_var, width=35)
        next_entry.pack(fill="x")
        toggle_entry.focus_set()

        def save_hotkeys() -> None:
            toggle_candidate = toggle_var.get().strip().lower()
            next_candidate = next_var.get().strip().lower()

            if not toggle_candidate or not next_candidate:
                messagebox.showerror("Invalid Hotkey", "Hotkey cannot be empty.")
                return

            if toggle_candidate == next_candidate:
                messagebox.showerror(
                    "Invalid Hotkey",
                    "Play/Pause and Next Track hotkeys must be different.",
                )
                return

            changed = self._on_change_hotkeys(toggle_candidate, next_candidate)
            if not changed:
                messagebox.showerror(
                    "Invalid Hotkey",
                    "Could not register one or more hotkeys. Try other combinations.",
                )
                return

            messagebox.showinfo(
                "Hotkeys Updated",
                f"Play/Pause: {toggle_candidate}\nNext Track: {next_candidate}",
            )
            root.destroy()

        save_button = tk.Button(root, text="Save", command=save_hotkeys)
        save_button.pack(pady=14)
        root.mainloop()

    def _handle_exit(self, _icon, _item) -> None:
        self._on_exit()
        self.icon.stop()

    def run(self) -> None:
        self.icon.run()
