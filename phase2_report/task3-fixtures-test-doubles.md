## Task 3 – Fixtures and Test Doubles

### Fixtures and Testing Oracle

Fixtures are fixed files or test data that can be reused during testing. They help us test the scraper using known inputs instead of depending only on the live website.

Useful fixtures for this project could include:

- Saved HTML pages
- Valid policy documents
- Invalid or corrupted policy documents
- Files with known content
- Responses from a local test server

These fixtures can be used as a source of truth because we already know what each file contains and what result we expect.

For example, a valid PDF should be recognised as a PDF. If a URL ends in `.pdf` but the returned content is HTML, the scraper should not treat it as a valid PDF.

Using fixtures also makes tests repeatable. The same test data can be used every time, even if the live website changes.

### Live-Site Request Observations

We carried out a small test to see whether the policy website showed any clear request limiting.

Five requests were sent to the policy index page. There was a two-second delay between each request.

The results were:

| Request | HTTP status | Response time (s) | Download size (bytes) |
|---|---:|---:|---:|
| 1 | 200 | 0.970394 | 584187 |
| 2 | 200 | 1.077670 | 584187 |
| 3 | 200 | 0.869424 | 584187 |
| 4 | 200 | 0.959649 | 584187 |
| 5 | 200 | 1.151368 | 584187 |

All five requests returned HTTP status `200`.

The response size was the same for every request, and the response times were also similar. We did not see any clear sign of request limiting during this small test.

However, this does not prove that the website has no request limits. The website may behave differently if more requests are sent or if requests are sent more quickly.

For automated testing, we should avoid sending many requests to the live website. Fixtures, mocks and local test servers can be used instead. This makes the tests safer and more repeatable.

### Use of Test Doubles

A test double can replace the real website or network connection during testing.

This allows us to create failure conditions in a controlled way instead of waiting for the real website to fail.

In Python, tools such as `unittest.mock`, pytest's `monkeypatch`, and a local HTTP server can be used to create test doubles.

Test doubles could simulate:

- **Timeouts:** a mock can raise a timeout error.
- **Connection failures:** a mock can raise a connection error.
- **Slow responses:** a local server can delay its response.
- **Interrupted downloads:** a local server can start sending data and then close the connection before the download is complete.

These situations are difficult to reproduce reliably using the live website because we do not control the real server.

### Test-Double Artifact – Incorrect Content for a PDF Link

We created a local test-double server in:

`task3_artifacts/wrong_content_server.py`

The server provides this URL:

`http://127.0.0.1:8000/fake-policy.pdf`

The URL ends in `.pdf`, but the server deliberately returns:

- HTTP status `200`
- Content type `text/html; charset=utf-8`
- HTML content instead of a PDF document

This demonstrates a failure scenario where a link appears to point to a PDF document, but the server returns the wrong type of content.

The server can be started with:

```bash
python3 task3_artifacts/wrong_content_server.py