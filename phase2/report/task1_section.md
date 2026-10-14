## 1. Task 1 – Prototype

**Code:** `phase2/prototype/scrape_prototype.py` (run instructions in the repository `README.md`).

### 1.1 What the prototype does

The prototype is a single Python script that uses only the standard library
(`urllib`, `html.parser`).

1. It sends one GET for the index page `https://uwa-policy.cits5501.arranstewart.io/policy/`.
   A `--start-url` option lets us point it at a local server for testing.
2. It parses every `<a href>`, resolves each one against the index URL and drops
   the fragment. It keeps a link only if it is http(s), on the same host as the
   index page, and has a document extension (`.pdf .doc .docx .rtf .odt .xls .xlsx .ppt .pptx`).
   Duplicates are removed by exact URL. On the live index this gives
   **216 candidate links** (65 `.pdf`, 96 `.doc`, 48 `.docx`, 4 `.rtf`, 3 `.pptx`).
3. It picks 5 links (3–5 via `--max-docs`), cycling through the extensions so
   that up to five different file types are tried, and downloads them.
4. For each download it prints (a) the URL, (b) the HTTP status, (c) the declared
   `Content-Type`, (d) the size in bytes and (e) the first 16 bytes. It then gives
   an outcome: `OK` when the status is 200 *and* the leading bytes match the
   extension (`%PDF-` for PDF, `PK\x03\x04` for docx/pptx, the 8-byte OLE2 header
   `D0 CF 11 E0 A1 B1 1A E1` for legacy `.doc`, `{\rtf` for RTF). It reports `SUSPECT` when
   the status is 200 but the bytes do not match, and `FAILED` otherwise.
5. Requests are limited by a hard budget of 20. The budget counts every HTTP request:
   the index, each document, each redirect hop and each retry. The index and document
   requests are spaced 3.5 s apart; redirect hops follow straight away. On a `429` the script waits for a numeric `Retry-After`
   (capped at 15 s) and retries once, then gives up. The exit status is 0 only when
   at least 3 documents were downloaded and all of them look valid.

Live run on 13 Oct 2026 (abridged: entries 2–5 are condensed to one line each; 6 of 20 requests used):

```text
Found 216 candidate document links (.doc x96, .docx x48, .pdf x65, .pptx x3, .rtf x4)

[1] .../policy-framework/policy-governance-framework.pdf
  HTTP status   : 200
  Content-Type  : application/pdf
  Size (bytes)  : 301201
  Initial bytes : b'%PDF-1.6\r%\xe2\xe3\xcf\xd3\r\n'
  Outcome       : OK (pdf signature)
[2] .../delegations/delegations-framework-policy.doc   200  application/msword    256512  OK (ole2)
[3] .../risk/risk-policy.docx                          200  ...wordprocessingml... 154182 OK (zip)
[4] .../fraud-and-corruption-training.pptx             200  ...presentationml...  4298871 OK (zip)
[5] ...-domestic-postgraduate-students-policy.rtf      200  application/rtf       207353  OK (rtf)

5/5 documents downloaded and look valid; 6/20 requests used.
```

### 1.2 Assumptions

- Every policy document is linked directly from the index page, so no recursive crawling is needed.
- A policy document is any same-host link whose path ends in one of the extensions listed above. Three
  document links that point to `https://www.uwa.edu.au/...` (the real UWA site) are treated as other
  websites and skipped.
- URLs are case-sensitive. We checked this: requesting a document path with different letter case
  returned `404`, so the prototype does not merge links that differ only in case.
- Downloads are small enough to hold in memory (the largest we saw was about 4.3 MB).

### 1.3 Limitations

1. **The validity check is shallow.** It looks only at the first few bytes. A file that begins with
   `%PDF-` but is truncated or corrupt is still reported as `OK`. It also
   cannot tell `.docx` from `.xlsx` or any other ZIP file, and it does not compare the declared
   `Content-Type` with the extension.
2. **Link discovery depends on extensions and the current page layout.** Documents served from
   URLs without an extension (for example `/download?id=42`) are missed. Pages that build their links
   with JavaScript would also yield nothing. If fewer than 3 links are found the prototype prints a
   warning and exits with status 1, but it cannot tell a changed page layout from an index that
   really has no documents.
3. **Error handling is minimal.** There is one timeout per request and one retry on `429` only.
   It has no retry with backoff for `5xx` errors or timeouts, and an HTTP-date `Retry-After` is not
   parsed. It does not detect an index page whose HTML was truncated. A connection dropped
   part-way through a download is reported as `FAILED`, but the partial file is not resumed.
4. **No persistence.** Nothing is saved or checksummed, so a rerun downloads everything again.
