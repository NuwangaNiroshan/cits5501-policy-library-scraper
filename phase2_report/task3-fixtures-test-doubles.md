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

The artifact is located at:

`task3_artifacts/wrong_content_server.py`

It provides a controlled HTTP endpoint:

`/fake-policy.pdf`

Although the URL ends in `.pdf`, the server deliberately returns:

- HTTP `200`
- `Content-Type: text/html; charset=utf-8`
- HTML content instead of PDF content
- no `%PDF` file signature

This behaves like a controlled stub because it always returns a known response
for the selected endpoint.

Run the artifact with:

```bash
python3 task3_artifacts/wrong_content_server.py
```

Then check the response with:

```bash
curl -i http://127.0.0.1:8000/fake-policy.pdf
```

If port `8000` is already being used, another port can be selected:

```bash
python3 task3_artifacts/wrong_content_server.py --port 8010
```

### Automated Verification

The automated test is located at:

`tests/test_task3_wrong_content_server.py`

The test starts the controlled HTTP server on an available local port and
verifies that:

- the response status is HTTP `200`
- the content type is HTML
- the body contains HTML
- the body does not start with the `%PDF` signature

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

### Expected Scraper Behaviour

A scraper should not assume that a URL ending in `.pdf` contains a valid PDF.

The response should also be checked using information such as:

- HTTP status
- `Content-Type`
- file signature or first bytes
- expected document format

A normal PDF commonly starts with `%PDF`. The controlled response instead
contains HTML and does not contain this PDF signature.

The current automated test verifies the behaviour of the test double itself.
Once the Task 1 scraper is integrated, this test double can also be used as
controlled input to verify that the scraper detects and rejects the invalid
PDF response.

### Why the Live Website Is Not Suitable for This Test

The live policy website normally serves real policy documents.

We cannot make the real server return HTML from a `.pdf` URL exactly when a
test requires that failure. Even if this problem occurred naturally, we would
not know when it would happen and could not reproduce it consistently.

Trying to create failures against the live server would also be inappropriate
and could generate unnecessary traffic.

The local test double gives us a safe, predictable and repeatable way to test
the same failure scenario.