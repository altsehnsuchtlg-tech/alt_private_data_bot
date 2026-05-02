from __future__ import annotations

try:
    import native_ext
except ImportError:  # pragma: no cover - fallback path in case extension build fails
    native_ext = None


def score_text(text: str) -> int:
    if native_ext is not None:
        return int(native_ext.score_text(text))

    # Python fallback keeps the bot functional even before native build is ready.
    score = 0
    for idx, ch in enumerate(text):
        score += (idx + 1) * ord(ch)
    return score % 100000
