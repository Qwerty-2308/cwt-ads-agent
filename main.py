"""Top-level runner — allows `python main.py` from project root."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))


def parse_args():
    p = argparse.ArgumentParser(
        description="CWT Ads AI Agent — generate video ads for any product"
    )
    p.add_argument(
        "--product",
        type=str,
        default=None,
        help="Product description (overrides data/product_data.md)",
    )
    p.add_argument(
        "--niche",
        type=str,
        default=None,
        help="Comma-separated search terms e.g. 'fitness,weight loss,supplements'",
    )
    p.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory (default: output/)",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Inject CLI overrides into env before config loads
    import os
    if args.product:
        os.environ["PRODUCT_OVERRIDE"] = args.product
    if args.niche:
        os.environ["SEARCH_TERMS_OVERRIDE"] = args.niche
    if args.output_dir:
        os.environ["OUTPUT_DIR_OVERRIDE"] = args.output_dir

    from cwt_ads_agent.main import run
    run()
