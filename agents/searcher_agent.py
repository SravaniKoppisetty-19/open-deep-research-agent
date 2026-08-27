"""
Searcher Agent
--------------
Collects real information from web and academic search results.
Returns structured research data for the Writer Agent.
"""

import os
import time
import serpapi


def search_web(query, num_results=5):
    """Search Google using SerpApi."""

    api_key = os.getenv("SERPAPI_KEY")

    if not api_key:
        raise ValueError(
            "SERPAPI_KEY is not configured. "
            "Add your SerpApi API key to the environment variables."
        )

    client = serpapi.Client(api_key=api_key)

    results = client.search({
        "engine": "google",
        "q": query,
        "num": num_results,
        "hl": "en",
        "gl": "in"
    })

    return results


def search_scholar(query, num_results=5):
    """Search Google Scholar for academic papers."""

    api_key = os.getenv("SERPAPI_KEY")

    if not api_key:
        raise ValueError("SERPAPI_KEY is not configured.")

    client = serpapi.Client(api_key=api_key)

    results = client.search({
        "engine": "google_scholar",
        "q": query,
        "num": num_results,
        "hl": "en"
    })

    return results


def extract_web_sources(results):
    """Extract useful information from Google results."""

    sources = []

    for result in results.get("organic_results", []):
        title = result.get("title", "")
        link = result.get("link", "")
        snippet = result.get("snippet", "")

        if title and link:
            sources.append({
                "title": title,
                "url": link,
                "snippet": snippet,
                "source_type": "Web"
            })

    return sources


def extract_scholar_sources(results):
    """Extract useful information from Google Scholar results."""

    sources = []

    for result in results.get("organic_results", []):
        title = result.get("title", "")
        link = result.get("link", "")
        snippet = result.get("snippet", "")

        publication_info = result.get("publication_info", {})

        summary = publication_info.get("summary", "")

        if title and link:
            sources.append({
                "title": title,
                "url": link,
                "snippet": snippet,
                "publication_info": summary,
                "source_type": "Academic"
            })

    return sources


def build_research_queries(subject):
    """Create multiple searches for better research coverage."""

    return [
        f"{subject} overview",
        f"{subject} latest developments",
        f"{subject} applications advantages challenges",
    ]


def searcher_agent(plan: dict) -> dict:
    """
    Searcher Agent:
    Collects real research information based on the planner's output.

    Args:
        plan: dict produced by planner_agent

    Returns:
        dict containing research information and sources.
    """

    subject = plan.get("subject", "").strip()
    input_type = plan.get("input_type", "topic")
    mode = plan.get("mode", "Short Summary")

    if not subject:
        return {
            "status": "error",
            "message": "No research topic was provided.",
            "abstract": "",
            "key_findings": [],
            "methodology": "",
            "analysis": "",
            "conclusion": "",
            "sources": []
        }

    try:

        # ------------------------------------------------
        # CASE 1: USER PROVIDED A URL
        # ------------------------------------------------

        if input_type == "url":

            search_query = f'"{subject}"'

            web_results = search_web(
                search_query,
                num_results=5
            )

            web_sources = extract_web_sources(web_results)

            # Also search academically related information
            scholar_results = search_scholar(
                subject,
                num_results=5
            )

            scholar_sources = extract_scholar_sources(
                scholar_results
            )

            sources = web_sources + scholar_sources

            # Remove duplicate URLs
            unique_sources = []
            seen_urls = set()

            for source in sources:

                url = source.get("url")

                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_sources.append(source)

            sources = unique_sources

        # ------------------------------------------------
        # CASE 2: NORMAL TOPIC SEARCH
        # ------------------------------------------------

        else:

            queries = build_research_queries(subject)

            sources = []

            # Search multiple related queries
            for query in queries:

                results = search_web(
                    query,
                    num_results=5
                )

                sources.extend(
                    extract_web_sources(results)
                )

            # Academic search
            scholar_results = search_scholar(
                subject,
                num_results=5
            )

            sources.extend(
                extract_scholar_sources(
                    scholar_results
                )
            )

            # Remove duplicate URLs
            unique_sources = []
            seen_urls = set()

            for source in sources:

                url = source.get("url")

                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_sources.append(source)

            sources = unique_sources

        # ------------------------------------------------
        # CREATE RESEARCH TEXT FOR WRITER AGENT
        # ------------------------------------------------

        research_text = []

        for source in sources:

            title = source.get("title", "")
            snippet = source.get("snippet", "")
            source_type = source.get(
                "source_type",
                "Web"
            )

            research_text.append(
                f"[{source_type}] {title}\n"
                f"{snippet}"
            )

        combined_research = "\n\n".join(
            research_text
        )

        # ------------------------------------------------
        # RETURN STRUCTURED DATA
        # ------------------------------------------------

        return {

            "title": f"Research Report: {subject}",

            "abstract": (
                f"Research information collected for the topic "
                f"'{subject}' from multiple web and academic sources."
            ),

            "key_findings": [
                item.get("snippet", "")
                for item in sources[:8]
                if item.get("snippet")
            ],

            "methodology": (
                "Information was collected using web search "
                "and academic search results. Multiple queries "
                "were used to improve coverage and reduce "
                "dependence on a single source."
            ),

            "analysis": combined_research,

            "conclusion": (
                f"The collected sources provide information "
                f"about {subject}. The Writer Agent should "
                f"synthesize these sources into the requested "
                f"research format."
            ),

            "sources": sources,

            "source_count": len(sources),

            "mode": mode,

            "input_type": input_type,

            "subject": subject,

            "status": "Real research data collected successfully"
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e),
            "abstract": "",
            "key_findings": [],
            "methodology": "",
            "analysis": "",
            "conclusion": "",
            "sources": [],
            "source_count": 0,
            "mode": mode,
            "input_type": input_type,
            "subject": subject
        }
