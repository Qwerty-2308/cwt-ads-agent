"""Agent 4 tool — generates voice narration using ElevenLabs (gTTS fallback)."""

from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, OUTPUT_DIR
from ..utils import get_logger

logger = get_logger(__name__)


class VoiceInput(BaseModel):
    script: str = Field(description="The full ad narration script text to convert to speech.")


class ElevenLabsVoiceTool(BaseTool):
    name: str = "elevenlabs_voice"
    description: str = (
        "Converts the ad script text to realistic voice narration using ElevenLabs "
        "(falls back to gTTS if ElevenLabs key lacks TTS permission). "
        "Saves audio to output/voice.mp3 and returns the file path."
    )
    args_schema: Type[BaseModel] = VoiceInput

    def _run(self, script: str) -> str:
        output_path = OUTPUT_DIR / "voice.mp3"

        # Try ElevenLabs first
        try:
            result = self._elevenlabs(script, output_path)
            if result:
                return str(output_path)
        except Exception as exc:
            logger.warning("ElevenLabs failed (%s) — falling back to gTTS", exc)

        # Fallback: gTTS (Google Text-to-Speech, completely free)
        return self._gtts(script, output_path)

    def _elevenlabs(self, script: str, output_path: Path) -> bool:
        from elevenlabs.client import ElevenLabs

        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        logger.info("Generating voice via ElevenLabs | voice=%s | chars=%d", ELEVENLABS_VOICE_ID, len(script))

        audio = client.text_to_speech.convert(
            voice_id=ELEVENLABS_VOICE_ID,
            text=script,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )

        with open(output_path, "wb") as fh:
            for chunk in audio:
                fh.write(chunk)

        size = output_path.stat().st_size
        if size < 1000:
            raise ValueError(f"ElevenLabs returned empty audio ({size} bytes)")

        logger.info("ElevenLabs voice saved → %s (%d bytes)", output_path, size)
        return True

    def _gtts(self, script: str, output_path: Path) -> str:
        from gtts import gTTS

        logger.info("Generating voice via gTTS | chars=%d", len(script))
        tts = gTTS(text=script, lang="en", slow=False)
        tts.save(str(output_path))

        size = output_path.stat().st_size
        logger.info("gTTS voice saved → %s (%d bytes)", output_path, size)
        return str(output_path)
