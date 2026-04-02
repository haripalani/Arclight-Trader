"""
MiroFish Normalizer
Extracts a directional trading signal from MiroFish's unstructured prediction report text.
"""
from dataclasses import dataclass

@dataclass
class MiroFishSignal:
    direction: str     # BULLISH | BEARISH | NEUTRAL
    confidence: float  # 0.0 – 1.0
    excerpt: str       # The key sentence that drove the decision
    bonus_score: int   # Trade Gate bonus points (0-20)

BULLISH_KEYWORDS = [
    "bullish", "upward", "rally", "rise", "increase", "positive",
    "买入", "上涨", "做多", "涨", "看多"
]
BEARISH_KEYWORDS = [
    "bearish", "downward", "decline", "drop", "fall", "negative",
    "卖出", "下跌", "做空", "跌", "看空"
]

def normalize_report(report_text: str) -> MiroFishSignal:
    """
    Parse a MiroFish prediction report and extract a directional signal.
    """
    if not report_text:
        return MiroFishSignal("NEUTRAL", 0.0, "No report received", 0)

    text_lower = report_text.lower()
    bullish_hits = sum(1 for kw in BULLISH_KEYWORDS if kw in text_lower)
    bearish_hits = sum(1 for kw in BEARISH_KEYWORDS if kw in text_lower)

    total = bullish_hits + bearish_hits
    if total == 0:
        return MiroFishSignal("NEUTRAL", 0.0, "No directional keywords found", 0)

    if bullish_hits > bearish_hits:
        confidence = bullish_hits / total
        bonus = int(confidence * 20)
        excerpt = _extract_sentence(report_text, BULLISH_KEYWORDS)
        return MiroFishSignal("BULLISH", round(confidence, 2), excerpt, bonus)
    elif bearish_hits > bullish_hits:
        confidence = bearish_hits / total
        bonus = int(confidence * 20)
        excerpt = _extract_sentence(report_text, BEARISH_KEYWORDS)
        return MiroFishSignal("BEARISH", round(confidence, 2), excerpt, bonus)
    else:
        return MiroFishSignal("NEUTRAL", 0.5, "Conflicting signals", 0)

def _extract_sentence(text: str, keywords: list[str]) -> str:
    """Return the first sentence containing a keyword."""
    for sentence in text.split("."):
        for kw in keywords:
            if kw in sentence.lower():
                return sentence.strip()[:200]
    return text[:200]
