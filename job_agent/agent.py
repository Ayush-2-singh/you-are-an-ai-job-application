from __future__ import annotations

import json
from pathlib import Path

from .generator import add_application_materials
from .models import JobRecommendation, Preferences
from .providers import ManualJsonProvider, SerpApiProvider
from .resume import parse_resume
from .scoring import filter_and_rank


def load_preferences(path: str | Path) -> Preferences:
    return Preferences.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def run_agent(
    config_path: str | Path,
    resume_path: str | Path,
    jobs_path: str | Path | None,
    limit: int,
    live_search: bool = False,
) -> list[JobRecommendation]:
    preferences = load_preferences(config_path)
    resume = parse_resume(resume_path)

    jobs = []
    if jobs_path:
        jobs.extend(ManualJsonProvider(jobs_path).fetch())
    if live_search:
        jobs.extend(SerpApiProvider().fetch(preferences, limit=limit * 2))

    ranked = filter_and_rank(jobs, resume, preferences, limit)
    return [add_application_materials(item, resume) for item in ranked]


def write_outputs(recommendations: list[JobRecommendation], output_dir: str | Path) -> tuple[Path, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    json_path = output_path / "job_report.json"
    md_path = output_path / "job_report.md"

    json_path.write_text(
        json.dumps([item.to_dict() for item in recommendations], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    md_path.write_text(_to_markdown(recommendations), encoding="utf-8")
    return json_path, md_path


def _to_markdown(recommendations: list[JobRecommendation]) -> str:
    lines = ["# Job Recommendations", ""]
    for index, item in enumerate(recommendations, start=1):
        job = item.job
        lines.extend(
            [
                f"## {index}. {job.role} - {job.company}",
                "",
                f"- Match score: {item.match_score}/100",
                f"- Platform: {job.platform}",
                f"- Location: {job.location}",
                f"- Salary: {job.salary or 'Not listed'}",
                f"- Required skills: {', '.join(job.required_skills) or 'Not listed'}",
                f"- Apply: {job.apply_link}",
                f"- Reason: {item.reason}",
                "",
                "### Recruiter Message",
                item.recruiter_message,
                "",
                "### Why Should We Hire You?",
                item.why_hire_answer,
                "",
            ]
        )
    return "\n".join(lines)

