import math
import torch
import numpy as np
from loguru import logger
from transformers import XLMWithLMHeadModel, XLMRobertaTokenizerFast, AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer
import unicodedata

# Setup logging
# logging.basicConfig(level=logging.INFO)


# -------- Load Models --------
try:
    embedder = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
except Exception as e:
    logger.error(f"Failed to load SentenceTransformer: {e}")
    raise


try:
    model_name = "facebook/mbart-large-50-many-to-many-mmt"
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    model.eval()
except Exception as e:
    logger.error(f"Failed to load XGLM model: {e}")
    raise


# -------- Perplexity --------

def is_amharic(text: str) -> bool:
    """Returns True if text is detected as Amharic or mostly uses Ethiopic script."""

    for char in text:
        if char.strip():
            if "ETHIOPIC" in unicodedata.name(char, ""):
                return True

    return False


def calculate_perplexity(text: str, max_length: int = 64) -> float:
    """
    Calculate perplexity of a sentence using XGLM decoder-only multilingual language model.

    Args:
        text (str): Input text in any supported language (e.g., English, Swahili).
        max_length (int): Max length for truncation to avoid very long sentences.

    Returns:
        float: Perplexity score (lower is better). Returns inf if invalid or failed.
    """
    if not text or not isinstance(text, str) or not text.strip():
        return float("inf")
    try:
        inputs = tokenizer(text.strip(), return_tensors="pt",
                           truncation=True, max_length=max_length)
        input_ids = inputs["input_ids"]
        with torch.no_grad():
            outputs = model(input_ids=input_ids, labels=input_ids)
            loss = outputs.loss
        return round(math.exp(loss.item()), 2)
    except Exception as e:
        logger.warning(f"mBART perplexity failed: {e}")
        return float("inf")

# -------- Embedding Entropy --------


def embedding_entropy(text: str) -> float:
    """
    Calculate the entropy of a sentence embedding vector to estimate semantic richness.

    """
    try:
        vec = embedder.encode([text], convert_to_tensor=False)[0]
        vec = np.abs(np.array(vec))
        prob_vec = vec / np.sum(vec)

        entropy = -np.sum(prob_vec * np.log(prob_vec + 1e-10))
        return float(round(entropy, 3))
    except Exception as e:
        logger.warning(f"Embedding entropy failed: {e}")
        return 0.0


# -------- Main Coherence Check --------
def check_coherence(
    text: str,
    perplexity_threshold: float = 80.0,
    entropy_threshold: float = 2.0,
    junk_flags: dict = None
) -> dict:
    """
    Check coherence of multilingual text input.

    Args:
        text (str): Input text in any language.
        perplexity_threshold (float): Max acceptable perplexity.
        entropy_threshold (float): Minimum acceptable embedding entropy.
        junk_flags (dict): Optional output of external junk detection.

    Returns:
        dict: {
            'perplexity': float,
            'entropy': float,
            'coherence_ok': bool
        }
    """
    results = {}

    # Fluency
    ppl = calculate_perplexity(text)
    results["perplexity"] = ppl

    # Semantic richness
    entropy = embedding_entropy(text)
    results["entropy"] = entropy

    logger.info(f"Perplexity: {ppl}, Entropy: {entropy}")

    # Coherence check
    results["coherence_ok"] = True if is_amharic(text) else (
        ppl < perplexity_threshold and entropy > entropy_threshold)

    return results
