"""Tests for the Task 3 controlled HTTP test double."""

from http.client import HTTPConnection
from http.server import HTTPServer
from threading import Thread

from task3_artifacts.wrong_content_server import (
    FAKE_PDF_PATH,
    WrongContentHandler,
)


def test_pdf_url_returns_html_instead_of_pdf() -> None:
    """Verify that the test double returns HTML from a .pdf URL."""
    server = HTTPServer(("127.0.0.1", 0), WrongContentHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    connection = HTTPConnection(
        "127.0.0.1",
        server.server_port,
        timeout=2,
    )

    try:
        connection.request("GET", FAKE_PDF_PATH)
        response = connection.getresponse()
        body = response.read()

        assert response.status == 200
        assert response.getheader("Content-Type") == "text/html; charset=utf-8"
        assert b"<html" in body.lower()
        assert not body.startswith(b"%PDF")

    finally:
        connection.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
