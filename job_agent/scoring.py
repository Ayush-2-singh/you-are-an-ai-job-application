from __future__ import annotations

import hashlib
import re

from .models import JobListing, JobRecommendation, Preferences, ResumeProfile


def dedupe_jobs(jobs: list[JobListing]) -> list[JobListing]:
    seen: set[str] = set()
    unique: list[JobListing] = []
    for job in jobs:
        identity = job.apply_link or f"{job.company}|{job.role}|{job.location}"
        digest = hashlib.sha256(identity.lower().encode("utf-8")).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        unique.append(job)
    return unique


def score_job(job: JobListing, resume: ResumeProfile, preferences: Preferences) -> JobRecommendation:
    text = " ".join(
        [
            job.company,
            job.role,
            job.platform,
            job.location,
            job.salary,
            job.description,
            " ".join(job.required_skills),
        ]
    ).lower()

    score = 25
    warnings: list[str] = []

    resume_skills = {skill.lower() for skill in resume.skills}
    job_skills = {skill.lower() for skill in job.required_skills}
    if job_skills:
        overlap = resume_skills & job_skills
        score += int(35 * (len(overlap) / max(len(job_skills), 1)))

    if any(role in text for role in preferences.target_roles):
        score += 10
    if any(location in text for location in preferences.preferred_locations):
        score += 8
    if any(term in text for term in ["paid", "stipend", "₹", "rs.", "inr"]):
        score += 8
    if any(term in text for term in ["fresher", "student", "intern", "recent graduate"]):
        score += 7

    preferred_hits = [term for term in preferences.preferred_terms if term.lower() in text]
    score += min(10, len(preferred_hits) * 2)

    for term in preferences.avoid_terms:
        if term.lower() in text:
            score -= 25
            warnings.append(f"Contains avoid term: {term}")

    if _looks_suspicious(text):
        score -= 30
        warnings.append("Possible scam risk: asks for fees or has vague compensation.")

    if "unpaid" in text:
        warnings.append("Unpaid listing; deprioritized.")

    reason = _build_reason(job, resume, preferred_hits, warnings)
    return JobRecommendation(job=job, match_score=max(0, min(score, 100)), reason=reason, warnings=warnings)


def filter_and_rank(
    jobs: list[JobListing], resume: ResumeProfile, preferences: Preferences, limit: int
) -> list[JobRecommendation]:
    recommendations = [score_job(job, resume, preferences) for job in dedupe_jobs(jobs)]
    recommendations = [
        item for item in recommendations if item.match_score >= preferences.min_match_score and "unpaid" not in item.warnings
    ]
    recommendations.sort(key=lambda item: item.match_score, reverse=True)
    return recommendations[: min(limit, preferences.application_limit)]


def _looks_suspicious(text: str) -> bool:
    patterns = [r"registration\s+fee", r"training\s+fee", r"pay\s+to\s+apply", r"guaranteed\s+job"]
    return any(re.search(pattern, text) for pattern in patterns)


def _build_reason(job: JobListing, resume: ResumeProfile, preferred_hits: list[str], warnings: list[str]) -> str:
    overlap = sorted(set(skill for skill in job.required_skills if skill.lower() in {s.lower() for s in resume.skills}))
    parts = []
    if overlap:
        parts.append(f"Strong overlap with your resume skills: {', '.join(overlap)}")
    if preferred_hits:
        parts.append(f"Matches preferences: {', '.join(preferred_hits[:5])}")
    if job.salary:
        parts.append(f"Compensation listed: {job.salary}")
    if warnings:
        parts.append(f"Review carefully: {'; '.join(warnings)}")
    return ". ".join(parts) or "Relevant internship based on role, remote preference, and skill match."
