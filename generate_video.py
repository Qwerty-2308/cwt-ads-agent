"""
Standalone video generator — reads output/ad_script.json and produces
voice + images + rendered MP4 without needing the CrewAI agent loop.

Usage:
    python generate_video.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from cwt_ads_agent.config import OUTPUT_DIR
from cwt_ads_agent.tools.image_gen import ImageGenTool
from cwt_ads_agent.tools.elevenlabs_voice import ElevenLabsVoiceTool
from cwt_ads_agent.tools.remotion_render import RemotionRenderTool
from cwt_ads_agent.utils import get_logger

logger = get_logger("generate_video")


def run() -> None:
    script_path = OUTPUT_DIR / "ad_script.json"
    if not script_path.exists():
        logger.error("No ad_script.json found. Run main.py first.")
        sys.exit(1)

    raw = script_path.read_text()
    # The LLM sometimes wraps JSON in markdown code fences — strip them
    raw = raw.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:])
    if raw.endswith("```"):
        raw = "\n".join(raw.split("\n")[:-1])

    script = json.loads(raw)
    logger.info("Loaded ad_script.json: %s", script.get("title", "untitled"))

    # ── Step 1: Generate images ──────────────────────────────────────────
    image_prompts = script.get("image_prompts", [])
    if not image_prompts:
        logger.warning("No image_prompts in script — using defaults")
        image_prompts = [
            "frustrated trader at desk staring at red screen",
            "stock market chart crashing, trader stressed",
            "AI dashboard with trading signals and data",
            "crowd of happy traders celebrating profits",
            "trader on laptop smiling with green chart",
            "call to action: crowdwisdomtrading.com trial sign up",
        ]

    prompt_str = ";".join(image_prompts)
    logger.info("Generating %d images...", len(image_prompts))
    image_paths_str = ImageGenTool()._run(prompt_str)
    image_paths = [p for p in image_paths_str.split("\n") if p.strip() and p != "Image generation failed"]
    logger.info("Generated %d images", len(image_paths))

    # ── Step 2: Generate voice ───────────────────────────────────────────
    narration = script.get("narration", "")
    if not narration:
        logger.error("No narration text in script")
        sys.exit(1)

    logger.info("Generating voice narration (%d chars)...", len(narration))
    voice_path = ElevenLabsVoiceTool()._run(narration)
    logger.info("Voice saved: %s", voice_path)

    # ── Step 3: Render video ─────────────────────────────────────────────
    render_data = {
        "title": script.get("title", "CWT Ad"),
        "narration": narration,
        "segments": script.get("segments", []),
        "voice_path": voice_path,
        "image_paths": image_paths,
    }

    logger.info("Rendering video with Remotion...")
    video_path = RemotionRenderTool()._run(json.dumps(render_data))
    logger.info("Video rendered: %s", video_path)

    print(f"\n✅ Video ready: {video_path}")


if __name__ == "__main__":
    run()
