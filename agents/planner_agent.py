"""
Planner Agent
-------------
Detects input type (research topic or URL) and creates a structured workflow plan.
"""

import re
import time


def is_valid_url(text: str) -> bool:
    """Check if the given text is a URL."""
    url_pattern = re.compile(r'^https?://.+$')
    return bool(url_pattern.match(text.strip()))


def planner_agent(input_data: dict) -> dict:
    """
    Planner Agent: Detects input type and creates a research workflow plan.

    Args:
        input_data: dict with keys 'topic', 'url', 'mode'

    Returns:
        dict containing detected type, plan steps, and metadata
    """

    time.sleep(0.5)

    topic = input_data.get("topic", "").strip()
    url = input_data.get("url", "").strip()
    mode = input_data.get("mode", "Short Summary")

    # Check whether input was provided
    if not topic and not url:
        return {
            "input_type": "error",
            "subject": "",
            "mode": mode,
            "steps": [],
            "keywords": [],
            "estimated_sources": 0,
            "status": "Please provide a research topic or URL",
        }

    # Detect input type
    if url and is_valid_url(url):
        input_type = "url"
        subject = url

        plan_steps = [
            "Fetch and parse research paper from URL",
            "Extract abstract, methodology, results, and conclusions",
            "Identify key contributions and novelty",
            "Summarize findings in structured format",
            "Compile references and citations",
        ]

        keywords = [
            "paper analysis",
            "academic research",
            "literature review",
        ]

    else:
        input_type = "topic"
        subject = topic

        plan_steps = [
            f"Search academic databases for: {topic}",
            "Collect top research papers and articles",
            "Extract key themes and findings",
            "Synthesize information across sources",
            "Generate structured research report",
        ]

        keywords = (
            topic.lower().split()[:5]
            if topic
            else ["research", "analysis"]
        )

    plan = {
        "input_type": input_type,
        "subject": subject,
        "mode": mode,
        "steps": plan_steps,
        "keywords": keywords,
        "estimated_sources": 8 if input_type == "topic" else 3,
        "status": "Plan created successfully",
    }

    return plan
