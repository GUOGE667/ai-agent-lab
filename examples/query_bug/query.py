from urllib.parse import quote


def build_query(params: dict[str, str]) -> str:
    """Encode query keys and values in insertion order."""
    return "&".join(f"{key}={quote(value)}" for key, value in params.items())
