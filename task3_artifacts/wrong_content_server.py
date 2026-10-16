"""Controlled HTTP server for the Phase 2 Task 3 test double."""

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = "127.0.0.1"
DEFAULT_PORT = 8000
FAKE_PDF_PATH = "/fake-policy.pdf"

HTML_RESPONSE = b"""<!DOCTYPE html>
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
    """Return HTML from a URL that appears to be a PDF."""

    def do_GET(self) -> None:
        """Handle GET requests."""
        if self.path != FAKE_PDF_PATH:
            self.send_error(404, "Not Found")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(HTML_RESPONSE)))
        self.end_headers()
        self.wfile.write(HTML_RESPONSE)


def run_server(port: int) -> None:
    """Run the controlled HTTP test-double server."""
    server = HTTPServer((HOST, port), WrongContentHandler)

    print(f"Task 3 test-double server running at http://{HOST}:{port}")
    print(f"Test URL: http://{HOST}:{port}{FAKE_PDF_PATH}")
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run the Task 3 controlled HTTP test double."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port to listen on (default: {DEFAULT_PORT})",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    run_server(arguments.port)
