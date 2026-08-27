"""
Searcher Agent
--------------
Collects real information from web sources
and academic sources based on the research topic.
"""

import os
import time
import serpapi


def get_api_key():
    """
    Get SerpApi key.

    Works with:
    - Streamlit Cloud secrets
    - Local environment variables
    """

    try:
        import streamlit as st

        if "SERPAPI_KEY" in st.secrets:
            return st.secrets["SERPAPI_KEY"]
    except Exception:
        pass

    return os.getenv("SERPAPI_KEY")


def search_google(query, num_results=5):
    """Search Google using SerpApi."""

    api_key = get_api_key()

    if not api_key:
        raise ValueError(
            "SERPAPI_KEY is missing. "
            "Add it to Streamlit Secrets."
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
    """Search Google Scholar."""

    api_key = get_api_key()

    if not api_key:
        raise ValueError(
            "SERPAPI_KEY is missing. "
            "Add it to Streamlit Secrets."
        )

    client = serpapi.Client(api_key=api_key)

    results = client.search({
        "engine": "google_scholar",
        "q": query,
        "num": num_results,
        "hl": "en"
    })

    return results


def extract_google_results(results):
    """Extract Google search results."""

    sources = []

    for item in results.get("organic_results", []):

        title = item.get("title", "")
        url = item.get("link", "")
        snippet = item.get("snippet", "")

        if not title or not url:
            continue

        sources.append({
            "title": title,
            "url": url,
            "snippet": snippet,
            "year": item.get("date", "N/A"),
            "venue": "Web",
            "source_type": "Web"
        })

    return sources


def extract_scholar_results(results):
    """Extract academic search results."""

    sources = []

    for item in results.get("organic_results", []):

        title = item.get("title", "")
        url = item.get("link", "")
        snippet = item.get("snippet", "")

        publication_info = item.get(
            "publication_info",
            {}
        )

        publication_summary = publication_info.get(
            "summary",
            ""
        )

        if not title:
            continue

        sources.append({
            "title": title,
            "url": url,
            "snippet": snippet,
            "year": "N/A",
            "venue": publication_summary,
            "source_type": "Academic"
        })

    return sources


def remove_duplicates(sources):
    """Remove duplicate URLs."""

    unique = []
    seen = set()

    for source in sources:

        url = source.get("url", "")

        if url and url not in seen:
            seen.add(url)
            unique.append(source)

    return unique


def searcher_agent(plan: dict) -> dict:
    """
    Searcher Agent.

    Performs real web and academic searches and returns
    information in the format expected by writer_agent.py.
    """

    time.sleep(0.5)

    subject = plan.get("subject", "").strip()
    input_type = plan.get("input_type", "topic")
    mode = plan.get("mode", "Short Summary")

    if not subject:
        return {
            "status": "error",
            "message": "No research topic was provided.",
            "subject": "",
            "sources": [],
            "key_findings": []
        }

    try:

        sources = []

        # --------------------------------------------------
        # NORMAL TOPIC SEARCH
        # --------------------------------------------------

        if input_type != "url":

            queries = [
                subject,
                f"{subject} latest research",
                f"{subject} applications challenges",
            ]

            for query in queries:

                results = search_google(
                    query,
                    num_results=5
                )

                sources.extend(
                    extract_google_results(results)
                )

            # Academic research
            scholar_results = search_scholar(
                subject,
                num_results=5
            )

            sources.extend(
                extract_scholar_results(
                    scholar_results
                )
            )

        # --------------------------------------------------
        # URL / PAPER SEARCH
        # --------------------------------------------------

        else:

            results = search_google(
                subject,
                num_results=5
            )

            sources.extend(
                extract_google_results(results)
            )

            scholar_results = search_scholar(
                subject,
                num_results=5
            )

            sources.extend(
                extract_scholar_results(
                    scholar_results
                )
            )

        # Remove duplicates
        sources = remove_duplicates(sources)

        # --------------------------------------------------
        # IF NOTHING WAS FOUND
        # --------------------------------------------------

        if not sources:

            return {
                "status": "error",
                "message": (
                    f"No search results found for '{subject}'."
                ),
                "subject": subject,
                "sources": [],
                "key_findings": []
            }

        # --------------------------------------------------
        # BUILD ACTUAL RESEARCH CONTENT
        # --------------------------------------------------

        findings = []

        for source in sources[:8]:

            snippet = source.get(
                "snippet",
                ""
            ).strip()

            if snippet:

                findings.append(snippet)

        # Use first few results as the research summary
        summary_parts = []

        for source in sources[:5]:

            title = source.get("title", "")
            snippet = source.get("snippet", "")

            if snippet:

                summary_parts.append(
                    f"{title}: {snippet}"
                )

        research_summary = "\n\n".join(
            summary_parts
        )

        # --------------------------------------------------
        # RETURN DATA FOR WRITER
        # --------------------------------------------------

        return {

            "title": f"Research Report: {subject}",

            "subject": subject,

            "input_type": input_type,

            "mode": mode,

            "abstract": (
                f"This research examines {subject} "
                f"using information collected from "
                f"multiple web and academic sources. "
                f"The search focused on recent developments, "
                f"applications, findings, and challenges "
                f"related to the topic."
            ),

            "key_findings": findings,

            "methodology": (
                "Information was collected through "
                "multiple web searches and academic "
                "literature searches. Results from "
                "different queries were combined and "
                "duplicate sources were removed."
            ),

            "analysis": research_summary,

            "conclusion": (
                f"The collected research provides "
                f"multiple perspectives on {subject}. "
                f"The findings and source information "
                f"should be considered together when "
                f"evaluating the topic."
            ),

            "sources": sources,

            "source_count": len(sources),

            "status": (
                "Research data collected successfully"
            )
        }

    except Exception as e:

        # IMPORTANT:
        # Do not silently return empty sections.

        return {
            "status": "error",
            "message": str(e),
            "subject": subject,
            "title": f"Research Report: {subject}",
            "abstract": "",
            "key_findings": [],
            "methodology": "",
            "analysis": "",
            "conclusion": "",
            "sources": [],
            "source_count": 0,
            "mode": mode,
            "input_type": input_type
        }
