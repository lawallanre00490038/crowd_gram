import logging
import fasttext
import argparse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model with error handling
try:
    fasttext_model = fasttext.load_model("lid.176.bin")
except Exception as e:
    logger.error(f"Failed to load FastText model: {e}")
    raise


# --- LANGUAGE VALIDATION ---
def detect_language_fasttext(text):
    """Detect language using FastText with confidence score, flagging low-confidence for rare languages."""
    if not text or not isinstance(text, str):
        return "unknown", 0.0
    try:
        prediction = fasttext_model.predict(text.replace("\n", " "), k=1)
        lang = prediction[0][0].replace("__label__", "")
        confidence = prediction[1][0]
        # Flag low-confidence detections for potential rare languages
        if confidence < 0.5:
            logger.warning(f"Low confidence ({confidence:.2f}) for language detection: '{text[:50]}...'. Consider manual review.")
        return lang, confidence
    except Exception as e:
        logger.warning(f"Language detection failed: {e}")
        return "unknown", 0.0
    


# --- MAIN WRAPPER ---
def main(text):
    """Expose detect_language_fasttext as a callable entry point."""
    lang, conf = detect_language_fasttext(text)
    return {"language": lang, "confidence": round(conf, 3)}

# --- CLI ENTRY ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run FastText language detection.")
    parser.add_argument("--text", type=str, required=True, help="Text to detect language for")
    args = parser.parse_args()

    result = main(args.text)
    print(f"Detected Language: {result['language']}")
    print(f"Confidence: {result['confidence']}")