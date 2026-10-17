## 2. Task 2 – Design of Test Suite

### 2.1 Testing Objective

The objective of this test suite is to evaluate the reliability and error-handling behaviour of a fully functional policy-document web scraper under unexpected website conditions. The tests address five scenarios: changes in website structure, truncated HTML responses, connection timeouts, HTTP client and server errors, and invalid or corrupted documents. The proposed test cases assess whether the scraper handles these conditions predictably by recovering where appropriate or clearly reporting failures without producing misleading results. Each test case follows the Arrange–Act–Assert (AAA) approach to establish reproducible test conditions and measurable expected outcomes.

### 2.2 Expected Scraper Behaviour

A reliable policy-document scraper should handle unexpected website conditions without crashing. It should not accept invalid documents or report misleading results. Where recovery is possible, it should continue processing. Otherwise, it should report the failure clearly. The expected behaviour for each required scenario is outlined below.

| Scenario | Expected Scraper Behaviour |
|---|---|
| **1. Website structure changes** | When changes to the HTML structure affect document discovery, the scraper should either identify the policy links using a supported alternative extraction method or clearly report an extraction failure. It should not incorrectly report successful extraction when no documents have been discovered. |
| **2. Truncated HTML** | The scraper should process incomplete HTML predictably. It may recover complete document links from the available content, but malformed or incomplete URLs must not be accepted. Detectable truncation should be reported. |
| **3. Short- or long-term timeouts** | Temporary timeouts may trigger limited retries. If the server remains unresponsive, the scraper should stop after the configured attempt limit and clearly report the failure without waiting indefinitely. |
| **4. HTTP 4xx and 5xx errors** | The scraper should distinguish unsuccessful HTTP responses from successful downloads. Permanent errors such as 404 should normally be reported without retrying, while temporary server errors such as 503 may justify limited retries. |
| **5. Invalid or corrupted documents** | The scraper should validate downloaded content rather than relying solely on HTTP status codes, filenames or declared content types. HTML returned instead of a PDF and corrupted documents should be rejected or clearly flagged. |

For reproducibility, the proposed tests assume a two-second request timeout and a maximum of three total attempts for retryable failures, including the initial request. HTTP 404 responses are not retried. Individual document failures should be reported without preventing other valid documents from being processed. These are proposed production-testing expectations and are not necessarily implemented by the Phase 2 prototype.

### 2.3 Test Case Design

Eight test cases are proposed to evaluate the scraper under the five required failure scenarios. Each case specifies its purpose, required setup (Arrange), execution (Act), and observable expected outcome (Assert). The tests are designed for a production-level scraper rather than the minimal prototype.

| Test ID | Related Scenario | Test Purpose | Arrange | Act | Assert |
|---|---|---|---|---|---|
| **T001** | Scenario 1: Website structure changes | Verify that the scraper responds appropriately when changes to the HTML structure prevent its original extraction method from identifying policy links. | Prepare an HTML fixture containing three valid PDF URLs stored in `data-document-url` attributes of `<button>` elements instead of the original `<a href>` elements. Use the T001 fixture defined below. | Run the scraper against the modified index page. | The scraper either successfully extracts all three expected document URLs using a supported fallback method or clearly reports an extraction failure. Reporting successful extraction with zero documents is considered a failure. |
| **T002** | Scenario 2: Truncated HTML | Verify that the scraper handles incomplete HTML without incorrectly extracting malformed document links. | Configure a local server at `http://127.0.0.1:3000/policy/` to return HTTP 200 with the exact truncated HTML fixture defined below. The response contains one complete PDF link followed by an unfinished anchor attribute. | Run the scraper against the truncated index page and inspect the extracted URLs and diagnostics. | Under the proposed partial-recovery policy, the extracted URL set must contain only `http://127.0.0.1:3000/documents/valid-policy.pdf`. The unfinished URL must not be extracted or downloaded. The scraper must report the detectable incomplete HTML without crashing. |
| **T003** | Scenario 3: Temporary timeout | Verify that the scraper recovers from a temporary timeout using bounded retries. | Configure a test server to exceed the two-second request timeout on the first attempt and return HTTP 200 with a valid PDF on the second attempt. Allow a maximum of three total attempts. | Run the scraper and request the PDF document. | The first attempt times out, the second succeeds, and the scraper reports a successful download after exactly two attempts. |
| **T004** | Scenario 3: Prolonged timeout | Verify that the scraper stops retrying when the server remains unresponsive. | Configure a test server to delay every response beyond the two-second request timeout. Allow a maximum of three total attempts. | Run the scraper against the unresponsive endpoint. | The scraper stops after three unsuccessful attempts, reports a timeout failure, and does not wait indefinitely or report a successful download. |
| **T005** | Scenario 4: HTTP 4xx error | Verify that the scraper correctly handles a missing document without affecting other valid downloads. | Configure one document endpoint to return HTTP 404 (Not Found) and another to return HTTP 200 with a valid PDF. Apply a policy that does not retry permanent 404 errors. | Run the scraper against an index containing both document links. | The scraper records HTTP 404, reports the affected download as failed, and makes only one request to the missing document. The valid control document is downloaded successfully. |
| **T006** | Scenario 4: HTTP 5xx error | Verify that the scraper handles persistent server errors using bounded retries. | Configure one document endpoint to return HTTP 503 (Service Unavailable) for every request, with no `Retry-After` header. Include a second endpoint returning a valid PDF. Allow three total attempts for the failing endpoint. | Run the scraper against an index containing both document links. | The scraper makes three attempts to the failing endpoint, reports HTTP 503 as an unsuccessful download, and successfully processes the valid control document. |
| **T007** | Scenario 5: PDF link returns HTML | Verify that the scraper rejects HTML content returned from a URL advertised as a PDF. | Configure a `.pdf` endpoint to return HTTP 200 with `Content-Type: text/html` and an HTML error page instead of PDF data. | Run the scraper and attempt to download the supposed PDF. | The scraper detects the unexpected content type, rejects the HTML response, and reports an invalid document rather than a successful PDF download. |
| **T008** | Scenario 5: Corrupted PDF | Verify that the scraper detects a corrupted PDF even when its filename, declared content type and initial bytes appear correct. | Configure a server to return HTTP 200 with `Content-Type: application/pdf` and corrupted PDF data beginning with `%PDF-` that cannot be opened by a PDF parser. | Run the scraper and validate the downloaded content. | The scraper detects the invalid PDF structure, reports a document-validation failure, and does not incorrectly classify the corrupted document as a successful download. |

#### Controlled HTML Fixtures for T001 and T002

The following fixtures specify the input conditions for T001 and T002 so that another student or teaching staff member can reproduce the tests.

**T001 – Modified Website Structure**

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

When served from `http://127.0.0.1:3000/policy/`, the expected document URLs are:

1. `http://127.0.0.1:3000/documents/academic-policy.pdf`
2. `http://127.0.0.1:3000/documents/privacy-policy.pdf`
3. `http://127.0.0.1:3000/documents/student-conduct.pdf`

The test passes if the scraper discovers all three URLs through a supported fallback mechanism or explicitly reports that document extraction failed. It fails if the scraper silently reports successful extraction with zero documents.

**T002 – Truncated HTML Response**

Configure the local server to return the following exact HTML content:

```html
<html><body><a href="/documents/valid-policy.pdf">Valid policy</a><a href="/documents/broken
```

The HTML contains one complete anchor element followed by a second anchor with an unfinished `href` attribute.

The expected extracted URL set under the proposed partial-recovery policy is:

```text
http://127.0.0.1:3000/documents/valid-policy.pdf
```

The scraper must not extract or download the incomplete `/documents/broken` link. It should identify and report the detectable incomplete HTML while preserving the valid link.

### 2.4 Test Coverage and Rationale

The proposed test suite contains eight test cases covering all five failure scenarios specified in the project requirements. T001 examines structural changes affecting document discovery, while T002 evaluates incomplete HTML processing using a reproducible fixture and expected URL set. T003 and T004 distinguish temporary connection failures from prolonged unavailability. T005 and T006 test HTTP client and server errors, including the continuation of valid downloads after individual failures. T007 and T008 examine different document-validation problems: incorrect response content and corrupted PDF structures.

Controlled fixtures and simulated server responses are proposed to make these conditions repeatable without depending on unpredictable failures in the live website. The test suite evaluates appropriate recovery, bounded retry behaviour, document validation and accurate failure reporting. These are proposed tests, not claims that the production-level behaviours have already been implemented or executed.