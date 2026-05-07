"""Agent 4 tool — assembles and renders the final video using Remotion."""

import json
import subprocess
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..config import OUTPUT_DIR, VIDEO_DIR, VIDEO_FPS, VIDEO_DURATION_SECONDS
from ..utils import get_logger

logger = get_logger(__name__)


class RenderInput(BaseModel):
    script_json: str = Field(
        description=(
            "JSON string with the ad script data. "
            "Must include: title, narration, segments (list of {text, start, duration}), "
            "voice_path, image_paths (list of paths)."
        )
    )


class RemotionRenderTool(BaseTool):
    name: str = "remotion_render"
    description: str = (
        "Takes the final ad script data and renders a 60-second MP4 video using Remotion. "
        "Requires Node.js and the video/ project dependencies to be installed. "
        "Returns the path to the rendered MP4."
    )
    args_schema: Type[BaseModel] = RenderInput

    def _run(self, script_json: str) -> str:
        try:
            data = json.loads(script_json)
        except json.JSONDecodeError as exc:
            logger.error("Invalid script JSON: %s", exc)
            raise ValueError(f"script_json must be valid JSON: {exc}") from exc

        # Write script data for Remotion to consume
        script_data_path = VIDEO_DIR / "src" / "script_data.json"
        with open(script_data_path, "w") as fh:
            json.dump(data, fh, indent=2)
        logger.info("Script data written → %s", script_data_path)

        # Copy voice and images to Remotion public/ so they're accessible
        self._copy_assets(data)

        output_mp4 = OUTPUT_DIR / "ad_video.mp4"

        # Install dependencies if needed
        node_modules = VIDEO_DIR / "node_modules"
        if not node_modules.exists():
            logger.info("Installing Remotion dependencies...")
            subprocess.run(
                ["npm", "install"],
                cwd=VIDEO_DIR,
                check=True,
                capture_output=True,
                text=True,
            )

        # Render via Remotion CLI
        logger.info("Rendering video with Remotion...")
        result = subprocess.run(
            [
                "npx",
                "remotion",
                "render",
                "src/index.ts",
                "AdVideo",
                str(output_mp4),
                "--props",
                json.dumps({"script": data}),
            ],
            cwd=VIDEO_DIR,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode != 0:
            logger.error("Remotion render failed:\n%s", result.stderr)
            raise RuntimeError(f"Remotion render failed:\n{result.stderr}")

        logger.info("Video rendered → %s", output_mp4)
        return str(output_mp4)

    def _copy_assets(self, data: dict) -> None:
        import shutil

        public_dir = VIDEO_DIR / "public"
        public_dir.mkdir(exist_ok=True)

        voice_path = data.get("voice_path", "")
        if voice_path and Path(voice_path).exists():
            dest = public_dir / "voice.mp3"
            shutil.copy(voice_path, dest)
            data["voice_path"] = "voice.mp3"
            logger.info("Copied voice → %s", dest)

        image_paths = data.get("image_paths", [])
        new_paths = []
        for i, img_path in enumerate(image_paths):
            if Path(img_path).exists():
                ext = Path(img_path).suffix
                dest = public_dir / f"scene_{i:02d}{ext}"
                shutil.copy(img_path, dest)
                new_paths.append(f"scene_{i:02d}{ext}")
                logger.info("Copied image %d → %s", i, dest)
            else:
                new_paths.append(img_path)
        data["image_paths"] = new_paths
