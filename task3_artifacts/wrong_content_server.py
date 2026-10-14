"""Local HTTP test double for Phase 2 Task 3.

The server provides a URL ending in .pdf but deliberately returns HTML.
This creates a repeatable failure scenario for testing the scraper.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = "127.0.0.1"
PORT = 8000
FAKE_PDF_PATH = "/fake-policy.pdf"

HTML_BODY = b"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Not a PDF</title>
</head>
<body>
    <h1>Policy document unavailable</h1>
    <p>This response is HTML, not a PDF document.</p>
</body>
</html>
"""


class WrongContentHandler(BaseHTTPRequestHandler):
    """HTTP handler that returns HTML for a fake PDF URL."""

    def do_GET(self) -> None:
        """Handle GET requests."""
        if self.path != FAKE_PDF_PATH:
            self.send_error(404, "Not Found")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(HTML_BODY)))
        self.end_headers()
        self.wfile.write(HTML_BODY)

    def log_message(self, format: str, *args: object) -> None:
        """Disable normal request logging."""
        return


def main() -> None:
    """Start the local test-double server."""
    server = HTTPServer((HOST, PORT), WrongContentHandler)

    print(
        f"Task 3 test double running at "
        f"http://{HOST}:{PORT}{FAKE_PDF_PATH}"
    )
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
