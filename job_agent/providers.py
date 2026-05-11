from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

from .models import JobListing, Preferences


class ManualJsonProvider:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def fetch(self) -> list[JobListing]:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return [JobListing.from_dict(item) for item in data]


class SerpApiProvider:
    """Search provider for Google results through SerpAPI.

    This keeps browser automation out of the agent and avoids platform scraping.
    """

    endpoint = "https://serpapi.com/search.json"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY", "")

    def fetch(self, preferences: Preferences, limit: int) -> list[JobListing]:
        if not self.api_key:
            return []

        results: list[JobListing] = []
        for role in preferences.target_roles:
            query = f'{role} remote paid internship India apply LinkedIn Indeed Internshala'
            params = urllib.parse.urlencode(
                {
                    "engine": "google",
                    "q": query,
                    "api_key": self.api_key,
                    "num": min(limit, 10),
                }
            )
            with urllib.request.urlopen(f"{self.endpoint}?{params}", timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
            for item in payload.get("organic_results", []):
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                link = item.get("link", "")
                platform = _platform_from_link(link)
                results.append(
                    JobListing(
                        company=_guess_company(title),
                        role=_guess_role(title, role),
                        platform=platform,
                        location="Remote",
                        salary=_guess_salary(snippet),
                        description=snippet,
                        required_skills=_guess_skills(snippet),
                        apply_link=link,
                        source_id=link,
                    )
                )
        return results


def _platform_from_link(link: str) -> str:
    lowered = link.lower()
    for name in ["linkedin", "indeed", "internshala", "instagram", "wellfound"]:
        if name in lowered:
            return name
    return "web"


def _guess_company(title: str) -> str:
    if " at " in title:
        return title.split(" at ", 1)[1].split("|", 1)[0].strip()
    if " hiring " in title.lower():
        return title.split(" hiring ", 1)[0].strip()
    return "Unknown"


def _guess_role(title: str, fallback: str) -> str:
    if " at " in title:
        return title.split(" at ", 1)[0].strip()
    if " hiring " in title.lower():
        return title.lower().split(" hiring ", 1)[1].split(" in ", 1)[0].title()
    return fallback.title()


def _guess_salary(text: str) -> str:
    markers = ["₹", "stipend", "paid"]
    if any(marker.lower() in text.lower() for marker in markers):
        return "Mentioned in listing"
    return ""


def _guess_skills(text: str) -> list[str]:
    skills = ["HTML", "CSS", "JavaScript", "React", "Node.js", "Java", "Spring Boot", "MySQL", "Git"]
    lowered = text.lower()
    return [skill for skill in skills if skill.lower() in lowered]

