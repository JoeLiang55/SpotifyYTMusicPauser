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

    hotkey_manager = HotkeyManager(on_toggle_media)

    def apply_hotkey(hotkey: str) -> bool:
        try:
            hotkey_manager.bind(hotkey)
            config_manager.update_hotkey(hotkey)
            return True
        except Exception as exc:  # noqa: BLE001
            print(f"Hotkey bind failed for '{hotkey}': {exc}")
            return False

    initial_hotkey = config.get("hotkey", "f6")
    if not apply_hotkey(initial_hotkey):
        if not apply_hotkey("f6"):
            raise RuntimeError("Failed to bind initial hotkey.")

    tray_app = TrayApp(
        get_hotkey=lambda: hotkey_manager.current_hotkey or "unbound",
        on_change_hotkey=apply_hotkey,
        on_toggle=on_toggle_media,
        on_exit=hotkey_manager.stop,
    )

    print(f"Music Hotkey Controller running. Current hotkey: {hotkey_manager.current_hotkey}")
    tray_app.run()


if __name__ == "__main__":
    main()
