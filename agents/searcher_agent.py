"""
Searcher Agent
--------------
Collects information from free web and academic sources.

No SerpAPI key is required.

Uses:
- DuckDuckGo HTML search for web sources
- OpenAlex API for academic sources
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import time


# --------------------------------------------------
# WEB SEARCH
# --------------------------------------------------

def search_google(query, num_results=5):
    """
    Free web search using DuckDuckGo.

    This function keeps the same name as the old
    SerpAPI-based function so the rest of the project
    does not need major changes.
    """

    url = "https://html.duckduckgo.com/html/"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    response = requests.post(
        url,
        data={"q": query},
        headers=headers,
        timeout=15
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    sources = []

    results = soup.select(".result")

    for result in results[:num_results]:

        title_element = result.select_one(".result__a")
        snippet_element = result.select_one(".result__snippet")

        if not title_element:
            continue

        title = title_element.get_text(" ", strip=True)

        link = title_element.get("href", "")

        snippet = ""

        if snippet_element:
            snippet = snippet_element.get_text(
                " ",
                strip=True
            )

        if not title or not link:
            continue

        sources.append({
            "title": title,
            "url": link,
            "snippet": snippet,
            "year": "N/A",
            "venue": "Web",
            "source_type": "Web"
        })

    return sources


# --------------------------------------------------
# ACADEMIC SEARCH
# --------------------------------------------------

def search_scholar(query, num_results=5):
    """
    Free academic search using OpenAlex.

    No API key is required.
    """

    url = "https://api.openalex.org/works"

    params = {
        "search": query,
        "per-page": num_results,
        "sort": "relevance_score:desc"
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    sources = []

    for item in data.get("results", []):

        title = item.get("title", "")

        if not title:
            continue

        publication_year = item.get(
            "publication_year",
            "N/A"
        )

        doi = item.get("doi")

        primary_location = item.get(
            "primary_location"
        ) or {}

        landing_page = primary_location.get(
            "landing_page_url"
        )

        url = doi or landing_page or ""

        abstract = ""

        abstract_data = item.get(
            "abstract_inverted_index"
        )

        if abstract_data:

            words = []

            for word, positions in abstract_data.items():

                for position in positions:

                    words.append(
                        (position, word)
                    )

            words.sort()

            abstract = " ".join(
                word for _, word in words
            )

        concepts = item.get("concepts", [])

        venue = ""

        if concepts:
            venue = concepts[0].get(
                "display_name",
                ""
            )

        sources.append({
            "title": title,
            "url": url,
            "snippet": abstract[:1000],
            "year": publication_year,
            "venue": venue,
            "source_type": "Academic"
        })

    return sources


# --------------------------------------------------
# RESULT EXTRACTION
# --------------------------------------------------

def extract_google_results(results):
    """
    Kept for compatibility with the old project.

    The new search_google() already returns
    cleaned results, so simply return them.
    """

    return results


def extract_scholar_results(results):
    """
    Kept for compatibility with the old project.
    """

    return results


# --------------------------------------------------
# REMOVE DUPLICATES
# --------------------------------------------------

def remove_duplicates(sources):

    unique_sources = []

    seen_urls = set()
    seen_titles = set()

    for source in sources:

        url = source.get("url", "").strip()

        title = source.get(
            "title",
            ""
        ).strip().lower()

        if url and url in seen_urls:
            continue

        if title and title in seen_titles:
            continue

        if url:
            seen_urls.add(url)

        if title:
            seen_titles.add(title)

        unique_sources.append(source)

    return unique_sources


# --------------------------------------------------
# MAIN SEARCHER AGENT
# --------------------------------------------------

def searcher_agent(
    subject,
    input_type="Topic",
    mode="Detailed Research Report"
):
    """
    Main Searcher Agent.

    Searches multiple queries and combines
    web + academic sources.
    """

    try:

        if not subject or not subject.strip():

            return {
                "status": "error",
                "message": "Research topic cannot be empty.",
                "subject": subject,
                "sources": [],
                "source_count": 0,
                "key_findings": [],
                "analysis": ""
            }

        subject = subject.strip()

        # --------------------------------------------------
        # CREATE MULTIPLE SEARCH QUERIES
        # --------------------------------------------------

        queries = [
            subject,
            f"{subject} latest developments",
            f"{subject} applications",
            f"{subject} advantages disadvantages",
            f"{subject} challenges future"
        ]

        all_web_sources = []
        all_academic_sources = []

        # --------------------------------------------------
        # WEB SEARCH
        # --------------------------------------------------

        for query in queries:

            try:

                results = search_google(
                    query,
                    num_results=5
                )

                all_web_sources.extend(results)

                time.sleep(1)

            except Exception as e:

                print(
                    f"Web search failed for "
                    f"'{query}': {e}"
                )

        # --------------------------------------------------
        # ACADEMIC SEARCH
        # --------------------------------------------------

        academic_queries = [
            subject,
            f"{subject} applications",
            f"{subject} challenges"
        ]

        for query in academic_queries:

            try:

                results = search_scholar(
                    query,
                    num_results=5
                )

                all_academic_sources.extend(
                    results
                )

                time.sleep(1)

            except Exception as e:

                print(
                    f"Academic search failed for "
                    f"'{query}': {e}"
                )

        # --------------------------------------------------
        # COMBINE RESULTS
        # --------------------------------------------------

        sources = (
            all_web_sources +
            all_academic_sources
        )

        sources = remove_duplicates(
            sources
        )

        # --------------------------------------------------
        # LIMIT SOURCES
        # --------------------------------------------------

        sources = sources[:25]

        # --------------------------------------------------
        # CREATE FINDINGS
        # --------------------------------------------------

        findings = []

        for source in sources[:10]:

            snippet = source.get(
                "snippet",
                ""
            )

            if snippet:

                findings.append(
                    snippet
                )

        # --------------------------------------------------
        # CREATE RESEARCH SUMMARY
        # --------------------------------------------------

        research_summary = (
            f"Research was conducted on "
            f"'{subject}' using multiple web "
            f"search queries and academic "
            f"literature searches. "
            f"The collected sources cover "
            f"recent developments, applications, "
            f"advantages, challenges, and future "
            f"directions related to the topic."
        )

        # --------------------------------------------------
        # RETURN DATA FOR WRITER
        # --------------------------------------------------

        return {

            "title":
                f"Research Report: {subject}",

            "subject":
                subject,

            "input_type":
                input_type,

            "mode":
                mode,

            "abstract": (
                f"This research examines "
                f"{subject} using information "
                f"collected from multiple web "
                f"and academic sources. "
                f"The search focused on recent "
                f"developments, applications, "
                f"findings, challenges, and "
                f"future directions."
            ),

            "key_findings":
                findings,

            "methodology": (
                "Information was collected using "
                "multiple web searches and "
                "academic literature searches. "
                "DuckDuckGo was used for general "
                "web information and OpenAlex "
                "was used to identify academic "
                "literature. Duplicate sources "
                "were removed before preparing "
                "the research output."
            ),

            "analysis":
                research_summary,

            "conclusion": (
                f"The collected sources provide "
                f"multiple perspectives on "
                f"{subject}. The findings should "
                f"be evaluated using the original "
                f"sources provided in the report."
            ),

            "sources":
                sources,

            "source_count":
                len(sources),

            "status":
                "Research data collected successfully"
        }

    except Exception as e:

        return {

            "status": "error",

            "message": str(e),

            "subject": subject,

            "title":
                f"Research Report: {subject}",

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
