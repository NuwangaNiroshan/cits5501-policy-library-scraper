# CITS5501 Project 2026 – Phase 2 Report

**Group:** 15  
**Repository:** [NuwangaNiroshan/cits5501-policy-library-scraper](https://github.com/NuwangaNiroshan/cits5501-policy-library-scraper)

## Group Members

| Full name | Student number | GitHub ID |
|---|---:|---|
| Roshan Shanker | 24819852 | `Roshss2508` |
| Nuwanga Niroshan Hewa Wiladdarage | 24684008 | `NuwangaNiroshan` |
| Cam Zhou | 24349432 | `camzhou831-star` |
| Sharmel Rayen Remington Villava Rayen | 25079168 | `SharmelRayen` |
| Swathy Shenoy | 25068786 | `Swathymahesh` |

## Overview

This report presents the Phase 2 prototype, proposed test suite, fixtures and test doubles, and adversarial test ideas for the UWA policy-library scraper. The accompanying repository contains the prototype source code, instructions for running it, the Task 3 test-double artifact, and automated verification.

---

## 1. Task 1 – Prototype

**Code:** `phase2/prototype/scrape_prototype.py` (run instructions are provided in the repository `README.md`).

### 1.1 What the Prototype Does

The prototype is a single Python script that uses only the standard library (`urllib` and `html.parser`).

1. It sends one GET request to the index page at `https://uwa-policy.cits5501.arranstewart.io/policy/`. A `--start-url` option allows it to use a local server for testing.
2. It parses every `<a href>`, resolves each link against the index URL, and removes the fragment. It retains only HTTP(S) links on the same host whose paths end in a supported document extension: `.pdf`, `.doc`, `.docx`, `.rtf`, `.odt`, `.xls`, `.xlsx`, `.ppt`, or `.pptx`. Exact duplicate URLs are removed. On the live index, this produced **216 candidate links**: 65 PDF, 96 DOC, 48 DOCX, 4 RTF, and 3 PPTX files.
3. It selects between three and five links, according to `--max-docs`, while cycling through extensions so that it attempts up to five different file types.
4. For every download, it prints the URL, HTTP status, declared `Content-Type`, size in bytes, and first 16 bytes. It reports `OK` when the status is 200 and the leading bytes match the extension: `%PDF-` for PDF; `PK\x03\x04` for DOCX/PPTX; the OLE2 header `D0 CF 11 E0 A1 B1 1A E1` for legacy DOC; and `{\rtf` for RTF. It reports `SUSPECT` when the status is 200 but the signature does not match, and `FAILED` otherwise.
5. A hard request budget of at most 20 is enforced; `--max-requests` accepts only values from 1 to 20. The budget counts the index request, document requests, redirect hops, and retries. Index and document requests are spaced 3.5 seconds apart so that the live site does not receive rapid requests. On an HTTP 429 response, the script waits for a numeric `Retry-After` value, capped at 15 seconds, and retries once. It exits successfully only when at least three documents were downloaded and all appear valid.

An abridged live run on 17 October 2026 produced the following results. Six of the available 20 requests were used.

```text
Found 216 candidate document links (.doc x96, .docx x48, .pdf x65, .pptx x3, .rtf x4)

[1] .../policy-framework/policy-governance-framework.pdf
  HTTP status   : 200
  Content-Type  : application/pdf
  Size (bytes)  : 301201
  Initial bytes : b'%PDF-1.6\r%\xe2\xe3\xcf\xd3\r\n'
  Outcome       : OK (pdf signature)
[2] .../delegations/delegations-framework-policy.doc   200  application/msword      256512  OK (ole2)
[3] .../risk/risk-policy.docx                          200  ...wordprocessingml...  154182  OK (zip)
[4] .../fraud-and-corruption-training.pptx             200  ...presentationml...   4298871  OK (zip)
[5] ...-domestic-postgraduate-students-policy.rtf      200  application/rtf         207353  OK (rtf)

5/5 documents downloaded and look valid; 6/20 requests used.
```

### 1.2 Assumptions

- Every policy document is linked directly from the index page, so recursive crawling is unnecessary.
- A policy document is a same-host link whose path ends in one of the supported extensions. Three document links leading to `https://www.uwa.edu.au/...` are treated as external and skipped.
- URLs are case-sensitive. Requesting a document path with different letter casing returned HTTP 404, so the prototype does not merge links that differ only by case.
- Downloads are small enough to hold in memory; the largest observed file was approximately 4.3 MB.

### 1.3 Limitations

1. **The validity check is shallow.** It checks only the first few bytes. A truncated or corrupted file beginning with `%PDF-` is still reported as `OK`. It cannot distinguish a DOCX file from an XLSX or another ZIP file, and it does not compare the declared `Content-Type` with the extension.
2. **Link discovery depends on extensions and the current page construction.** URLs without an extension, such as `/download?id=42`, are missed, as are links created only by JavaScript. If fewer than three links are found, the prototype reports a warning and exits with status 1, but it cannot distinguish a changed page layout from a genuine empty index.
3. **Error handling is minimal.** Each request has one timeout, and only HTTP 429 responses are retried. There is no retry with backoff for 5xx responses or timeouts, and an HTTP-date `Retry-After` value is not parsed. Truncated index HTML is not detected. A connection interrupted during a download is reported as failed, but the partial file is not resumed.
4. **There is no persistence.** Files are not saved or checksummed, so every run downloads them again.

---

## 2. Task 2 – Design of Test Suite

### 2.1 Testing Objective

The test suite is designed to evaluate the reliability and error-handling behaviour of a fully functional policy-document scraper under unexpected website conditions. It addresses five scenarios: changes in website structure, truncated HTML, connection timeouts, HTTP client and server errors, and invalid or corrupted documents. Each proposed test follows the Arrange–Act–Assert (AAA) pattern to define reproducible conditions and measurable outcomes.

### 2.2 Expected Scraper Behaviour

A reliable scraper should handle unexpected conditions without crashing. It should not accept invalid documents or report misleading results. Where recovery is possible, it should continue processing; otherwise, it should report the failure clearly.

| Scenario | Expected scraper behaviour |
|---|---|
| **1. Website structure changes** | When an HTML change affects discovery, the scraper should either identify policy links through a supported fallback method or clearly report an extraction failure. It must not report successful extraction when it found no documents. |
| **2. Truncated HTML** | The scraper should process incomplete HTML predictably. It may recover complete links from available content, but malformed or incomplete URLs must not be accepted. Detectable truncation should be reported. |
| **3. Short- or long-term timeouts** | Temporary timeouts may trigger limited retries. If the server remains unresponsive, the scraper should stop after the configured attempt limit and report failure without waiting indefinitely. |
| **4. HTTP 4xx and 5xx errors** | Unsuccessful responses must not be treated as successful downloads. Permanent errors such as 404 should normally be reported without retrying, while temporary server errors such as 503 may justify limited retries. |
| **5. Invalid or corrupted documents** | Downloaded content should be validated rather than trusting the status code, filename, or declared content type. HTML returned instead of a PDF and corrupted documents should be rejected or clearly flagged. |

For reproducibility, these tests assume a two-second request timeout and no more than three total attempts for retryable failures, including the first request. HTTP 404 responses are not retried. A failure affecting one document should be reported without preventing other valid documents from being processed. These are proposed production-testing expectations and are not necessarily implemented in the Phase 2 prototype.

### 2.3 Test Case Design

| ID | Scenario and purpose | Arrange | Act | Assert |
|---|---|---|---|---|
| **T001** | **Structure change:** verify the response when the original extraction method no longer finds links. | Use the T001 fixture below, containing three valid PDF URLs in `data-document-url` attributes on `<button>` elements instead of `<a href>` elements. | Run the scraper against the modified page. | The scraper either extracts all three expected URLs using a supported fallback or clearly reports extraction failure. Silent success with zero documents fails the test. |
| **T002** | **Truncated HTML:** verify that malformed links are not extracted. | Serve the exact T002 fixture below at `http://127.0.0.1:3000/policy/`. It contains one complete PDF link and one unfinished anchor attribute. | Run the scraper and inspect extracted URLs and diagnostics. | Only `http://127.0.0.1:3000/documents/valid-policy.pdf` is extracted. The unfinished URL is neither extracted nor downloaded, and detectable incomplete HTML is reported without a crash. |
| **T003** | **Temporary timeout:** verify recovery through bounded retries. | Make the server exceed the two-second timeout on the first attempt and return a valid PDF with HTTP 200 on the second. Allow three total attempts. | Request the PDF through the scraper. | The first attempt times out, the second succeeds, and the scraper reports success after exactly two attempts. |
| **T004** | **Prolonged timeout:** verify the retry bound. | Delay every response beyond the two-second timeout. Allow three total attempts. | Run the scraper against the endpoint. | The scraper stops after three attempts, reports a timeout, and neither waits indefinitely nor reports success. |
| **T005** | **HTTP 404:** verify permanent client-error handling and continuation. | Return HTTP 404 for one document and a valid PDF with HTTP 200 for another. Do not retry 404 responses. | Run the scraper against an index containing both links. | The scraper records and reports the 404 after one request, while downloading the control document successfully. |
| **T006** | **HTTP 503:** verify bounded retries and continuation. | Return HTTP 503 without `Retry-After` for one endpoint and a valid PDF for another. Allow three attempts for the failing endpoint. | Run the scraper against an index containing both links. | The failing endpoint is requested three times and reported as unsuccessful; the control document is processed successfully. |
| **T007** | **PDF URL returns HTML:** verify content validation. | Make a `.pdf` endpoint return HTTP 200, `Content-Type: text/html`, and an HTML error page. | Attempt to download the supposed PDF. | The scraper detects the unexpected content, rejects the response, and reports an invalid document instead of a successful PDF. |
| **T008** | **Corrupted PDF:** verify validation beyond superficial indicators. | Return HTTP 200, `Content-Type: application/pdf`, and corrupted data beginning with `%PDF-` that a PDF parser cannot open. | Download and validate the response. | The scraper reports document-validation failure and does not classify it as a successful download. |

#### Controlled Fixture for T001

Use this modified policy index:

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

When served from `http://127.0.0.1:3000/policy/`, the expected URLs are:

1. `http://127.0.0.1:3000/documents/academic-policy.pdf`
2. `http://127.0.0.1:3000/documents/privacy-policy.pdf`
3. `http://127.0.0.1:3000/documents/student-conduct.pdf`

The test passes if all three are discovered through a supported fallback or extraction failure is explicitly reported. Silent success with zero documents fails the test.

#### Controlled Fixture for T002

Serve this exact truncated response:

```html
<html><body><a href="/documents/valid-policy.pdf">Valid policy</a><a href="/documents/broken
```

Under the proposed partial-recovery policy, the expected extracted URL set contains only:

```text
http://127.0.0.1:3000/documents/valid-policy.pdf
```

The incomplete `/documents/broken` link must not be extracted or downloaded. The scraper should report the detectable incomplete HTML while retaining the valid link.

### 2.4 Coverage and Rationale

The eight cases cover all five required failure scenarios. T001 and T002 test document discovery under structural and response-integrity problems. T003 and T004 distinguish temporary timeouts from prolonged unavailability. T005 and T006 test HTTP client and server failures while checking that valid downloads continue. T007 and T008 examine different validation failures: an incorrect response format and a structurally corrupted document.

Controlled fixtures and simulated responses make the conditions repeatable without depending on unpredictable live-site failures. These are proposed tests, not claims that all production-level behaviours have already been implemented.

---

## 3. Task 3 – Fixtures and Test Doubles

### 3.1 Fixtures and Test Oracle

Fixtures are fixed files, test data, or controlled environments that can be reused. They allow the scraper to be tested against known inputs rather than depending only on the live website. Useful fixtures include saved HTML pages, valid policy documents, corrupted documents, files with known content, and responses from a controlled local server.

The **fixture or test double** provides the controlled input or environment. The **test oracle** specifies the expected result used to determine whether the scraper behaved correctly. For example, the Task 3 server provides a URL ending in `.pdf` but deliberately returns HTML. Before running the test, the expected response is known:

- HTTP status 200;
- declared content type `text/html`;
- an HTML response body; and
- no `%PDF` signature at the beginning of the response.

The scraper should therefore reject the response as an invalid PDF. Because the input and expected result are predetermined, the test is repeatable and does not depend on changing live-site content.

### 3.2 Live-Site Request Observations

On 14 October 2026, five requests were sent to the policy index with a two-second delay between requests to check for obvious request limiting.

| Request | HTTP status | Response time (s) | Download size (bytes) |
|---:|---:|---:|---:|
| 1 | 200 | 0.970394 | 584187 |
| 2 | 200 | 1.077670 | 584187 |
| 3 | 200 | 0.869424 | 584187 |
| 4 | 200 | 0.959649 | 584187 |
| 5 | 200 | 1.151368 | 584187 |

All five responses had status 200 and the same size, with reasonably consistent response times. No clear request limiting was observed during this small test, but this does not prove that no limits exist at higher request volumes or rates. Automated testing should therefore use fixtures, mocks, and controlled servers instead of repeatedly contacting the live site. The command and complete observations are recorded in `task3_artifacts/observations/request_limit_check.txt`.

### 3.3 Use of Test Doubles

A test double replaces the live website or network connection during a test, allowing controlled failure conditions to be reproduced when required. Python facilities such as `unittest.mock`, pytest's `monkeypatch`, and local HTTP servers can simulate:

- a timeout by raising a timeout error;
- a connection failure by raising a connection error;
- a slow response by delaying the local server; and
- an interrupted download by closing the connection after sending only part of the body.

These behaviours are difficult to reproduce reliably on the live site because the group cannot control the real server. Test doubles make the Task 2 scenarios repeatable without requiring the live website to fail at a particular time.

### 3.4 Test-Double Artifact

The artifact at `task3_artifacts/wrong_content_server.py` provides a controlled `/fake-policy.pdf` endpoint. Although the URL ends in `.pdf`, it returns HTTP 200, `Content-Type: text/html; charset=utf-8`, an HTML body, and no `%PDF` signature. This is a controlled stub because it always gives a known response for the endpoint.

Run the artifact from the repository root:

```bash
python3 task3_artifacts/wrong_content_server.py
```

Inspect the response in another terminal:

```bash
curl -i http://127.0.0.1:8000/fake-policy.pdf
```

If port 8000 is occupied, select another port:

```bash
python3 task3_artifacts/wrong_content_server.py --port 8010
```

### 3.5 Automated Verification

The automated test at `tests/test_task3_wrong_content_server.py` starts the server on an available local port and verifies that the status is 200, the content type and body are HTML, and the body does not begin with `%PDF`. The server is then shut down automatically.

Run the artifact test with:

```bash
uv run pytest tests/test_task3_wrong_content_server.py -v
```

Run all project checks with:

```bash
uv run pytest
uv run ruff check .
uv run mypy .
```

The current automated test validates the test double itself. Once integrated into a production scraper test, the double can verify that the scraper rejects the invalid PDF response by considering the HTTP status, declared content type, file signature, and expected document format.

### 3.6 Why the Live Website Is Unsuitable for This Test

The live policy site normally serves real policy documents. The group cannot make it return HTML from a `.pdf` URL precisely when a test requires that failure. Even if this occurred naturally, its timing would be unknown and the condition would not be reproducible. Attempting to create failures against the live server would also be inappropriate and could generate unnecessary traffic. The local test double provides a safe, predictable, and repeatable alternative.

---

## 4. Task 4 – Adversarial Inputs

A scraper may work correctly on ordinary pages while relying on assumptions about URLs, document identity, response sizes, and filenames. The following eight controlled tests are designed to challenge such assumptions in another team's scraper. Each test could use saved HTML, known valid policy documents, and a local HTTP server or simulated responses. Expected URLs, identities, and file contents would be recorded in a fixture manifest before execution so that results can be assessed against known values without relying on the live site.

| ID | Assumption being challenged | Input artifact or environment | Failure and detection method |
|---|---|---|---|
| **A401** | Document links can be used without resolving them against the page URL. | Serve an index at `/policy/index.html` containing `href="files/alpha.pdf"`, `href="/documents/beta.pdf"`, and an absolute same-site URL. All targets return known valid PDFs. | Failure occurs if incorrect paths are requested, supported links are missed, or the scraper crashes. Compare the request log and discovered URLs with the expected absolute URLs, including `/policy/files/alpha.pdf` and `/documents/beta.pdf`. |
| **A402** | A document URL always ends in a lowercase extension. | Provide `/policy.PDF`, `/policy.pdf?download=1`, and `/policy.docx?version=2`, each returning a valid corresponding document. | For a scraper expected to support these forms, silently excluding an eligible file through a case-sensitive check of the complete URL is a failure. Compare discovery with the manifest. If the scraper deliberately restricts these forms, record the outcome as a documented limitation instead. |
| **A403** | Every different link identifies a different document, and filenames are unique identifiers. | Include `/documents/a.pdf`, `/documents/a.pdf#page=1`, and `/documents/a.pdf#page=2`, which refer to one resource. Also include distinct files at `/department-a/policy.pdf` and `/department-b/policy.pdf`. The manifest records three distinct documents. | Failure occurs if fragment variants inflate the count or the two different `policy.pdf` resources are combined. Compare identities, counts, and content with the manifest. The request log also reveals unnecessary duplicate downloads. |
| **A404** | Redirects will eventually reach a document. | Make `/first.pdf` redirect to `/second.pdf`, which redirects back to `/first.pdf`. Include a valid control PDF. Configure at most three redirect hops per document and an overall request budget. | Failure occurs if a bound is exceeded, the scraper hangs, or it reports success for the cycle. Count requests, inspect the recorded outcome, and verify that the valid control follows the documented continuation policy. |
| **A405** | Checking only the original link's host is sufficient to keep downloads within the permitted site. | Under an explicit permitted-host policy, make an allowed-host `/redirect.pdf` redirect to a second controlled host excluded by that policy. Use only simulated responses or test servers. | Failure occurs if the excluded destination is requested. Inspect both server logs or the simulated client's call history and verify that the redirect is rejected with a recorded reason. |
| **A406** | A response is small enough to read entirely into memory. | Set a 1 MiB test download limit. Serve a body larger than that limit without a `Content-Length` header, plus a small valid PDF as a control. | Failure occurs if the scraper reads the complete oversized stream, retains more data than the configured limit, or accepts the oversized document. Instrument bytes read and retained, allowing for a documented chunk boundary, and verify that the control remains processable. |
| **A407** | A server-supplied filename is safe to use as a local path. | For a scraper that saves files, return a valid PDF with `Content-Disposition: attachment; filename="../../outside-policy.pdf"`. Inside a temporary sandbox, place the download directory at `a407/work/downloads/`. Path resolution targets `a407/outside-policy.pdf`, outside the download directory but still inside the sandbox. Put a sentinel with known content at that exact target and record it before execution. | Failure occurs if the scraper writes outside the download directory or modifies the sentinel at the resolved target. Inspect the resolved output path and compare the sentinel before and after. Rejecting the filename or replacing it with a safe name is acceptable. This test applies only when the scraper saves files. |
| **A408** | Document titles and URLs contain only ASCII characters. | Serve correctly declared UTF-8 HTML with titles such as `Éthique Policy` and `学生政策` and corresponding percent-encoded URLs. Both targets return known valid PDFs. | Failure occurs if URL handling requests the wrong resource or decoding crashes. Compare requested URLs and retrieved content with the manifest. If titles are captured or displayed, compare them with the exact Unicode strings to detect corruption. |

The redirect and size limits in these tests are illustrative settings, not additional numerical requirements from the brief. Where a capability is deliberately unsupported, the limitation should be documented so that outcomes can be interpreted consistently. Task 4 proposes adversarial tests; it does not claim that they were implemented or executed.

---

## Repository Verification

On 17 October 2026, the following checks passed against the combined repository:

```text
uv run ruff check .  -> All checks passed
uv run mypy .        -> Success: no issues found
uv run pytest        -> 2 tests passed
```
