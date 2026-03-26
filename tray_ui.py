import threading
import tkinter as tk
from tkinter import messagebox
from typing import Callable

import pystray
from PIL import Image, ImageDraw


class TrayApp:
    def __init__(
        self,
        get_hotkey: Callable[[], str],
        on_change_hotkey: Callable[[str], bool],
        on_toggle: Callable[[], None],
        on_exit: Callable[[], None],
    ) -> None:
        self._get_hotkey = get_hotkey
        self._on_change_hotkey = on_change_hotkey
        self._on_toggle = on_toggle
        self._on_exit = on_exit
        self.icon = pystray.Icon(
            "music-hotkey",
            self._build_icon(),
            "Music Hotkey Controller",
            menu=pystray.Menu(
                pystray.MenuItem(self._status_text, lambda: None, enabled=False),
                pystray.MenuItem("Toggle Media Now", self._handle_toggle),
                pystray.MenuItem("Change Hotkey", self._show_hotkey_editor),
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

    def _status_text(self, _item):
        return f"Active hotkey: {self._get_hotkey()}"

    def _handle_toggle(self, _icon, _item) -> None:
        self._on_toggle()

    def _show_hotkey_editor(self, _icon, _item) -> None:
        thread = threading.Thread(target=self._open_hotkey_window, daemon=True)
        thread.start()

    def _open_hotkey_window(self) -> None:
        root = tk.Tk()
        root.title("Set Hotkey")
        root.geometry("340x140")
        root.resizable(False, False)

        label = tk.Label(root, text="Enter hotkey (example: f6, ctrl+alt+m)")
        label.pack(pady=(14, 8))

        hotkey_var = tk.StringVar(value=self._get_hotkey())
        entry = tk.Entry(root, textvariable=hotkey_var, width=35)
        entry.pack()
        entry.focus_set()

        def save_hotkey() -> None:
            candidate = hotkey_var.get().strip().lower()
            if not candidate:
                messagebox.showerror("Invalid Hotkey", "Hotkey cannot be empty.")
                return

            changed = self._on_change_hotkey(candidate)
            if not changed:
                messagebox.showerror(
                    "Invalid Hotkey",
                    "Could not register this hotkey. Try another combination.",
                )
                return

            messagebox.showinfo("Hotkey Updated", f"New hotkey: {candidate}")
            root.destroy()

        save_button = tk.Button(root, text="Save", command=save_hotkey)
        save_button.pack(pady=14)
        root.mainloop()

    def _handle_exit(self, _icon, _item) -> None:
        self._on_exit()
        self.icon.stop()

    def run(self) -> None:
        self.icon.run()
