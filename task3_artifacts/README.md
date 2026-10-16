# Task 3 – Controlled HTTP Test Double

This artifact demonstrates a failure scenario where a URL ending in `.pdf`
returns HTML instead of a valid PDF document.

It provides a controlled and repeatable environment without depending on the
live policy website.

## Run the Server

From the repository root:

```bash
python3 task3_artifacts/wrong_content_server.py
```

By default, the server runs on:

```text
http://127.0.0.1:8000
```

The test endpoint is:

```text
http://127.0.0.1:8000/fake-policy.pdf
```

## Check the Response

In another terminal, run:

```bash
curl -i http://127.0.0.1:8000/fake-policy.pdf
```

## Expected Result

The response should contain:

```text
HTTP 200
Content-Type: text/html; charset=utf-8
```

The response body contains HTML instead of PDF data and does not begin with
the normal PDF `%PDF` signature.

This demonstrates why a scraper should not trust the `.pdf` file extension
alone when validating downloaded documents.

Other paths return HTTP `404`.

## Using a Different Port

If port `8000` is already being used, start the server with another port:

```bash
python3 task3_artifacts/wrong_content_server.py --port 8010
```

Then check it with:

```bash
curl -i http://127.0.0.1:8010/fake-policy.pdf
```

## Automated Test

Run the automated test with:

```bash
uv run pytest tests/test_task3_wrong_content_server.py -v
```

The test verifies that the controlled `.pdf` endpoint:

- returns HTTP `200`
- returns `text/html`
- contains HTML
- does not begin with `%PDF`

## Why a Local Test Double Is Used

The live policy website normally serves real policy documents. We cannot make
the live server return HTML from a `.pdf` URL exactly when required for a test.

Even if that failure happened naturally, it would be unpredictable and
difficult to reproduce.

The local test double allows the same failure to be reproduced safely and
consistently without creating unnecessary requests to the live website.

## Future Scraper Integration

Once the scraper prototype is integrated, this server can be used as a
controlled input for a scraper test. The scraper can request
`/fake-policy.pdf` and the test can verify that the response is detected as
invalid PDF content rather than being accepted as a valid policy document.