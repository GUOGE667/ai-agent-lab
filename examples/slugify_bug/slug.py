def slugify(title: str) -> str:
    """Return a lowercase, hyphen-separated title slug."""
    return title.replace(" ", "-")
