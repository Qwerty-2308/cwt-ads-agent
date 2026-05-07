"""CWT Ads Agent — 4-agent CrewAI pipeline."""

import json
import os
from pathlib import Path

from crewai import Agent, Crew, LLM, Process, Task

from .config import (
    LLM_MODEL,
    LLM_BASE_URL,
    LLM_FALLBACK_MODELS,
    OPENROUTER_API_KEY,
    OUTPUT_DIR,
)
from .tools import (
    MetaAdsResearchTool,
    ElevenLabsVoiceTool,
    ImageGenTool,
    GDriveTool,
    RemotionRenderTool,
)
from .utils import get_logger

logger = get_logger(__name__)


def build_llm() -> LLM:
    return LLM(
        model=LLM_MODEL,
        api_key=OPENROUTER_API_KEY,
        base_url=LLM_BASE_URL,
        max_retries=5,
    )


def build_crew() -> Crew:
    llm = build_llm()

    # ── Tools ────────────────────────────────────────────────────────────
    ads_tool = MetaAdsResearchTool()
    gdrive_tool = GDriveTool()
    image_tool = ImageGenTool()
    voice_tool = ElevenLabsVoiceTool()
    render_tool = RemotionRenderTool()

    # ── Agent 1: Ad Researcher ───────────────────────────────────────────
    ad_researcher = Agent(
        role="Meta Ads Library Researcher",
        goal=(
            "Find the top-performing trading and finance ads on Facebook and Instagram "
            "from the last 30 days. Identify what makes them succeed."
        ),
        backstory=(
            "You are a performance marketing expert who specialises in analysing "
            "paid social campaigns for financial products. You know how to read "
            "ad creative to spot what resonates with retail traders and investors."
        ),
        tools=[ads_tool],
        llm=llm,
        verbose=True,
        max_iter=3,
    )

    # ── Agent 2: Marketing Analyzer ─────────────────────────────────────
    marketing_analyzer = Agent(
        role="Direct-Response Marketing Analyst",
        goal=(
            "Extract the core pain points, emotional hooks, and marketing frameworks "
            "from the winning ads. Produce an actionable brief for ad creation."
        ),
        backstory=(
            "You are a copywriting strategist trained in direct-response marketing. "
            "You can read any ad and immediately identify the psychological triggers, "
            "the core promise, the target avatar, and why it converts."
        ),
        tools=[],
        llm=llm,
        verbose=True,
        max_iter=3,
    )

    # ── Agent 3: Script Writer ───────────────────────────────────────────
    script_writer = Agent(
        role="Video Ad Scriptwriter",
        goal=(
            "Write a compelling 60-second video ad script for CrowdWisdomTrading "
            "that combines winning marketing angles with CWT's unique product data."
        ),
        backstory=(
            "You are an award-winning direct-response scriptwriter who has written "
            "hundreds of profitable video ads for financial and trading brands. "
            "You know how to open with a pattern interrupt, build desire, handle "
            "objections, and close with a clear CTA — all in 60 seconds."
        ),
        tools=[gdrive_tool],
        llm=llm,
        verbose=True,
        max_iter=3,
    )

    # ── Agent 4: Video Creator ───────────────────────────────────────────
    video_creator = Agent(
        role="AI Video Producer",
        goal=(
            "Generate all visual and audio assets for the 60-second ad and render "
            "the final MP4 using Remotion with voice narration and subtitles."
        ),
        backstory=(
            "You are an AI-powered video producer who creates high-converting social "
            "media ads. You can generate images, produce voice-overs, and orchestrate "
            "video rendering pipelines. You always produce polished, professional output."
        ),
        tools=[image_tool, voice_tool, render_tool],
        llm=llm,
        verbose=True,
        max_iter=12,
    )

    # ── Task 1: Research ─────────────────────────────────────────────────
    research_task = Task(
        description=(
            "Search the Meta Ads Library for successful trading and finance ads "
            "from the last 30 days using the meta_ads_research tool. "
            "Focus on ads promoting trading signals, trading communities, stock market "
            "education, and financial freedom in the US, UK, Australia, and Canada. "
            "Save all results to output/ads_research.json. "
            "Return a summary of the top 10 ads found."
        ),
        expected_output=(
            "A JSON summary of the top 10 best-performing ads found, including "
            "page name, ad copy, CTA, and what makes each ad compelling."
        ),
        agent=ad_researcher,
    )

    # ── Task 2: Analysis ────────────────────────────────────────────────
    analysis_task = Task(
        description=(
            "Analyse the top ads from the research task output. "
            "For each winning ad identify: "
            "1. Core pain point being addressed "
            "2. Primary emotional hook / pattern interrupt "
            "3. Key promise / transformation offered "
            "4. Proof elements used (numbers, testimonials, social proof) "
            "5. CTA structure "
            "Then synthesise the top 5 pain points and top 3 proven hooks "
            "that appear across multiple winning ads. "
            "Save the full analysis to output/marketing_analysis.json."
        ),
        expected_output=(
            "A structured marketing brief containing: "
            "top 5 pain points, top 3 emotional hooks, "
            "proven ad frameworks found, and a recommended angle for the CWT ad."
        ),
        agent=marketing_analyzer,
        context=[research_task],
        output_file=str(OUTPUT_DIR / "marketing_analysis.json"),
    )

    # ── Task 3: Scripting ────────────────────────────────────────────────
    script_task = Task(
        description=(
            "Use the gdrive_product_data tool to fetch CrowdWisdomTrading's product "
            "information, USPs, and audience data. "
            "Then write a 60-second video ad script using the top pain points "
            "and hooks from the marketing analysis. "
            "The script must follow this structure: "
            "- Seconds 0-5: Pattern interrupt / hook (stop the scroll) "
            "- Seconds 5-20: Agitate the pain "
            "- Seconds 20-40: Introduce CWT as the solution with proof points "
            "- Seconds 40-55: Social proof + transformation "
            "- Seconds 55-60: CTA (crowdwisdomtrading.com/trial) "
            "Also provide: "
            "a) The full narration text for voice-over "
            "b) 6 image prompts (one per ~10-second scene) "
            "c) Subtitle segments with start times "
            "Return the complete script as a JSON object and save to "
            "output/ad_script.json."
        ),
        expected_output=(
            "A JSON object with keys: title, narration (full voice-over text), "
            "segments (list of {text, start, duration} for subtitles), "
            "image_prompts (list of 6 scene descriptions)."
        ),
        agent=script_writer,
        context=[research_task, analysis_task],
        output_file=str(OUTPUT_DIR / "ad_script.json"),
    )

    # ── Task 4: Video Production ─────────────────────────────────────────
    video_task = Task(
        description=(
            "Produce the final 60-second ad video using the script from Task 3. "
            "Step 1: Generate 6 scene images using image_generator tool. "
            "  Use the image_prompts from the script — each prompt separated by ';'. "
            "  Example: 'stressed trader at desk;crowd of happy traders;stock chart going up;...' "
            "Step 2: Generate voice narration using elevenlabs_voice tool. "
            "  Pass the full narration text from the script. "
            "Step 3: Build the script_json payload with these exact keys: "
            "  title, narration, segments, voice_path (from step 2), "
            "  image_paths (list from step 1, split by newline). "
            "Step 4: Render the video using remotion_render tool with the script_json. "
            "Return the path to the final rendered MP4 file."
        ),
        expected_output=(
            "The absolute file path to the rendered output/ad_video.mp4 file, "
            "confirming the video was successfully created."
        ),
        agent=video_creator,
        context=[script_task],
    )

    return Crew(
        agents=[ad_researcher, marketing_analyzer, script_writer, video_creator],
        tasks=[research_task, analysis_task, script_task, video_task],
        process=Process.sequential,
        verbose=True,
    )
