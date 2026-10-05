"""Input sanitization, boundary defense, and prompt injection defense utilities."""

import re
from typing import Tuple


def sanitize_code_input(code: str, max_chars: int = 10000, max_lines: int = 500) -> Tuple[str, bool]:
    """
    Validates and normalizes source code input.
    Rejects null bytes, validates length, and returns normalized string.
    """
    if "\x00" in code:
        raise ValueError("Null bytes are not allowed in source code.")

    # Normalize line endings to \n
    normalized = code.replace("\r\n", "\n").replace("\r", "\n")

    lines = normalized.split("\n")
    if len(lines) > max_lines:
        raise ValueError(f"Code exceeds {max_lines} lines limit (found {len(lines)} lines).")

    if len(normalized) > max_chars:
        raise ValueError(f"Code exceeds {max_chars} characters limit (found {len(normalized)} chars).")

    return normalized, True


def build_safe_prompt_envelope(code: str, language: str) -> str:
    """
    Wraps user code into a hardened XML-style boundary envelope for AI models.
    Defends against prompt injection by escaping internal closing delimiter tags.
    """
    # Neutralize any attempted delimiter closing injections
    escaped_code = code.replace("</untrusted_source_code>", "&lt;/untrusted_source_code&gt;")
    escaped_code = escaped_code.replace("<untrusted_source_code>", "&lt;untrusted_source_code&gt;")

    envelope = (
        f"<target_language>{language}</target_language>\n"
        f"<untrusted_source_code>\n"
        f"{escaped_code}\n"
        f"</untrusted_source_code>"
    )
    return envelope
