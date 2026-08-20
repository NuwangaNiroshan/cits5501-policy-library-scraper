# CITS5501 Project 2026 – Phase 1 Report

**Repository URL:** [https://github.com/NuwangaNiroshan/cits5501-policy-library-scraper](https://github.com/NuwangaNiroshan/cits5501-policy-library-scraper)

## Group Members

| Full Name | Student Number | GitHub Username |
| :--- | :--- | :--- |
| Roshan Shanker | 24819852 | `Roshss2508` |
| Nuwanga Niroshan Hewa Wiladdarage | 24684008 | `NuwangaNiroshan` |
| Cam Zhou | 24349432 | `camzhou831-star` |
| Sharmel Rayen Remington Villava Rayen | 25079168 | `SharmelRayen` |
| Swathy Shenoy | 25068786 | `Swathymahesh` |

---

## Planning and Organization

### 1. Collaboration & Workflow Plan

Where is your group’s Collaboration & Workflow Plan maintained? Is it in the Git repository, or elsewhere?

**Answer:**

Our Collaboration & Workflow Plan is maintained in docs/collaboration-workflow-plan.md within the team’s private GitHub repository. Keeping the plan in the repository gives all members 
access to the current version and allows updates to be tracked and reviewed through Git.

---

### 2. Task Tracking

What tool or approach are you using to track assigned tasks and completion?

Why did you choose it?

Has anyone in the group used it before?

**Answer:**

We use GitHub Issues to allocate and track project tasks. Each work package is recorded as an issue containing a task description, completion criteria, relevant labels and an assigned 
team member. Pull requests are linked to their corresponding issues so that progress can be followed from allocation through review and completion.

We chose GitHub Issues because the project is already hosted on GitHub, so we do not need to manage another platform. It also provides a visible and traceable record of task ownership and 
completion. Most team members have previously used GitHub Issues, including in earlier university projects, and are familiar with the basic workflow.

---

## Language and Tooling

### 3. Implementation Language

Which language has your group chosen?

Have any members of the group not used it – and if so, how will they get familiar with it?

#### Factors Influencing the Language Choice

Rank the top three factors in order of importance:

- Familiarity with the language
- Team members’ experience
- Library support
- Ease of debugging
- Performance
- Maintainability
- Assessment considerations
- Career value
- Other (explain)

**Top three factors:**

1. Library support
2. Familiarity with the language
3. Ease of debugging

What advantages do you expect your chosen language to give your team?

What disadvantages or risks do you expect?

If you had to implement this project in the other language, what do you think would be most difficult?

What might be easier?

**Answer:**

The group has chosen Python. *(To be confirmed with everyone. If any member has not used Python before, we will note here how they plan to get up to speed, e.g. pairing on early tasks and working through the official tutorial.)*

Why these three factors, in this order:

1. **Library support.** The project is scraping plus document parsing (PDF, Word, RTF), and Python has mature, well-documented libraries for every step: `httpx` or `requests` for HTTP, `pypdf` for PDF, `python-docx` for Word. One member has built a FastAPI backend that relied on `httpx` and `python-docx` in production and found them solid. Java has equivalents (Apache PDFBox, Apache POI) but they generally need more setup and more code for the same task.
2. **Familiarity with the language.** Python is the language most of the group has in common *(confirm per member)*. One member has completed two Python projects with pytest suites (a FastAPI backend with acceptance and end-to-end tests, and a smaller CLI tool), so the testing workflow this unit focuses on is something the group has already done in Python.
3. **Ease of debugging.** No compile step, a REPL for poking at a half-parsed document, and readable stack traces. In scraping work most "bugs" are surprises in external data, and the quickest way to diagnose them is to inspect real responses interactively.

Advantages we expect: fast iteration, concise code so more effort goes into behaviour and tests instead of boilerplate, and pytest's low setup cost makes it easier for every member to write tests.

Disadvantages and risks: with dynamic typing, mistakes such as wrong argument types, misspelled attributes or `None` leaking through only show up at runtime. In a five-person codebase that is a real integration risk, which is the main reason we plan to run a type checker in CI (see Q12). Performance is a theoretical disadvantage but not a practical one here, since the bottleneck of a scraper is the network, not the interpreter.

If we had to use Java instead, the hardest part for us would be the build and dependency toolchain (nobody in the group has real Gradle or Maven experience *(confirm)*), and the amount of boilerplate for a small CLI tool. What would be easier in Java is that the compiler and static typing catch integration mistakes at build time for free. In Python we have to opt in to that via mypy, which is what we intend to do.

---

### 4. Build and Dependency Management

What build/dependency management tool will you use?

Examples:

- Python: `uv` or Poetry
- Java: Gradle or Maven
- Other suitable tool

Has anyone in the group used it before, or will this be the first time setting up a project with it?

**Answer:**

We will use `uv`, for three reasons:

1. The marking environment has `uv` pre-installed, so our setup instructions can be a single command (`uv sync`) with no bootstrap step.
2. It keeps a lockfile (`uv.lock`), so every member and the CI runner install identical dependency versions.
3. It is fast enough that a clean install in CI takes seconds rather than minutes.

This will be the first time any of us has used `uv` on a real project *(confirm per member)*. The underlying ideas are familiar though. One member's FastAPI project pins every dependency to an exact version in `requirements.txt`, and a monorepo project they work on pins the package manager version and runs frozen installs in CI, so the build fails if the lockfile and manifest disagree instead of silently installing something newer. `uv` is a more integrated version of the same pin, lock, frozen-install workflow, so we expect the learning curve to be short. One member will set up the initial `pyproject.toml` and lockfile so everyone else starts from a working template.

---

## Technical Risks

### 5. Web Scraper Failures

What parts of a web scraper do you expect could most easily fail, and how?

**Answer:**

HTML parsing is the component most likely to fail. CSS selectors and XPath queries break silently if the website’s underlying markup changes. The scraper is also fragile due to:

* **Network issues:** Timeouts, connection resets, and non-200 HTTP responses.
* **Document parsing problems:** Corrupted, password-protected/encrypted, or scanned non-searchable PDF, DOCX, or RTF documents.
* **Character encoding mismatches:** Inconsistent character encodings (e.g., UTF-8 vs ISO-8859-1) that can corrupt document titles and text without raising an explicit crash.

---

### 6. External Factors

Which external factors could make your software stop working after it has been completed?

**Answer:**

Several external factors outside our direct control could cause the software to stop functioning:

* **Website redesigns & URL changes:** Alterations to DOM element hierarchies, CSS class names, or URL routing and pagination schemes.
* **Anti-bot measures & access restrictions:** Introduction of rate limits, IP blocking, CAPTCHAs, or changes requiring user authentication/login.
* **Client-side rendering:** Migration to dynamic JavaScript-rendered single-page application (SPA) architectures that require browser execution.
* **Network & environment changes:** Server-side TLS/SSL certificate changes, deprecation of upstream HTTP/parsing libraries, or breaking runtime updates in Python.

---

### 7. Testing Difficulty

Which components of your project do you think will be easiest to test?

Which do you expect will be hardest?

**Answer:**

* **Easiest to test:** Pure, deterministic logic that operates without network or filesystem dependencies. This includes CLI argument parsing, query string validation, and document parsing against static, local test fixtures.
* **Hardest to test:** The live HTTP network layer, retry and backoff timing logic, and error paths for transient network failures (e.g., dropped connections, timeouts, partial downloads). Testing these reliably requires mock servers and simulated network faults rather than hitting the live university website.

---

### 8. Website Assumptions

What assumptions is your software likely to make about the website it scrapes?

How could those assumptions be violated?

**Answer:**

Our software makes several key assumptions about the target website:

* **Structural stability:** Assuming that HTML markup structure, element IDs, and CSS classes remain consistent.
* **Protocol & metadata validity:** Assuming HTTP status codes are used accurately (e.g., 404 for missing pages) and that `Content-Type` headers correctly match the actual file content.
* **Document integrity:** Assuming linked policy documents are well-formed and accessible directly via static HTTP GET requests without requiring JavaScript execution or session cookies.

These assumptions can be violated at any time without prior notice if the website administrators update the CMS, restructure URL paths, or alter document hosting practices.

---

## Team Practices

### 9. Responding to a Serious Bug

Suppose a serious bug is discovered two days before the deadline.

How would your team investigate and respond?

**Answer:**
If a serious bug is discovered two days before the deadline, we will first reproduce it and record the relevant inputs, environment and observed behaviour. We will assess its severity, 
identify the affected parts of the application and prioritise the issue. Appropriate members will then investigate the cause and test the proposed fix.

The fix will be submitted through a pull request and reviewed by another team member. Where possible, a regression test will be added to reproduce the original failure and confirm that it 
has been corrected. We will avoid unrelated changes while resolving the bug and seek advice from our facilitator if we need additional support.

---

### 10. Definition of Finished

What will convince your team that a feature is "finished"?

**Answer:**
A feature will be considered finished when it satisfies its agreed requirements and acceptance criteria, produces the expected results and handles relevant error conditions. Its automated 
tests and agreed quality checks must pass, and any necessary documentation must be updated.

The change must also be submitted through a pull request, reviewed by someone other than the author and merged into the main branch. Writing the code alone is therefore not enough for a 
feature to be considered finished.

---

### 11. Resolving Disagreements

If two group members disagree about whether software is "working correctly", how will you resolve that disagreement?

**Answer:**
If two members disagree about whether the software is working correctly, we will compare its behaviour with the project specification and agreed requirements. We will reproduce the 
behaviour using the same input and environment and examine or create a test with a clearly defined expected result.

The decision will be based on the specification and observable evidence rather than personal preference. If the specification does not provide enough information to determine the correct 
behaviour, we will document the uncertainty and ask our facilitator for clarification.

---

## Code Quality

### 12. Type Checking and Linting

#### Python Groups

Will you use a type checker such as:

- `mypy`
- `pyright`

If so, will it run in CI or just periodically/manually?

Has anyone used one before?

Do you plan to use a linter such as:

- `pylint`
- `black`

#### Java Groups

Is your team familiar with any static analysis/linting tools such as:

- Checkstyle
- SpotBugs
- PMD

Do you plan to use any?

**Answer:**

Yes to both. We will use `mypy` as the type checker and `ruff` as the linter (ruff also handles formatting, so we do not need black separately). Both will run in CI on every push and pull request as blocking checks, not just advisory ones. See Q13 and Q15 for how this fits with our merge policy and CI setup.

Nobody in the group has used mypy or ruff specifically *(confirm per member)*, but one member has run the equivalent workflow in TypeScript, which is where this plan comes from. Their browser-extension project runs the compiler in strict mode with a type-check-only script (`tsc --noEmit`) that must pass before a build ships, and a monorepo they contribute to runs a `typecheck` step in CI as a merge gate, alongside `shellcheck` for shell scripts. Two things we learned from running that setup and want to apply here:

1. Type checking catches integration mistakes between people, not just typos. If module A changes a return shape and module B does not notice, a strict type check fails immediately instead of it surfacing as a runtime bug days later. With five people writing separate parts of the scraper (fetcher, parsers, query engine), that is the kind of bug we would otherwise ship. It matters more in Python than in TypeScript because without mypy nothing else catches it before runtime (see the dynamic typing risk in Q3).
2. Checks only change behaviour if they are automatic and blocking. A linter people are supposed to run by hand stops being run in the week before a deadline, which is when it is needed most. Running mypy and ruff in CI costs seconds per push.

We will start with a small configuration that is strict on new code rather than trying to make every rule pass on day one, so the checks stay useful instead of becoming something people work around.

---

### 13. Failed Quality Checks

Suppose a group member’s contribution does not pass your linting or type-checking checks.

What will be the consequences?

Will merges be blocked if these checks fail, or will the checks be advisory only?

If a group member’s code does not pass the agreed linting or type-checking checks the merge should be blocked until the problems are fixed. The person who made the changes should correct the issues and run the checks again before requesting approval. If the failure is caused by an unusual case or a tool configuration problem, then the team can discuss it and agree on an exception.

This makes the checks part of our quality gate, rather than only giving warnings. It also helps prevent avoidable code-quality problems from being merged into the main branch.

---

## Testing Framework

### 14. Testing Framework

What test framework will you use?

Examples:

- Python: `pytest`
- Java: JUnit 5
- Other suitable framework

Has the group used it before, or only heard of it?

**Answer:**

The group has chosen pytest as the testing framework, mainly because it is simpler to set up and 
use than Python’s built-in testing framework. A few team members have some basic familiarity with 
pytest, including using it for unit and integration testing, while others have limited experience 
with dedicated testing frameworks. This will therefore be an opportunity for the group to learn and 
share knowledge together.

---

## CI / Automation

### 15. Continuous Integration

Will you set up continuous integration, such as GitHub Actions, to run your test suite automatically?

Or will you run tests manually before submission?

Have any members of your group used continuous integration before?

We use GitHub Actions to run our tests automatically when code is pushed or a pull request is created. This allows us to catch problems early, before code is merged into the main branch. We can still do the tests manually while we are developing. But the automatic checks will be the main check before merging them.

Some of the group members have experience with continuous integration, others less so. One member has used GitHub Actions in a previous project. We can start with a simple workflow and help each other to understand how it works.

---

## Testing Mindset

### 16. Trying to Break the Scraper

Suppose your scraper is finished and submitted.

Now imagine another student is trying to break your software and get it to exhibit failures or unexpected behaviour.

What might they try first?

**Answer:**

To find flaws in the application, another student might try:

* **Invalid CLI arguments:** Passing missing, contradictory, or unexpected command-line flags and arguments.
* **Network fault simulation:** Disconnecting the network during execution, introducing high latency/timeouts, or redirecting the tool to URLs returning 404/500 errors.
* **Malformed data inputs:** Pointing the scraper to corrupted, empty, or non-standard file types.
* **Concurrency and edge conditions:** Running multiple instances simultaneously against the same output directory or abruptly terminating the process (SIGINT/SIGTERM) mid-download.
* **Error stream leaks:** Checking whether error messages or unhandled stack traces are leaked to standard output (`stdout`) instead of standard error (`stderr`).

---

### 17. Correctness of Output

How will you know that your software is producing the correct output, rather than merely some output?

**Answer:**

Running without errors is not the same as producing the right result. To check this properly, a few 
real policy pages and documents will be reviewed and saved with known expected results. The 
program’s output can then be compared against these saved results. Using saved test data also means 
that testing will not depend only on live website content, which may change over time.

The program will also be tried on messy or broken inputs, such as missing files or dead links, to 
make sure it responds sensibly instead of quietly giving the wrong answer. The goal is to confirm 
that the program is getting things right, not just that it runs.

---

### 18. Evidence of Reliability

What evidence would increase your confidence that your software is reliable?

**Answer:**

Evidence that would increase the team’s confidence in the software’s reliability includes:

* Results staying consistent when tests are run more than once
* Someone other than the person who made a change trying to find problems with it
* The program working properly on a different computer, not just the one on which it was developed
* The scraper handling a slow or unavailable website without unexpectedly failing
* Regression tests showing that old bugs have not reappeared after being fixed

---

### 19. Biggest Reliability Challenge

At this stage of the project, what do you think will be the biggest challenge in producing reliable software?

**Answer:**

The biggest challenge is managing testing against an uncontrolled external dependency. Relying on the live website makes test suites slow, non-deterministic, and prone to flakiness, while relying solely on mocked tests risks making assumptions that do not reflect real-world site behaviors and failure modes. Balancing robust mock-based unit tests with realistic integration tests across three different document formats (PDF, Word, RTF) represents the primary reliability risk.

---

## Process and Standards

### 20. Code Review Process

What will be your code review process?

Does someone other than the author review changes before merging, or is this informal?

We will use pull requests for code review. Each important feature will be developed on separate branch. When the work is complete, the team member will push the branch and create a pull request. At least one  other team members will review the changes and then merge it in the main branch. The reviewer will look at the code, the tests, error handling and if the change meets the project requirements.

If any issues are discovered, the author will correct them before the pull request is approved. The code will not be merged until the review is complete and the required automated checks pass. This process will help us find problems early, keep the code quality consistent, and make sure more than one team member understands important changes.
