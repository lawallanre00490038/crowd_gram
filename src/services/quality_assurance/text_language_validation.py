import os
import langid
from loguru import logger
import pycountry
import pandas as pd
from typing import Dict, Any
from functools import lru_cache
from transformers import pipeline

abs_path = os.path.dirname(os.path.abspath(__file__))

# Load AfroLID model globally
try:
    afrolid_model = pipeline("text-classification",
                             model="UBC-NLP/afrolid_1.5")
except Exception as e:
    logger.error(f"Failed to load AfroLID model: {e}")
    raise

# Load supported languages CSV file


def load_iso_mapping(filepath="./supported-languages.csv"):
    try:
        filepath = os.path.join(abs_path, "..", "..",
                                "data", "supported-languages.csv")
        df = pd.read_csv(filepath)
        mapping = {
            row["isocode"]: {"name": row["language"], "script": row["script"]}
            for _, row in df.iterrows()
        }
        return mapping
    except Exception as e:
        logger.error(f"Failed to load mapping file: {e}")
        return {}


# Mapping loaded once
mapping = load_iso_mapping()


@lru_cache(maxsize=256)
def get_language_name_from_iso(code: str) -> str:
    """Fallback to pycountry to get language name from ISO 639-1 or 639-3 code."""
    try:
        # Try alpha_2 (ISO 639-1)
        lang_obj = pycountry.languages.get(alpha_2=code)
        if lang_obj:
            return lang_obj.name
    except Exception:
        pass

    try:
        # Try alpha_3 (ISO 639-3)
        lang_obj = pycountry.languages.get(alpha_3=code)
        if lang_obj:
            return lang_obj.name
    except Exception:
        pass

    return code  # return code itself if no match


def langid_fallback(text: str) -> Dict[str, Any]:
    """
    Run langid classification with fallback to custom mapping + pycountry.
    Returns structured language metadata.
    """
    fallback_code, fallback_conf = langid.classify(text)

    # Check custom mapping (AfroLID CSV)
    if fallback_code in mapping:
        meta = mapping[fallback_code]
    else:
        # Fallback to pycountry
        lang_name = get_language_name_from_iso(fallback_code)
        logger.info("language name", get_language_name_from_iso("En"))
        meta = {
            "name": lang_name,
            "script": "unknown"
        }

    logger.info(
        f"[langid fallback] {fallback_code} ({meta['name']}) | Confidence: {round(fallback_conf, 3)}")

    return {
        "code": fallback_code,
        "language": meta["name"],
        "script": meta["script"],
        "confidence": round(fallback_conf, 3),
        "source": "langid"
    }


def detect_message_language(text: str, confidence_threshold: float = 0.75) -> Dict[str, Any]:
    """
    Detects the language of the input text using AfroLID 1.5, and falls back to langid if confidence is low.

    Returns a dict with keys: code, language, script, confidence, source
    """
    if not text or not isinstance(text, str) or not text.strip():
        return _unknown_response()

    text = text.strip()

    # Step 1: Try AfroLID
    try:
        result = afrolid_model(text)[0]
        code = result["label"]
        confidence = round(result["score"], 3)
        meta = mapping.get(code, {"name": code, "script": "unknown"})

        if confidence >= confidence_threshold:
            logger.info(
                f"[AfroLID] {code} ({meta['name']}) | Confidence: {confidence}")
            return {
                "code": code,
                "language": meta["name"],
                "script": meta["script"],
                "confidence": confidence,
                "source": "afrolid"
            }
        else:
            logger.warning(
                f"[AfroLID] Low confidence ({confidence}). Falling back to langid.")
    except Exception as e:
        logger.warning(
            f"[AfroLID] Detection failed: {e}. Falling back to langid.")

    # Step 2: Fallback to langid
    try:
        return langid_fallback(text)

    except Exception as e:
        logger.error(f"[Fallback] langid failed: {e}")
        return _unknown_response()


# -------------------- Unknown Response --------------------
def _unknown_response() -> Dict[str, Any]:
    return {
        "code": "unknown",
        "language": "unknown",
        "script": "unknown",
        "confidence": 0.0,
        "source": "none"
    }
