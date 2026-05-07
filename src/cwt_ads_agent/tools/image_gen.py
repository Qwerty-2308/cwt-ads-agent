"""Agent 4 tool — generates ad images using Pollinations.ai (free, no API key)."""

import re
import time
import urllib.parse
from pathlib import Path
from typing import Type

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..config import OUTPUT_DIR, IMAGE_WIDTH, IMAGE_HEIGHT
from ..utils import get_logger

logger = get_logger(__name__)

BASE_URL = "https://image.pollinations.ai/prompt"
MAX_PROMPT_LEN = 200
RETRY_DELAY = 5


class ImageGenInput(BaseModel):
    prompts: str = Field(
        description=(
            "Scene image prompts separated by semicolons (;) or newlines. "
            "One prompt per scene. Example: 'stressed trader at desk;happy traders celebrating'"
        )
    )


class ImageGenTool(BaseTool):
    name: str = "image_generator"
    description: str = (
        "Generates high-quality images for each scene of the ad video using Pollinations.ai (free). "
        "Pass prompts as semicolon-separated strings — one per scene. "
        "Saves images to output/images/scene_00.jpg, scene_01.jpg, etc. "
        "Returns newline-separated list of saved file paths."
    )
    args_schema: Type[BaseModel] = ImageGenInput

    def _run(self, prompts: str) -> str:
        # Handle both ; and newline separators
        if ";" in prompts:
            raw_scenes = prompts.split(";")
        else:
            raw_scenes = prompts.split("\n")

        scenes = []
        for s in raw_scenes:
            s = s.strip()
            if not s:
                continue
            # Strip "Scene X:" / "Scene X -" prefixes the LLM adds
            s = re.sub(r"^[Ss]cene\s*\d+\s*[:–\-]\s*", "", s)
            if len(s) > MAX_PROMPT_LEN:
                s = s[:MAX_PROMPT_LEN]
            scenes.append(s)

        if not scenes:
            return "No valid prompts provided"

        img_dir = OUTPUT_DIR / "images"
        img_dir.mkdir(parents=True, exist_ok=True)

        saved_paths = []
        for i, prompt in enumerate(scenes):
            path = img_dir / f"scene_{i:02d}.jpg"
            success = self._download_with_retry(prompt, path)
            if success:
                saved_paths.append(str(path))
                logger.info("Image %d/%d saved → %s", i + 1, len(scenes), path)
            else:
                logger.warning("Skipping scene %d — all retries failed", i)

            if i < len(scenes) - 1:
                time.sleep(2)

        if saved_paths:
            return "\n".join(saved_paths)
        return "Image generation failed"

    def _download_with_retry(self, prompt: str, dest: Path, max_retries: int = 3) -> bool:
        enhanced = (
            f"{prompt}, cinematic, 4k, professional photography, "
            "dramatic lighting, trading finance"
        )
        encoded = urllib.parse.quote(enhanced)
        url = f"{BASE_URL}/{encoded}?width={IMAGE_WIDTH}&height={IMAGE_HEIGHT}&nologo=true"

        for attempt in range(max_retries):
            try:
                resp = requests.get(url, timeout=60)
                if resp.status_code == 429:
                    wait = RETRY_DELAY * (attempt + 1)
                    logger.warning("Pollinations 429 — waiting %ds", wait)
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                dest.write_bytes(resp.content)
                return True
            except Exception as exc:
                logger.error("Image gen attempt %d failed: %s", attempt + 1, exc)
                if attempt < max_retries - 1:
                    time.sleep(RETRY_DELAY)

        return False
