from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Preferences:
    target_roles: list[str]
    preferred_locations: list[str]
    required_terms: list[str]
    preferred_terms: list[str]
    avoid_terms: list[str]
    platforms: list[str]
    min_match_score: int
    application_limit: int
    salary_expectation: str
    remote_preference: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Preferences":
        return cls(
            target_roles=list(data.get("target_roles", [])),
            preferred_locations=list(data.get("preferred_locations", [])),
            required_terms=list(data.get("required_terms", [])),
            preferred_terms=list(data.get("preferred_terms", [])),
            avoid_terms=list(data.get("avoid_terms", [])),
            platforms=list(data.get("platforms", [])),
            min_match_score=int(data.get("min_match_score", 65)),
            application_limit=int(data.get("application_limit", 10)),
            salary_expectation=str(data.get("salary_expectation", "")),
            remote_preference=str(data.get("remote_preference", "remote")),
        )


@dataclass
class ResumeProfile:
    name: str
    email: str
    phone: str
    location: str
    skills: list[str]
    raw_text: str


@dataclass
class JobListing:
    company: str
    role: str
    platform: str
    location: str
    salary: str
    description: str
    required_skills: list[str]
    apply_link: str
    source_id: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JobListing":
        return cls(
            company=str(data.get("company", "Unknown")),
            role=str(data.get("role", "Unknown Role")),
            platform=str(data.get("platform", "web")),
            location=str(data.get("location", "")),
            salary=str(data.get("salary", "")),
            description=str(data.get("description", "")),
            required_skills=list(data.get("required_skills", [])),
            apply_link=str(data.get("apply_link", "")),
            source_id=str(data.get("source_id", "")),
        )


@dataclass
class JobRecommendation:
    job: JobListing
    match_score: int
    reason: str
    warnings: list[str] = field(default_factory=list)
    cover_letter: str = ""
    recruiter_message: str = ""
    why_hire_answer: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["company"] = self.job.company
        data["role"] = self.job.role
        data["salary"] = self.job.salary or "Not listed"
        data["required_skills"] = self.job.required_skills
        data["application_link"] = self.job.apply_link
        return data

