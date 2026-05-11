from __future__ import annotations

from .models import JobRecommendation, ResumeProfile


def add_application_materials(recommendation: JobRecommendation, resume: ResumeProfile) -> JobRecommendation:
    job = recommendation.job
    skills = ", ".join(resume.skills[:8])
    recommendation.why_hire_answer = (
        f"You should hire me because I have hands-on web development experience, including live deployed "
        f"projects and internship work. My background in {skills} helps me build responsive, practical "
        f"applications, and I am comfortable learning quickly, using Git, debugging issues, and contributing "
        f"to real project work as an intern."
    )
    recommendation.recruiter_message = (
        f"Hi, I'm {resume.name}. I'm interested in the {job.role} role at {job.company}. "
        f"I have hands-on experience with {skills}, including deployed web projects and a web developer "
        f"internship. I'd be grateful if you could review my profile for this opportunity."
    )
    recommendation.cover_letter = (
        f"Dear {job.company} Hiring Team,\n\n"
        f"I am excited to apply for the {job.role} position. I am currently building my software engineering "
        f"foundation through B.Tech coursework and hands-on projects, with practical experience in {skills}. "
        f"My recent work includes responsive websites, deployed applications, REST-oriented development, and "
        f"Git-based workflows.\n\n"
        f"This role interests me because it aligns closely with my goal of contributing to real engineering "
        f"projects while growing under experienced mentorship. I can bring consistency, curiosity, clean code "
        f"habits, and a strong willingness to learn.\n\n"
        f"Sincerely,\n{resume.name}"
    )
    return recommendation
