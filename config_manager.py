import json
from pathlib import Path
from typing import Dict


DEFAULT_CONFIG = {"hotkey": "f6"}


class ConfigManager:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path

    def load(self) -> Dict[str, str]:
        if not self.config_path.exists():
            self.save(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()

        try:
            data = json.loads(self.config_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self.save(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()

        hotkey = data.get("hotkey", DEFAULT_CONFIG["hotkey"])
        return {"hotkey": str(hotkey).lower()}

    def save(self, config: Dict[str, str]) -> None:
        self.config_path.write_text(
            json.dumps(config, indent=2),
            encoding="utf-8",
        )

    def update_hotkey(self, hotkey: str) -> Dict[str, str]:
        config = self.load()
        config["hotkey"] = hotkey.lower().strip()
        self.save(config)
        return config
