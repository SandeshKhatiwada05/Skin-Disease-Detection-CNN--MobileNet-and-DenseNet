# Helper to generate authoritative info URLs for predicted classes.
# Use this server-side to ensure <a href="{{ predictions.urlN }}"> is always absolute and valid.

from urllib.parse import quote_plus

DERMNET = "https://dermnetnz.org"
DERMNET_SEARCH = f"{DERMNET}/search?query="

# Known classes in HAM10000-style label set mapped to DermNet topics.
DERMNET_MAP = {
    "actinic keratosis": f"{DERMNET}/topics/actinic-keratosis",
    "atopic dermatitis": f"{DERMNET}/topics/atopic-dermatitis",
    # Benign keratosis-like lesions (SK/LPLK) -> seborrhoeic keratoses overview
    "benign keratosis": f"{DERMNET}/topics/seborrhoeic-keratoses",
    "dermatofibroma": f"{DERMNET}/topics/dermatofibroma",
    "melanocytic nevus": f"{DERMNET}/topics/melanocytic-naevi-of-the-skin",
    "melanoma": f"{DERMNET}/topics/melanoma",
    "squamous cell carcinoma": f"{DERMNET}/topics/cutaneous-squamous-cell-carcinoma",
    # Grouped class -> point to tinea corporis (ringworm body)
    "tinea ringworm candidiasis": f"{DERMNET}/topics/tinea-corporis",
    # Broad category -> DermNet search
    "vascular lesion": None,
}

def official_info_url(name: str) -> str:
    """
    Returns an absolute URL to an authoritative information page for a disease name.
    Prefers DermNet NZ. Falls back to DermNet on-site search via Google if no exact mapping.
    """
    if not name:
        return "https://www.google.com/search?q=site:dermnetnz.org"
    key = name.strip().lower()
    mapped = DERMNET_MAP.get(key)
    if mapped:
        return mapped
    if mapped is None and key == "vascular lesion":
        return f"{DERMNET_SEARCH}{quote_plus('vascular lesion')}"
    # Fallback: DermNet site search on Google
    return f"https://www.google.com/search?q={quote_plus('site:dermnetnz.org ' + name)}"