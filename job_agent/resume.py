from __future__ import annotations

import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from .models import ResumeProfile


KNOWN_SKILLS = [
    "HTML",
    "CSS",
    "JavaScript",
    "React",
    "Node.js",
    "Python",
    "Java",
    "C++",
    "Git",
    "GitHub",
    "Vercel",
    "REST APIs",
    "MySQL",
    "MongoDB",
    "Spring Boot",
    "Responsive Design",
    "UI/UX",
]


def parse_docx_text(path: str | Path) -> str:
    docx_path = Path(path)
    with zipfile.ZipFile(docx_path) as archive:
        xml = archive.read("word/document.xml")

    root = ElementTree.fromstring(xml)
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs: list[str] = []
    for paragraph in root.findall(".//w:p", namespace):
        pieces = [node.text or "" for node in paragraph.findall(".//w:t", namespace)]
        text = "".join(pieces).strip()
        if text:
            paragraphs.append(text)
    return "\n".join(paragraphs)


def parse_resume(path: str | Path) -> ResumeProfile:
    text = parse_docx_text(path)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    name = lines[0].title() if lines else ""

    email_match = re.search(r"[\w.+-]+@[\w.-]+\.\w+", text)
    phone_match = re.search(r"(?:\+91\s*)?\d[\d\s-]{8,}\d", text)

    skills = []
    lowered = text.lower()
    for skill in KNOWN_SKILLS:
        if skill.lower() in lowered:
            skills.append(skill)

    location = "India"
    for candidate in ["Lucknow", "Bangalore", "Delhi", "Mumbai", "Pune", "Hyderabad"]:
        if candidate.lower() in lowered:
            location = f"{candidate}, India"
            break

    return ResumeProfile(
        name=name,
        email=email_match.group(0) if email_match else "",
        phone=phone_match.group(0).strip() if phone_match else "",
        location=location,
        skills=skills,
        raw_text=text,
    )

