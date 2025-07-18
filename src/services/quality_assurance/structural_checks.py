import unicodedata
import logging
import re
from better_profanity import profanity

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_junk(text):
    """Check for junk text like placeholder or irrelevant content."""
    if not text or not isinstance(text, str):
        return True
    return bool(re.search(r"asdf|lorem|click here|\{\{\w+\}\}", text.lower(), re.IGNORECASE))

def has_repeated_chars(text, threshold=4):
    """Detect excessive repeated characters."""
    if not text or not isinstance(text, str):
        return False
    return bool(re.search(rf"(.)\1{{{threshold},}}", text))

def check_unicode_script(text, expected_script_prefix):
    """Verify text matches expected Unicode script."""
    if not text or not isinstance(text, str):
        return False
    try:
        return all(unicodedata.name(char, "").startswith(expected_script_prefix) for char in text if char.strip())
    except Exception as e:
        logger.warning(f"Unicode script check failed: {e}")
        return False

def check_profanity(text):
    """Check for profanity using better_profanity library."""
    if not text or not isinstance(text, str):
        return False
    try:
        return profanity.contains_profanity(text)
    except Exception as e:
        logger.warning(f"Profanity check failed: {e}")
        return False
    

# --- MAIN WRAPPER ---
def main(text, expected_script_prefix="LATIN", repeat_threshold=4):
    """Run all structural QA checks on a single text."""
    return {
        "junk": check_junk(text),
        "repeated_chars": has_repeated_chars(text, threshold=repeat_threshold),
        "script_ok": check_unicode_script(text, expected_script_prefix),
        "profanity": check_profanity(text)
    }

# --- CLI ENTRY ---
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run structural QA checks on a given text.")
    parser.add_argument("--text", type=str, required=True, help="Input text to evaluate")
    parser.add_argument("--expected_script", type=str, default="LATIN", help="Expected Unicode script prefix (e.g., 'LATIN', 'ARABIC')")
    parser.add_argument("--repeat_threshold", type=int, default=4, help="Repetition threshold for character checks")

    args = parser.parse_args()

    results = main(args.text, expected_script_prefix=args.expected_script, repeat_threshold=args.repeat_threshold)
    
    for key, value in results.items():
        print(f"{key}: {value}")
