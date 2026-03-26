import asyncio
from dataclasses import dataclass
from typing import List

from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionPlaybackStatus,
)
from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as MediaManager,
)


@dataclass
class ToggleResult:
    action: str
    affected_sessions: int
    session_sources: List[str]


@dataclass
class SkipResult:
    affected_sessions: int
    session_sources: List[str]


class MediaController:
    async def _get_sessions(self):
        session_manager = await MediaManager.request_async()
        return list(session_manager.get_sessions())

    def _get_action(self, sessions) -> str:
        for session in sessions:
            playback_info = session.get_playback_info()
            if (
                playback_info
                and playback_info.playback_status
                == GlobalSystemMediaTransportControlsSessionPlaybackStatus.PLAYING
            ):
                return "pause"
        return "play"

    async def toggle_all_async(self) -> ToggleResult:
        sessions = await self._get_sessions()
        action = self._get_action(sessions)

        affected = 0
        sources: List[str] = []

        for session in sessions:
            source_id = session.source_app_user_model_id
            playback_info = session.get_playback_info()
            controls = playback_info.controls if playback_info else None

            if action == "pause" and controls and controls.is_pause_enabled:
                ok = await session.try_pause_async()
                if ok:
                    affected += 1
                    sources.append(source_id)
            elif action == "play" and controls and controls.is_play_enabled:
                ok = await session.try_play_async()
                if ok:
                    affected += 1
                    sources.append(source_id)

        return ToggleResult(action=action, affected_sessions=affected, session_sources=sources)

    def toggle_all(self) -> ToggleResult:
        return asyncio.run(self.toggle_all_async())

    async def skip_next_async(self) -> SkipResult:
        sessions = await self._get_sessions()

        affected = 0
        sources: List[str] = []

        for session in sessions:
            source_id = session.source_app_user_model_id
            playback_info = session.get_playback_info()
            controls = playback_info.controls if playback_info else None

            if controls and controls.is_next_enabled:
                ok = await session.try_skip_next_async()
                if ok:
                    affected += 1
                    sources.append(source_id)

        return SkipResult(affected_sessions=affected, session_sources=sources)

    def skip_next(self) -> SkipResult:
        return asyncio.run(self.skip_next_async())
