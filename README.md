# AI Job Application Agent

A local career copilot for finding and ranking remote paid internships.

The first version is intentionally safe and practical:

- Parses your `.docx` resume for skills and project keywords.
- Searches through configured providers, or ingests pasted/manual job listings.
- Filters duplicate, unpaid, senior-only, and suspicious listings.
- Scores jobs against your resume and preferences.
- Generates application-ready cover letters, recruiter DMs, and short answers.
- Never submits an application automatically.

## Quick Start

```bash
python3 -m job_agent.cli run \
  --config config.example.json \
  --resume /Users/ayush/Downloads/Ayush_Singh_Resume-2.docx \
  --jobs data/sample_jobs.json \
  --limit 10
```

The report is written to `outputs/job_report.json` and `outputs/job_report.md`.

## Live Search

For reliable live internet search, set a SerpAPI key:

```bash
export SERPAPI_API_KEY="your_key"
python3 -m job_agent.cli search \
  --config config.example.json \
  --resume /Users/ayush/Downloads/Ayush_Singh_Resume-2.docx \
  --limit 10
```

Without a search key, use `--jobs` with JSON listings you export or paste from LinkedIn,
Internshala, Indeed, Instagram posts, or any other source.

## Safety

This agent can prepare application material, but it does not log into platforms,
bypass anti-bot protections, or submit applications without explicit human approval.

