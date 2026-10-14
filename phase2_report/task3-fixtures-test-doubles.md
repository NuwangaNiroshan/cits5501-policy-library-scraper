## Task 3 – Fixtures and Test Doubles

### Fixtures and Testing Oracle

Fixtures are fixed files, test data, or controlled environments that can be reused during testing. They allow us to test the scraper using known inputs instead of depending only on the live website.

Useful fixtures for this project could include:

- Saved HTML pages
- Valid policy documents
- Invalid or corrupted policy documents
- Files with known content
- Responses from a controlled local server

The **fixture or test double** provides the controlled input or environment for the test. The **test oracle** provides the expected result that is used to decide whether the scraper behaved correctly.

For example, our local test double provides a URL ending in `.pdf`, but deliberately returns HTML. The expected result is known before the test is run:

- The HTTP status is `200`
- The declared content type is `text/html`
- The response contains HTML
- The response does not begin with the `%PDF` signature

A scraper should therefore not accept this response as a valid PDF document.

Because both the input and expected result are known, the same test can be repeated with the same expected outcome. This also avoids depending on live website content, which may change over time.

### Live-Site Request Observations

We carried out a small test to see whether the policy website showed any clear request limiting.

Five requests were sent to the policy index page, with a two-second delay between each request.

The results were:

| Request | HTTP status | Response time (s) | Download size (bytes) |
|---|---:|---:|---:|
| 1 | 200 | 0.970394 | 584187 |
| 2 | 200 | 1.077670 | 584187 |
| 3 | 200 | 0.869424 | 584187 |
| 4 | 200 | 0.959649 | 584187 |
| 5 | 200 | 1.151368 | 584187 |

All five requests returned HTTP status `200`.

The response size was the same for every request, and the response times were also similar. We did not observe any clear sign of request limiting during this small test.

However, this does not prove that the website has no request limits. The website may behave differently if more requests are sent or if requests are sent more quickly.

For automated testing, we should avoid sending many requests to the live website. Fixtures, mocks, and controlled local servers can be used instead. This reduces unnecessary requests to the real server and makes the tests more repeatable.

The request observations are recorded in:

`task3_artifacts/observations/request_limit_check.txt`

### Use of Test Doubles

A test double can replace the real website or network connection during testing. This allows us to create failure conditions in a controlled and repeatable way instead of waiting for the real website to fail.

In Python, tools such as `unittest.mock`, pytest's `monkeypatch`, and controlled local HTTP servers can be used to create test doubles.

Test doubles could simulate the following conditions:

- **Timeouts:** a mock can raise a timeout error.
- **Connection failures:** a mock can raise a connection error instead of contacting the real server.
- **Slow responses:** a controlled local server can delay its response.
- **Interrupted downloads:** a controlled server can start sending data and then close the connection before the download is complete.

These conditions are difficult to reproduce reliably using the live website because we do not control the real server.

Using test doubles also allows the Task 2 failure scenarios to be tested repeatedly without requiring the real website to fail at the correct time.

### Test-Double Artifact – Incorrect Content for a PDF Link

We created a controlled local HTTP test double in:

`task3_artifacts/wrong_content_server.py`

The server provides the following URL:

`http://127.0.0.1:8000/fake-policy.pdf`

The URL ends in `.pdf`, but the server deliberately returns:

- HTTP status `200`
- Content type `text/html; charset=utf-8`
- HTML content instead of a PDF document

This demonstrates a failure scenario where a link appears to point to a PDF policy document, but the server returns the wrong type of content.

The local server acts as a test double, similar to a stub, because it replaces the real website and returns a fixed response that we control. This allows the same failure condition to be reproduced every time the test is run.

The server can be started with:

```bash
python3 task3_artifacts/wrong_content_server.py