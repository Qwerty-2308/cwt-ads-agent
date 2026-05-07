"""Top-level runner — allows `python main.py` from project root."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from cwt_ads_agent.main import run

if __name__ == "__main__":
    run()
