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

Our Collaboration & Workflow Plan is maintained in `docs/collaboration-workflow-plan.md` within the team’s private GitHub repository. Keeping the plan in the repository gives all members access to the current version and allows updates to be tracked and reviewed through Git.

---

### 2. Task Tracking

We use GitHub Issues to allocate and track project tasks. Each work package is recorded as an issue containing a task description, completion criteria, relevant labels and an assigned team member. Pull requests are linked to their corresponding issues so that progress can be followed from allocation through review and completion.

We chose GitHub Issues because the project is already hosted on GitHub, so we do not need to manage another platform. It also provides a visible and traceable record of task ownership and completion. Most team members have previously used GitHub Issues, including in earlier university projects, and are familiar with the basic workflow.

---

## Language and Tooling

### 3. Implementation Language

---

### 4. Build and Dependency Management

---

## Technical Risks

### 5. Web Scraper Failures

---

### 6. External Factors

---

### 7. Testing Difficulty

---

### 8. Website Assumptions

---

## Team Practices

### 9. Responding to a Serious Bug

If a serious bug is discovered two days before the deadline, we will first reproduce it and record the relevant inputs, environment and observed behaviour. We will assess its severity, identify the affected parts of the application and prioritise the issue. Appropriate members will then investigate the cause and test the proposed fix.

The fix will be submitted through a pull request and reviewed by another team member. Where possible, a regression test will be added to reproduce the original failure and confirm that it has been corrected. We will avoid unrelated changes while resolving the bug and seek advice from our facilitator if we need additional support.

---

### 10. Definition of Finished

A feature will be considered finished when it satisfies its agreed requirements and acceptance criteria, produces the expected results and handles relevant error conditions. Its automated tests and agreed quality checks must pass, and any necessary documentation must be updated.

The change must also be submitted through a pull request, reviewed by someone other than the author and merged into the main branch. Writing the code alone is therefore not enough for a feature to be considered finished.

---

### 11. Resolving Disagreements

If two members disagree about whether the software is working correctly, we will compare its behaviour with the project specification and agreed requirements. We will reproduce the behaviour using the same input and environment and examine or create a test with a clearly defined expected result.

The decision will be based on the specification and observable evidence rather than personal preference. If the specification does not provide enough information to determine the correct behaviour, we will document the uncertainty and ask our facilitator for clarification.

---

## Code Quality

### 12. Type Checking and Linting

---

### 13. Failed Quality Checks

If a group member’s code does not pass the agreed linting or type-checking checks the merge will be blocked until the problems are fixed. The person who made the changes should correct the issues and run the checks again before requesting approval. If the failure is caused by an unusual case or a tool configuration problem, then the team can discuss it and agree on an exception.

This makes the checks part of our quality gate, rather than only giving warnings. It also helps prevent avoidable code-quality problems from being merged into the main branch.

---

## Testing Framework

### 14. Testing Framework

The group has chosen pytest as the testing framework, mainly because it is simpler to set up and use than Python’s built-in testing framework. A few team members have some basic familiarity with pytest, including using it for unit and integration testing, while others have limited experience with dedicated testing frameworks. This will therefore be an opportunity for the group to learn and share knowledge together.

---

## CI / Automation

### 15. Continuous Integration

We use GitHub Actions to run our tests automatically when code is pushed or a pull request is created. This allows us to catch problems early, before code is merged into the main branch. We can still do the tests manually while we are developing. However, the automated checks must pass before a pull request is merged.

Some of the group members have experience with continuous integration, others less so. One member has used GitHub Actions in a previous project. We can start with a simple workflow and help each other to understand how it works.

---

## Testing Mindset

### 16. Trying to Break the Scraper

---

### 17. Correctness of Output

Running without errors is not the same as producing the right result. To check this properly, a few real policy pages and documents will be reviewed and saved with known expected results. The program’s output can then be compared against these saved results. Using saved test data also means that testing will not depend only on live website content, which may change over time.

The program will also be tried on messy or broken inputs, such as missing files or dead links, to make sure it responds sensibly instead of quietly giving the wrong answer. The goal is to confirm that the program is getting things right, not just that it runs.

---

### 18. Evidence of Reliability

Evidence that would increase the team’s confidence in the software’s reliability includes:

* Results staying consistent when tests are run more than once
* Someone other than the person who made a change trying to find problems with it
* The program working properly on a different computer, not just the one on which it was developed
* The scraper handling a slow or unavailable website without unexpectedly failing
* Regression tests showing that old bugs have not reappeared after being fixed

---

### 19. Biggest Reliability Challenge

---

## Process and Standards

### 20. Code Review Process

We use pull requests for code review. Each important feature will be developed on a separate branch. When the work is complete, the team member will push the branch and create a pull request. At least one other team member will review the changes before they are merged into the main branch. The reviewer will look at the code, the tests, error handling and if the change meets the project requirements.

If any issues are discovered, the author will correct them before the pull request is approved. The code will not be merged until the review is complete and the required automated checks pass. This process will help us find problems early, keep the code quality consistent, and make sure more than one team member understands important changes.
