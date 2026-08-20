# CITS5501 Project 2026 – Phase 1 Report

## Planning and Organization

### 1. Collaboration & Workflow Plan

Where is your group’s Collaboration & Workflow Plan maintained? Is it in the Git repository, or elsewhere?

**Answer:**

---

### 2. Task Tracking

What tool or approach are you using to track assigned tasks and completion?

Why did you choose it?

Has anyone in the group used it before?

**Answer:**

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

1. 
2. 
3. 

What advantages do you expect your chosen language to give your team?

What disadvantages or risks do you expect?

If you had to implement this project in the other language, what do you think would be most difficult?

What might be easier?

**Answer:**

---

### 4. Build and Dependency Management

What build/dependency management tool will you use?

Examples:

- Python: `uv` or Poetry
- Java: Gradle or Maven
- Other suitable tool

Has anyone in the group used it before, or will this be the first time setting up a project with it?

**Answer:**

---

## Technical Risks

### 5. Web Scraper Failures

What parts of a web scraper do you expect could most easily fail, and how?

**Answer:**

---

### 6. External Factors

Which external factors could make your software stop working after it has been completed?

**Answer:**

---

### 7. Testing Difficulty

Which components of your project do you think will be easiest to test?

Which do you expect will be hardest?

**Answer:**

---

### 8. Website Assumptions

What assumptions is your software likely to make about the website it scrapes?

How could those assumptions be violated?

**Answer:**

---

## Team Practices

### 9. Responding to a Serious Bug

Suppose a serious bug is discovered two days before the deadline.

How would your team investigate and respond?

**Answer:**

---

### 10. Definition of Finished

What will convince your team that a feature is "finished"?

**Answer:**

---

### 11. Resolving Disagreements

If two group members disagree about whether software is "working correctly", how will you resolve that disagreement?

**Answer:**

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

---

### 17. Correctness of Output

How will you know that your software is producing the correct output, rather than merely some output?

**Answer:**

---

### 18. Evidence of Reliability

What evidence would increase your confidence that your software is reliable?

**Answer:**

---

### 19. Biggest Reliability Challenge

At this stage of the project, what do you think will be the biggest challenge in producing reliable software?

**Answer:**

---

## Process and Standards

### 20. Code Review Process

What will be your code review process?

Does someone other than the author review changes before merging, or is this informal?

We will use pull requests for code review. Each important feature will be developed on separate branch. When the work is complete, the team member will push the branch and create a pull request. At least one  other team members will review the changes and then merge it in the main branch. The reviewer will look at the code, the tests, error handling and if the change meets the project requirements.

If any issues are discovered, the author will correct them before the pull request is approved. The code will not be merged until the review is complete and the required automated checks pass. This process will help us find problems early, keep the code quality consistent, and make sure more than one team member understands important changes.