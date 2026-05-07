"""Entry point for the CWT Ads Agent pipeline."""

import json
import sys
from pathlib import Path

from .crew import build_crew
from .utils import get_logger

logger = get_logger(__name__)


def run() -> None:
    logger.info("=" * 60)
    logger.info("CrowdWisdomTrading Daily Ads AI Agent — Starting")
    logger.info("=" * 60)

    crew = build_crew()

    try:
        result = crew.kickoff()
        logger.info("=" * 60)
        logger.info("Pipeline completed successfully")
        logger.info("=" * 60)

        # Print output file locations
        output_dir = Path("output")
        outputs = {
            "ads_research": output_dir / "ads_research.json",
            "marketing_analysis": output_dir / "marketing_analysis.json",
            "ad_script": output_dir / "ad_script.json",
            "voice": output_dir / "voice.mp3",
            "video": output_dir / "ad_video.mp4",
        }

        print("\n📦 Output files:")
        for name, path in outputs.items():
            status = "✅" if path.exists() else "❌"
            print(f"  {status} {name}: {path}")

        print(f"\n🎬 Final result:\n{result}")

    except Exception as exc:
        logger.error("Pipeline failed: %s", exc, exc_info=True)
        sys.exit(1)
