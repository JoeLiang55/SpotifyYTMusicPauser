from pathlib import Path

from config_manager import ConfigManager
from hotkey_manager import HotkeyManager
from media_controller import MediaController
from tray_ui import TrayApp


def main() -> None:
    project_dir = Path(__file__).resolve().parent
    config_manager = ConfigManager(project_dir / "config.json")
    media_controller = MediaController()

    config = config_manager.load()

    def on_toggle_media() -> None:
        try:
            result = media_controller.toggle_all()
            print(
                f"Action: {result.action} | Sessions: {result.affected_sessions}"
                f" | Sources: {', '.join(result.session_sources) if result.session_sources else 'none'}"
            )
        except Exception as exc:  # noqa: BLE001
            print(f"Media toggle failed: {exc}")

    def on_next_track() -> None:
        try:
            result = media_controller.skip_next()
            print(
                f"Action: next | Sessions: {result.affected_sessions}"
                f" | Sources: {', '.join(result.session_sources) if result.session_sources else 'none'}"
            )
        except Exception as exc:  # noqa: BLE001
            print(f"Next track failed: {exc}")

    hotkey_manager = HotkeyManager()

    def apply_hotkeys(toggle_hotkey: str, next_track_hotkey: str) -> bool:
        previous_toggle_hotkey = hotkey_manager.get_hotkey("toggle")
        previous_next_hotkey = hotkey_manager.get_hotkey("next_track")
        try:
            hotkey_manager.bind("toggle", toggle_hotkey, on_toggle_media)
            hotkey_manager.bind("next_track", next_track_hotkey, on_next_track)

            config_manager.update_hotkey(toggle_hotkey)
            config_manager.update_next_track_hotkey(next_track_hotkey)
            return True
        except Exception as exc:  # noqa: BLE001
            print(
                "Hotkey bind failed"
                f" (toggle='{toggle_hotkey}', next='{next_track_hotkey}'): {exc}"
            )
            # Restore previously active bindings when an update fails.
            if previous_toggle_hotkey:
                try:
                    hotkey_manager.bind("toggle", previous_toggle_hotkey, on_toggle_media)
                except Exception:
                    pass

            if previous_next_hotkey:
                try:
                    hotkey_manager.bind("next_track", previous_next_hotkey, on_next_track)
                except Exception:
                    pass
            return False

    initial_hotkey = config.get("hotkey", "f6")
    initial_next_track_hotkey = config.get("next_track_hotkey", "f7")
    if not apply_hotkeys(initial_hotkey, initial_next_track_hotkey):
        if not apply_hotkeys("f6", "f7"):
            raise RuntimeError("Failed to bind initial hotkeys.")

    tray_app = TrayApp(
        get_hotkeys=lambda: {
            "toggle": hotkey_manager.get_hotkey("toggle") or "unbound",
            "next_track": hotkey_manager.get_hotkey("next_track") or "unbound",
        },
        on_change_hotkeys=apply_hotkeys,
        on_toggle=on_toggle_media,
        on_next_track=on_next_track,
        on_exit=hotkey_manager.stop,
    )

    print(
        "Music Hotkey Controller running."
        f" Toggle: {hotkey_manager.get_hotkey('toggle')}"
        f" | Next Track: {hotkey_manager.get_hotkey('next_track')}"
    )
    tray_app.run()


if __name__ == "__main__":
    main()
