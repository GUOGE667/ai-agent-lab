def extension(filename: str) -> str:
    """Return the lowercase final suffix without the dot, or an empty string."""
    if "." not in filename:
        return ""
    return filename.split(".")[1].lower()
