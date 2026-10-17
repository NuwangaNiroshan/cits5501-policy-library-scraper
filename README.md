# CITS5501 Policy Library Scraper

A CITS5501 group project focused on building and testing a reliable command-line application for retrieving and querying documents from an online policy library.

## Project overview

The completed application will retrieve policy documents in formats including PDF, Word and RTF, and allow users to query the retrieved content.

The project focuses on reliability and testing in an unpredictable web environment. Relevant conditions include:

* Temporary server unavailability
* Rate limiting
* Broken or redirected links
* Unexpected HTTP responses
* Malformed webpage content
* Changes to webpage structure
* Incomplete or unsupported documents

## Current status

The repository contains the completed **Phase 2** submission materials:

* a minimal policy-document scraper prototype;
* a written test-suite design covering the five required failure scenarios;
* fixtures and a working local HTTP test double;
* proposed adversarial inputs for testing another team's scraper; and
* the combined Phase 2 report in Markdown.

## Repository contents

* [`phase1_report/`](./phase1_report/) – Phase 1 report and related files
* [`phase2/prototype/`](./phase2/prototype/) – Task 1 scraper prototype
* [`phase2_report/phase2_report.md`](./phase2_report/phase2_report.md) – combined Phase 2 report
* [`phase2_report/`](./phase2_report/) – individual report sections for Tasks 1–4
* [`task3_artifacts/`](./task3_artifacts/) – Task 3 local test double, observations and instructions
* [`tests/`](./tests/) – automated smoke test and Task 3 artifact verification
* [`.github/workflows/ci.yml`](./.github/workflows/ci.yml) – CI pipeline (lint, type check, tests)
* [`README.md`](./README.md) – Project overview and repository guide

The Phase 2 report is maintained in Markdown and will be submitted in both Markdown and PDF formats.

## Team

* Roshan Shanker
* Nuwanga Niroshan Hewa Wiladdarage
* Cam Zhou
* Sharmel Rayen Remington Villava Rayen
* Swathy Shenoy

Student numbers and repository usernames are recorded in the Phase 1 report as required by the project specification.

## Collaboration

All team members will contribute through version control. Tasks will be allocated and tracked, and changes will be reviewed before being merged into the main branch.

The team’s detailed communication, task-management, version-control and resource-risk practices will be recorded in the Collaboration & Workflow Plan.

## Phase 2 – Task 1 prototype

`phase2/prototype/scrape_prototype.py` is the minimal scraper prototype for Phase 2 Task 1.

* **Python:** 3.10 or later (the CI version); it uses the standard library only.
* **Dependencies:** none for the prototype itself. `uv sync` is only needed for the lint, type-check and test commands below.
* **Network:** it needs internet access to reach the course policy site.

Run it from the repository root:

```bash
python3 phase2/prototype/scrape_prototype.py
```

It loads https://uwa-policy.cits5501.arranstewart.io/policy/, prints how many document links it found for each file type, then downloads up to 5 of them (cycling through up to five different file types). For each one it prints the URL, HTTP status, declared `Content-Type`, size in bytes, the first 16 bytes and an outcome (`OK`, `SUSPECT` or `FAILED`). Files are not saved to disk. A run takes about 20 seconds because the index and document requests are spaced 3.5 s apart so the live site does not receive rapid requests.

| Option | Default | Meaning |
|---|---|---|
| `--start-url URL` | course site | Index page to start from (e.g. `http://localhost:8000/policy/`) |
| `--max-docs N` | 5 | Number of documents to download (3–5) |
| `--max-requests N` | 20 | Hard cap on all HTTP requests: index, documents, redirect hops and retries (1–20; larger, zero or negative values are rejected) |
| `--delay S` | 3.5 | Seconds between requests |
| `--timeout S` | 15 | Per-request timeout |

The exit status is 0 only if at least 3 documents were downloaded and every one looks valid.

## Development setup

The project uses Python with [uv](https://docs.astral.sh/uv/) for dependency management (the marking environment ships with both). To set up and run the same checks CI runs:

```bash
uv sync            # install dependencies from uv.lock
uv run ruff check .   # lint
uv run mypy .         # type check
uv run pytest         # tests
```

Continuous integration runs these on every push to `main` and every pull request; merges are blocked if any check fails.

## Contribution workflow

### 1. Update the local main branch

```bash
git switch main
git pull origin main
```

### 2. Create a branch for the assigned task

Use a short and descriptive branch name. For example:

```bash
git switch -c docs/update-readme
or 
git checkout -b docs/update-readme
```

### 3. Make and review the changes

Before committing, check which files have changed and review the differences:

```bash
git status
git diff
```

### 4. Commit the relevant files

For example:

```bash
git add README.md
git commit -m "docs: update project README"
```

The file path and commit message should be changed to match the work being submitted.

### 5. Push the branch

For example:

```bash
git push -u origin docs/update-readme
```

### 6. Open a pull request

Open a pull request on GitHub and request a review from another team member. Address any review feedback before the changes are merged.

Changes should not be committed directly to the `main` branch.
