# xff_header_chain_parser

Parses an `X-Forwarded-For` header into an ordered list of client IP strings, left to right.

```python
from xff_header_chain_parser import parse_xff_chain

chain = parse_xff_chain("203.0.113.1, 198.51.100.7")
# chain == ["203.0.113.1", "198.51.100.7"]
```

## Why this exists

When a request passes through proxies, each proxy appends the IP it saw to the
`X-Forwarded-For` header. The leftmost entry is the original client; the rest
are proxies. The hard part is never the comma split — it is deciding which
entries to trust. That decision belongs in the application, which knows which
of its proxies strip untrusted input. This library deliberately does only the
mechanical parse and returns the chain as a plain list of strings so the caller
can apply its own trust policy without fighting the parser.

## What it does and does not do

- Returns each entry as a **string**, untouched. Entries are not validated as
  IPv4 or IPv6 literals.
- Port suffixes (`1.2.3.4:443`, `[::1]:443`) are preserved, not stripped.
- Surrounding whitespace around each entry is stripped.
- Empty entries from stray commas are dropped.
- A single empty or whitespace-only header yields `[]`.
- `None` and non-string inputs raise `InvalidHeaderError` (a subclass of
  `ValueError`).

## The awkward edge

Real XFF chains in the wild frequently contain hostname-like values,
port-suffixed addresses, or entries injected by untrusted upstreams. This
parser returns them verbatim. If you need strict IP validation, apply it to
the returned list — the parser will not throw away or rewrite entries it
cannot classify.

## Running the tests

```
PYTHONPATH=src python -m unittest discover -s tests
```

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

