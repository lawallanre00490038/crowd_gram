def check_length_and_truncation(source, translation, min_ratio=0.5, max_ratio=2.0):
    """Verify translation length is reasonable and not truncated."""
    if not source or not translation or not isinstance(source, str) or not isinstance(translation, str):
        return False
    src_len = len(source.split())
    tgt_len = len(translation.split())
    ratio = tgt_len / max(1, src_len)
    truncated = any(translation.rstrip().endswith(end) for end in ("...", "…", "but", "because"))
    return min_ratio <= ratio <= max_ratio and not truncated

def main(source, translation, min_ratio=0.5, max_ratio=2.0):
    """Wrapper for programmatic use or external import."""
    return check_length_and_truncation(source, translation, min_ratio, max_ratio)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run length & truncation check.")
    parser.add_argument("--source", type=str, required=True, help="Original source text")
    parser.add_argument("--translation", type=str, required=True, help="Translated text")
    parser.add_argument("--min_ratio", type=float, default=0.5, help="Minimum length ratio")
    parser.add_argument("--max_ratio", type=float, default=2.0, help="Maximum length ratio")

    args = parser.parse_args()

    result = main(args.source, args.translation, args.min_ratio, args.max_ratio)
    print(" Length & truncation check passed?" , result)
