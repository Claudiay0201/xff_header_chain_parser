from __future__ import annotations


class InvalidHeaderError(ValueError):
    """Raised when the X-Forwarded-For header cannot be parsed.

    Inherits from ValueError so callers that already catch ValueError for
    general input validation do not miss this specific case.
    """


def parse_xff_chain(header: str) -> list[str]:
    """Parse an X-Forwarded-For header into an ordered list of client IP strings.

    The X-Forwarded-For header is a comma-separated list of IP addresses.
    RFC 7239 (which defines the Forwarded HTTP extension) and common proxy
    practice both append to the *left* side of the list: the first element is
    the original client, and each subsequent element is a proxy that handled
    the request. We preserve that left-to-right order verbatim so callers can
    apply their own trust policy.

    Design decisions (stated plainly so the behaviour is unambiguous):

    * Each entry is returned as a **string**, untouched. This library does
      not validate that entries are valid IPv4 or IPv6 literals. Doing so would
      force a choice about how to handle entries that fail validation (skip?
      raise?), and real-world XFF chains frequently contain hostname-like values
      or port-suffixed addresses depending on the proxy. Returning strings keeps
      the parser honest about what it actually inspected.
    * Port suffixes (``1.2.3.4:443`` or ``[::1]:443``) are **not** stripped, for
      the same reason: the caller decides what to trust.
    * A single empty header (``""``) returns ``[]``. This is the case where no
      proxy chain is present at all.
    * Surrounding whitespace on each entry is stripped, because the RFC's
      ``#element`` production permits optional whitespace around commas and it
      is the overwhelmingly common real-world shape.
    * Empty entries produced by stray commas (``"1.2.3.4,,5.6.7.8``) are
      dropped, because they carry no information and silently preserving them
      would force every caller to filter them out.
    * A header containing a bare comma or only whitespace after stripping
      (``","``) yields ``[]``, not an error.
    * ``None`` is explicitly rejected with :class:`InvalidHeaderError`. This
      is the one non-string input we guard against, because it is the value
      most commonly seen when a framework passes a missing header through
      unchanged.
    """
    if header is None:
        raise InvalidHeaderError("X-Forwarded-For header must be a string, got None")
    if not isinstance(header, str):
        raise InvalidHeaderError(
            "X-Forwarded-For header must be a string, got " + type(header).__name__
        )

    parts = header.split(",")
    result: list[str] = []
    for part in parts:
        candidate = part.strip()
        if candidate == "":
            continue
        result.append(candidate)
    return result
