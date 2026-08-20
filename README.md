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

The project is currently in **Phase 1: Planning and Organisation**.

During Phase 1, the team is establishing its:

* Collaboration and communication process
* Task-tracking approach
* Version-control workflow
* Implementation language and development tools
* Code-review and quality practices
* Testing strategy
* Technical and resource risk-management approach

Implementation and testing of the application will take place during Phase 2.

## Repository contents

* [`phase1_report/`](./phase1_report/) – Phase 1 report and related files
* [`README.md`](./README.md) – Project overview and repository guide

The Phase 1 report will be maintained in Markdown and submitted in both Markdown and PDF formats.

## Team

* Roshan Sada Shanker
* Nuwanga Niroshan Hewa Wiladdarage
* Cam Zhou
* Sharmel Rayen Remington Villava Rayen
* Swathy Shenoy

Student numbers and repository usernames are recorded in the Phase 1 report as required by the project specification.

## Collaboration

All team members will contribute through version control. Tasks will be allocated and tracked, and changes will be reviewed before being merged into the main branch.

The team’s detailed communication, task-management, version-control and resource-risk practices will be recorded in the Collaboration & Workflow Plan.

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
