"""Environment variable validation for arxiv stats action."""


def validate_env(env: dict) -> None:
    """Validate environment configuration.

    Args:
        env: Dict of environment variable names to values.

    Raises:
        ValueError: If any value is invalid.
    """
    out_dir = env.get("OUT_DIR", "./data")
    if ".." in out_dir:
        raise ValueError(f"OUT_DIR must not contain path traversal: {out_dir}")

    topics = env.get("TOPICS", "")
    if not topics:
        raise ValueError("TOPICS must not be empty")

    for key in ("START_RESULT", "RESULT_COUNT", "MAX_RESULTS_PER_QUERY"):
        val = env.get(key)
        if val is not None:
            try:
                n = int(val)
            except (ValueError, TypeError):
                raise ValueError(f"{key} must be a positive integer, got: {val}") from None
            if n < 0:
                raise ValueError(f"{key} must be a positive integer, got: {val}")

    citations = env.get("INCLUDE_CITATIONS")
    if citations is not None and citations not in ("true", "false"):
        raise ValueError(f"INCLUDE_CITATIONS must be 'true' or 'false', got: {citations}")
