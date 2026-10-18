# CITS5501 - Phase II Report

**Unit:** Software Testing and Quality Assurance  
**Group:** 15  
**Repository:** [NuwangaNiroshan/cits5501-policy-library-scraper](https://github.com/NuwangaNiroshan/cits5501-policy-library-scraper)

| Student Number | Name                                  | GitHub ID       |
|----------------|---------------------------------------|-----------------|
| 24819852       | Roshan Shanker                        | Roshss2508      |
| 24684008       | Nuwanga Niroshan Hewa Wiladdarage     | NuwangaNiroshan |
| 24349432       | Cam Zhou                              | camzhou831-star |
| 25079168       | Sharmel Rayen Remington Villava Rayen | SharmelRayen    |
| 25068786       | Swathy Mahesh Shenoy                  | Swathymahesh    |

## Overview

The Phase 2 prototype and a variety of materials for the UWA policy-library scraper, including proposed test plans and ideas for adversarial tests, are all provided in this report. In addition to this, the repository contains the source code for the prototype, instructions for execution, the verification tests, and the double artifacts for the test created in Task 3.

## 1. Task 1 - Prototype

**Code:** `phase2/prototype/scrape_prototype.py` (instructions are available in the repository `README.md`).

### 1.1 What the Prototype Does

The prototype is a single Python script that uses only the standard library (`urllib` and `html.parser`).

1.  It sends one GET request to the index page at `https://uwa-policy.cits5501.arranstewart.io/policy/`. A `--start-url` option lets us point it at a local server for testing.

2.  It parses every `<a href>`, resolves each one against the index URL and drops the fragment. It keeps a link only if it is HTTP(S), on the same host as the index page, and has a document extension (`.pdf`, `.doc`, `.docx`, `.rtf`, `.odt`, `.xls`, `.xlsx`, `.ppt`, or `.pptx`). Duplicates are removed by exact URL. On the live index this gives **216 candidate links** (65 PDF, 96 DOC, 48 DOCX, 4 RTF, and 3 PPTX files).

3.  It picks five links (three to five via `--max-docs`), cycling through the extensions so that up to five different file types are tried, and downloads them.

4.  For each download it prints (a) the URL, (b) the HTTP status, (c) the declared `Content-Type`, (d) the size in bytes and (e) the first 16 bytes. It then gives an outcome: `OK` when the status is 200 *and* the leading bytes match the extension (`%PDF-` for PDF, `PK\x03\x04` for DOCX/PPTX, the eight-byte OLE2 header `D0 CF 11 E0 A1 B1 1A E1` for legacy DOC, and `{\rtf` for RTF). It reports `SUSPECT` when the status is 200 but the bytes do not match, and `FAILED` otherwise.

5.  Requests are limited by a hard budget of at most 20 (`--max-requests` accepts only 1-20). The budget counts every HTTP request: the index, each document, each redirect hop and each retry. The index and document requests are spaced 3.5 seconds apart, so the live site does not receive rapid requests; redirect hops follow immediately. On HTTP 429, the script waits for a numeric `Retry-After` value (capped at 15 seconds) and retries once, then gives up. The exit status is 0 only when at least three documents were downloaded and all of them look valid.

Live run on 17 Oct 2026 (abridged: entries 2–5 are condensed to one line each; 6 of 20 requests used):

```text
Found 216 candidate document links (.doc x96, .docx x48, .pdf x65, .pptx x3, .rtf x4)
```

| Document                                                   | HTTP status | Content-Type           | Size (bytes) | Leading signature (abridged) | Outcome            |
|------------------------------------------------------------|-------------|------------------------|-------------|------------------------------|--------------------|
| [1] .../policy-framework/policy-governance-framework.pdf | 200 | `application/pdf` | 301201 | `%PDF-1.6` | `OK (PDF signature)` |
| [2] .../delegations/delegations-framework-policy.doc | 200 | `application/msword` | 256512 | `D0 CF 11 E0 A1 B1 1A E1` | `OK (OLE2)` |
| [3] .../risk/risk-policy.docx | 200 | `...wordprocessingml...` | 154182 | `50 4B 03 04` | `OK (ZIP)` |
| [4] .../fraud-and-corruption-training.pptx | 200 | `...presentationml...` | 4298871 | `50 4B 03 04` | `OK (ZIP)` |
| [5] ...-domestic-postgraduate-students-policy.rtf | 200 | `application/rtf` | 207353 | `{\rtf` | `OK (RTF)` |

5/5 documents downloaded and look valid; 6/20 requests used.

### 1.2 Assumptions

- Every policy document is linked directly from the index page, so no recursive crawling is needed.

- A policy document is any same-host link whose path ends in one of the extensions listed above. Three document links that point to https://www.uwa.edu.au/... (the real UWA site) are treated as other websites and skipped.

- URLs are case-sensitive. We checked this: requesting a document path with different letter case returned 404, so the prototype does not merge links that differ only in case.

- Downloads are small enough to hold in memory (the largest we saw was about 4.3 MB).

### 1.3 Limitations

1.  **The validity check is shallow.** It looks only at the first few bytes. A file that begins with %PDF- but is truncated or corrupt is still reported as OK. It also cannot tell .docx from .xlsx or any other ZIP file, and it does not compare the declared Content-Type with the extension.

2.  **Link discovery depends on extensions and the current page layout.** Documents served from URLs without an extension (for example /download?id=42) are missed. Pages that build their links with JavaScript would also yield nothing. If fewer than 3 links are found the prototype prints a warning and exits with status 1, but it cannot tell a changed page layout from an index that really has no documents.

3.  **Error handling is minimal.** There is one timeout per request and one retry on 429 only. It has no retry with backoff for 5xx errors or timeouts, and an HTTP-date Retry-After is not parsed. It does not detect an index page whose HTML was truncated. A connection dropped part-way through a download is reported as FAILED, but the partial file is not resumed.

4.  **No persistence.** Nothing is saved or checksummed, so a rerun downloads everything again.

## 2. Task 2 - Design of Test Suite

### 2.1 Testing Objective

This set of test cases evaluates a fully operational policy-document scraper in terms of reliability and its response to various abnormal circumstances that can be encountered during operation. The test cases cover five specific scenarios, such as the scraping of a changed webpage, truncated HTML, timed out connections, HTTP client/server errors, and damaged or corrupted documents. The expected behaviour for each scenario is defined, and the test cases determine whether the scraper behaves appropriately and either recovers or reports a failure. The test cases are developed based on the Arrange-Act-Assert methodology and clearly define the steps needed for the test setup, the action to be taken and the final expected results.

### 2.2 Expected Scraper Behaviour

A reliable policy-document scraper should handle unexpected website conditions without crashing. It should not accept invalid documents or report misleading results. Where recovery is possible, it should continue processing. Otherwise, it should report the failure clearly.

The expected behaviour for each required scenario is outlined below.

| **Scenario**                          | **Expected Scraper Behaviour**                                                                                                                                                                                                                                                                            |
|---------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **1. Website structure changes**      | When changes to the HTML structure affect document discovery, the scraper should either identify the policy links using a supported alternative extraction method or clearly report an extraction failure. It should not incorrectly report successful extraction when no documents have been discovered. |
| **2. Truncated HTML**                 | The scraper should process incomplete HTML predictably. It may recover complete document links from the available content, but malformed or incomplete URLs must not be accepted. Detectable truncation should be reported.                                                                               |
| **3. Short- or long-term timeouts**   | Temporary timeouts may trigger limited retries. If the server remains unresponsive, the scraper should stop after the configured attempt limit and clearly report the failure without waiting indefinitely.                                                                                               |
| **4. HTTP 4xx and 5xx errors**        | The scraper should distinguish unsuccessful HTTP responses from successful downloads. Permanent errors such as 404 should normally be reported without retrying, while temporary server errors such as 503 may justify limited retries.                                                                   |
| **5. Invalid or corrupted documents** | The scraper should validate downloaded content rather than relying solely on HTTP status codes, filenames or declared content types. HTML returned instead of a PDF and corrupted documents should be rejected or clearly flagged.                                                                        |

For reproducibility, the proposed tests assume a two-second request timeout and a maximum of three total attempts for retriable failures, including the initial request. HTTP 404 responses are not retried. Individual document failures should be reported without preventing other valid documents from being processed. These are proposed production-testing expectations and are not necessarily implemented by the Phase 2 prototype.

### 2.3 Test Case Design

Eight test cases are proposed to evaluate the scraper under the five required failure scenarios. Each case specifies its purpose, required setup (Arrange), execution (Act), and observable expected outcome

(Assert). The tests are designed for a production-level scraper rather than the minimal prototype.

| **Test ID** | **Related Scenario**                  | **Test Purpose**                                                                                                                                        | **Arrange**                                                                                                                                                                                                                   | **Act**                                                                                          | **Assert**                                                                                                                                                                                                                                                             |
|-------------|---------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **T001**    | Scenario 1: Website structure changes | Verify that the scraper responds appropriately when changes to the HTML structure prevent its original extraction method from identifying policy links. | Prepare an HTML fixture containing three valid PDF URLs stored in data-document-url attributes of \<button\> elements instead of the original \<a href\> elements. Use the T001 fixture defined below.                        | Run the scraper against the modified index page.                                                 | The scraper either successfully extracts all three expected document URLs using a supported fallback method or clearly reports an extraction failure. Reporting successful extraction with zero documents is considered a failure.                                     |
| **T002**    | Scenario 2: Truncated HTML            | Verify that the scraper handles incomplete HTML without incorrectly extracting malformed document links.                                                | Configure a local server at http://127.0.0.1:3000/policy/ to return HTTP 200 with the exact truncated HTML fixture defined below. The response contains one complete PDF link followed by an unfinished anchor attribute.     | Run the scraper against the truncated index page and inspect the extracted URLs and diagnostics. | Under the proposed partial-recovery policy, the extracted URL set must contain only http://127.0.0.1:3000/documents/valid-policy.pdf. The unfinished URL must not be extracted or downloaded. The scraper must report the detectable incomplete HTML without crashing. |
| **T003**    | Scenario 3: Temporary timeout         | Verify that the scraper recovers from a temporary timeout using bounded retries.                                                                        | Configure a test server to exceed the two-second request timeout on the first attempt and return HTTP 200 with a valid PDF on the second attempt. Allow a maximum of three total attempts.                                    | Run the scraper and request the PDF document.                                                    | The first attempt times out, the second succeeds, and the scraper reports a successful download after exactly two attempts.                                                                                                                                            |
| **T004**    | Scenario 3: Prolonged timeout         | Verify that the scraper stops retrying when the server remains unresponsive.                                                                            | Configure a test server to delay every response beyond the two-second request timeout. Allow a maximum of three total attempts.                                                                                               | Run the scraper against the unresponsive endpoint.                                               | The scraper stops after three unsuccessful attempts, reports a timeout failure, and does not wait indefinitely or report a successful download.                                                                                                                        |
| **T005**    | Scenario 4: HTTP 4xx error            | Verify that the scraper correctly handles a missing document without affecting other valid downloads.                                                   | Configure one document endpoint to return HTTP 404 (Not Found) and another to return HTTP 200 with a valid PDF. Apply a policy that does not retry permanent 404 errors.                                                      | Run the scraper against an index containing both document links.                                 | The scraper records HTTP 404, reports the affected download as failed, and makes only one request to the missing document. The valid control document is downloaded successfully.                                                                                      |
| **T006**    | Scenario 4: HTTP 5xx error            | Verify that the scraper handles persistent server errors using bounded retries.                                                                         | Configure one document endpoint to return HTTP 503 (Service Unavailable) for every request, with no Retry-After header. Include a second endpoint returning a valid PDF. Allow three total attempts for the failing endpoint. | Run the scraper against an index containing both document links.                                 | The scraper makes three attempts to the failing endpoint, reports HTTP 503 as an unsuccessful download, and successfully processes the valid control document.                                                                                                         |
| **T007**    | Scenario 5: PDF link returns HTML     | Verify that the scraper rejects HTML content returned from a URL advertised as a PDF.                                                                   | Configure a .pdf endpoint to return HTTP 200 with Content-Type: text/html and an HTML error page instead of PDF data.                                                                                                         | Run the scraper and attempt to download the supposed PDF.                                        | The scraper detects the unexpected content type, rejects the HTML response, and reports an invalid document rather than a successful PDF download.                                                                                                                     |
| **T008**    | Scenario 5: Corrupted PDF             | Verify that the scraper detects a corrupted PDF even when its filename, declared content type and initial bytes appear correct.                         | Configure a server to return HTTP 200 with Content-Type: application/pdf and corrupted PDF data beginning with %PDF- that cannot be opened by a PDF parser.                                                                   | Run the scraper and validate the downloaded content.                                             | The scraper detects the invalid PDF structure, reports a document-validation failure, and does not incorrectly classify the corrupted document as a successful download.                                                                                               |

#### Controlled HTML Fixtures for T001 and T002

The following fixtures specify the input conditions for T001 and T002 so that another student or teaching staff member can reproduce the tests.

##### T001 - Modified Website Structure

Use the following HTML as the modified policy index:

```html
<html>
<body>
  <button data-document-url="/documents/academic-policy.pdf">
    Academic Policy
  </button>
  <button data-document-url="/documents/privacy-policy.pdf">
    Privacy Policy
  </button>
  <button data-document-url="/documents/student-conduct.pdf">
    Student Conduct Policy
  </button>
</body>
</html>
```

When served from http://127.0.0.1:3000/policy/, the expected document URLs are:

1.  `http://127.0.0.1:3000/documents/academic-policy.pdf`

2.  `http://127.0.0.1:3000/documents/privacy-policy.pdf`

3.  `http://127.0.0.1:3000/documents/student-conduct.pdf`

The test passes if the scraper discovers all three URLs through a supported fallback mechanism or explicitly reports that document extraction failed. It fails if the scraper silently reports successful extraction with zero documents.

##### T002 - Truncated HTML Response

Configure the local server to return the following exact HTML content:

```html
<html><body><a href="/documents/valid-policy.pdf">Valid policy</a><a href="/documents/broken
```

The HTML contains one complete anchor element followed by a second anchor with an unfinished href attribute.

The expected extracted URL set under the proposed partial-recovery policy is:

`http://127.0.0.1:3000/documents/valid-policy.pdf`

The scraper must not extract or download the incomplete `/documents/broken` link. It should identify and report the detectable incomplete HTML while preserving the valid link.

### 2.4 Test Coverage and Rationale

The proposed test suite contains eight test cases covering all five failure scenarios specified in the project requirements. T001 examines structural changes affecting document discovery, while T002 evaluates incomplete HTML processing using a reproducible fixture and expected URL set. T003 and T004 distinguish temporary connection failures from prolonged unavailability. T005 and T006 test HTTP client and server errors, including the continuation of valid downloads after individual failures. T007 and T008 examine different document-validation problems: incorrect response content and corrupted PDF structures.

Controlled fixtures and simulated server responses are proposed to make these conditions repeatable without depending on unpredictable failures in the live website. The test suite evaluates appropriate recovery, bounded retry behaviour, document validation and accurate failure reporting. These are proposed tests, not claims that the production-level behaviours have already been implemented or executed.

## 3. Task 3 - Fixtures and Test Doubles

### 3.1 Fixtures and Testing Oracle

Fixtures are fixed files, test data, or controlled environments that can be reused during testing. They allow us to test the scraper using known inputs instead of depending only on the live website.

Useful fixtures for this project could include:

- Saved HTML pages

- Valid policy documents

- Invalid or corrupted policy documents

- Files with known content

- Responses from a controlled local server

The **fixture or test double** provides the controlled input or environment for the test. The **test oracle** provides the expected result that is used to decide whether the scraper behaved correctly.

For example, our local test double provides a URL ending in .pdf but deliberately returns HTML. The expected result is known before the test is run:

- The HTTP status is 200

- The declared content type is text/html

- The response contains HTML

- The response does not begin with the %PDF signature

A scraper should therefore not accept this response as a valid PDF document.

Because both the input and expected result are known, the same test can be repeated with the same expected outcome. This also avoids depending on live website content, which may change over time.

### 3.2 Live-Site Request Observations

We carried out a small test to see whether the policy website showed any clear request limiting.

Five requests were sent to the policy index page, with a two-second delay between each request.

The results were:

| **Request** | **HTTP status** | **Response time (s)** | **Download size (bytes)** |
|-------------|-----------------|-----------------------|---------------------------|
| 1           | 200             | 0.970394              | 584187                    |
| 2           | 200             | 1.077670              | 584187                    |
| 3           | 200             | 0.869424              | 584187                    |
| 4           | 200             | 0.959649              | 584187                    |
| 5           | 200             | 1.151368              | 584187                    |

All five requests returned HTTP status 200.

The response size was the same for every request, and the response times were also similar. We did not observe any clear sign of request limiting during this small test.

However, this does not prove that the website has no request limits. The website may behave differently if more requests are sent or if requests are sent more quickly.

For automated testing, we should avoid sending many requests to the live website. Fixtures, mocks, and controlled local servers can be used instead. This reduces unnecessary requests to the real server and makes the tests more repeatable.

The request observations are recorded in:

`task3_artifacts/observations/request_limit_check.txt`

### 3.3 Use of Test Doubles

A test double can replace the real website or network connection during testing. This allows us to create failure conditions in a controlled and repeatable way instead of waiting for the real website to fail.

In Python, tools such as `unittest.mock`, pytest's `monkeypatch`, and controlled local HTTP servers can be used to create test doubles.

Test doubles could simulate the following conditions:

- **Timeouts:** a mock can raise a timeout error.

- **Connection failures:** a mock can raise a connection error instead of contacting the real server.

- **Slow responses:** a controlled local server can delay its response.

- **Interrupted downloads:** a controlled server can start sending data and then close the connection before the download is complete.

These conditions are difficult to reproduce reliably using the live website because we do not control the real server.

Using test doubles also allows the Task 2 failure scenarios to be tested repeatedly without requiring the real website to fail at the correct time.

### 3.4 Test-Double Artifact - Incorrect Content for a PDF Link

The artifact is located at:

`task3_artifacts/wrong_content_server.py`

It provides a controlled HTTP endpoint:

`/fake-policy.pdf`

Although the URL ends in .pdf, the server deliberately returns:

- HTTP 200

- Content-Type: text/html; charset=utf-8

- HTML content instead of PDF content

- no %PDF file signature

This behaves like a controlled stub because it always returns a known response for the selected endpoint.

Run the artifact with:

```bash
python3 task3_artifacts/wrong_content_server.py
```

Then check the response with:

```bash
curl -i http://127.0.0.1:8000/fake-policy.pdf
```

If port 8000 is already being used, another port can be selected:

```bash
python3 task3_artifacts/wrong_content_server.py --port 8010
```

### 3.5 Automated Verification

The automated test is located at:

`tests/test_task3_wrong_content_server.py`

The test starts the controlled HTTP server on an available local port and verifies that:

- the response status is HTTP 200

- the content type is HTML

- the body contains HTML

- the body does not start with the %PDF signature

The server is then shut down automatically.

The test can be run with:

```bash
uv run pytest tests/test_task3_wrong_content_server.py -v
```

The full project checks are:

```bash
uv run pytest
uv run ruff check .
uv run mypy .
```

#### Expected Scraper Behaviour

A scraper should not assume that a URL ending in .pdf contains a valid PDF.

The response should also be checked using information such as:

- HTTP status

- Content-Type

- file signature or first bytes

- expected document format

A normal PDF commonly starts with %PDF. The controlled response instead contains HTML and does not contain this PDF signature.

The current automated test verifies the behaviour of the test double itself. Once the Task 1 scraper is integrated, this test double can also be used as controlled input to verify that the scraper detects and rejects the invalid PDF response.

### 3.6 Why the Live Website Is Not Suitable for This Test

The live policy website normally serves real policy documents.

We cannot make the real server return HTML from a .pdf URL exactly when a test requires that failure. Even if this problem occurred naturally, we would not know when it would happen and could not reproduce it consistently.

Trying to create failures against the live server would also be inappropriate and could generate unnecessary traffic.

The local test double gives us a safe, predictable and repeatable way to test the same failure scenario.

## 4. Task 4 - Adversarial Inputs

A scraper may work correctly on ordinary pages while making assumptions about URLs, document identity, response sizes and filenames. To test another team's scraper, we would construct unusual but controlled inputs that challenge these assumptions.

The following eight ideas are proposed tests, rather than results from tests already performed. Each could use saved HTML, known valid policy documents and a local HTTP server or simulated HTTP responses. Expected URLs, document identities and file contents would be recorded in a fixture manifest before execution, so that results could be checked against known values without relying on the live site.

| **ID** | **Assumption being challenged**                                                          | **Input artifact or environment**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | **Failure and how it would be detected**                                                                                                                                                                                                                                                                                                                             |
|--------|------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| A401   | Document links can be used directly without resolving them against the page URL.         | Serve an index at /policy/index.html containing href="files/alpha.pdf", href="/documents/beta.pdf" and an absolute same-site document URL. All three targets return known valid PDFs.                                                                                                                                                                                                                                                                                                                                      | Failure occurs if the scraper requests incorrect paths, misses supported links or crashes. Compare the request log and discovered URLs with the expected absolute URLs, including /policy/files/alpha.pdf and /documents/beta.pdf.                                                                                                                                   |
| A402   | A document URL always ends with a lowercase file extension.                              | Provide /policy.PDF, /policy.pdf?download=1 and /policy.docx?version=2, each returning a valid document of the corresponding type.                                                                                                                                                                                                                                                                                                                                                                                         | For a scraper expected to support these URL forms, failure is silently excluding eligible documents through a case-sensitive check of the complete URL. Compare discovery results with the manifest. For a deliberately restricted scraper, record this as a filtering limitation rather than assuming support is required.                                          |
| A403   | Every different link is a different document, and filenames uniquely identify documents. | Include /documents/a.pdf, /documents/a.pdf#page=1 and /documents/a.pdf#page=2, all referring to one resource. Also include /department-a/policy.pdf and /department-b/policy.pdf, containing different PDFs. The manifest identifies three distinct documents.                                                                                                                                                                                                                                                             | Failure occurs if fragment variants inflate the distinct-document count, or the two different policy.pdf resources are combined. Compare reported identities, counts and retrieved contents with the manifest. Request logs reveal unnecessary repeated downloads.                                                                                                   |
| A404   | Following redirects will eventually reach a document.                                    | Configure /first.pdf to redirect to /second.pdf, which redirects back to /first.pdf. Include a separate valid PDF. Before execution, configure a maximum of three redirect hops for each document and an overall request budget.                                                                                                                                                                                                                                                                                           | Failure occurs if the scraper exceeds either configured bound, hangs or reports success for the cycle. Count requests, including redirect requests, and inspect the recorded outcome. Verify that the separate valid document is handled according to the documented continuation policy.                                                                            |
| A405   | Checking the original link's host is enough to keep downloads within the permitted site. | Configure an explicit permitted-host policy. An allowed-host URL, /redirect.pdf, redirects to a second controlled host that is excluded by that policy. Use simulated responses or test servers only.                                                                                                                                                                                                                                                                                                                      | Failure occurs if the scraper requests the excluded destination despite its configured policy. Inspect both servers' logs, or the simulated client's call history. Verify that the redirect is rejected and the reason is recorded.                                                                                                                                  |
| A406   | A response is small enough to download fully into memory.                                | Configure a test download limit of 1 MiB. Serve a response without a Content-Length header that streams more than that amount. Include a small valid PDF as a control.                                                                                                                                                                                                                                                                                                                                                     | Failure occurs if the scraper reads the complete oversized stream, accumulates more body data than its configured limit or accepts the oversized document. Instrument the stream to record bytes read and retained, allowing for a documented read-chunk boundary. Inspect the outcome and confirm that the small control remains processable.                       |
| A407   | A server-supplied filename is safe to use as a local path.                               | For a scraper that saves files, return a valid PDF with Content-Disposition: attachment; filename="../../outside-policy.pdf". Inside an outer temporary sandbox, create the designated download directory at a407/work/downloads/. After path resolution, the malicious filename targets a407/outside-policy.pdf, which is outside the download directory but remains inside the temporary sandbox. Place a sentinel file with known contents at exactly a407/outside-policy.pdf and record its contents before execution. | Failure occurs if the scraper writes outside the designated download directory or modifies the sentinel at the resolved target path. Inspect the resolved output path and compare the sentinel contents before and after execution. Rejecting the filename or replacing it with a safe filename is acceptable. This test is conditional on the scraper saving files. |
| A408   | Document titles and URLs contain only ASCII characters.                                  | Serve correctly declared UTF-8 HTML containing titles such as Éthique Policy and 学生政策, with corresponding percent-encoded document URLs. Both targets return known valid PDFs.                                                                                                                                                                                                                                                                                                                                         | Failure occurs if URL handling requests the wrong resource or decoding crashes the scraper. Compare requested URLs and retrieved contents with the manifest. If titles are captured or displayed, compare them with the exact expected Unicode strings to detect corruption.                                                                                         |

These ideas assess robustness beyond the minimal prototype. The redirect and size limits above are illustrative test settings, not additional numerical requirements from the brief. Where a capability is deliberately unsupported, its limitation should be documented so that outcomes can be interpreted consistently. Task 4 proposes the tests; it does not claim that these checks have been implemented or executed.

## Repository Verification

On 17 October 2026, the following checks passed against the combined repository:

```text
uv run ruff check .  -> All checks passed
uv run mypy .        -> Success: no issues found
uv run pytest        -> 2 tests passed
```
