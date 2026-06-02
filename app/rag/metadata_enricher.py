from __future__ import annotations

from app.schemas.rag import DocumentChunk


EXCEPTION_KEYWORDS = {
    "FAILED_SETTLEMENT": ["failed settlement", "fail", "settlement failed"],
    "SSI_MISMATCH": ["ssi mismatch", "settlement instruction", "ssi validation"],
    "HOLIDAY_ISSUE": ["holiday", "business day", "market calendar"],
    "BOOKING_BREAK": ["booking mismatch", "booking break", "trade booking"],
    "MANUAL_OVERRIDE": ["manual override", "override approval"],
    "AUDIT": ["audit trail", "audit policy", "evidence retention"],
}

MARKET_KEYWORDS = {
    "US": ["us", "dtc"],
    "GB": ["uk", "gb", "crest"],
    "EU": ["eu", "euroclear", "clearstream"],
    "JP": ["jp", "jasdec"],
    "IN": ["in", "nsdl", "cdsl"],
    "SG": ["sg"],
}


def infer_exception_type(text: str) -> str:
    lowered = text.lower()
    for exception_type, keywords in EXCEPTION_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return exception_type
    return "ALL"


def infer_market(text: str) -> str:
    lowered = text.lower()
    for market, keywords in MARKET_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return market
    return "ALL"


def enrich_chunk_metadata(chunk: DocumentChunk) -> dict:
    text_for_inference = f"{chunk.section_heading}\n{chunk.text}".lower()
    metadata = dict(chunk.metadata)

    metadata["doc_name"] = chunk.doc_name
    metadata["doc_type"] = chunk.doc_type
    metadata["section_heading"] = chunk.section_heading
    metadata["source_path"] = chunk.source_path

    metadata["exception_type"] = metadata.get("exception_type") or infer_exception_type(text_for_inference)
    metadata["market"] = metadata.get("market") or infer_market(text_for_inference)
    metadata["version"] = metadata.get("version", "v1.0")
    metadata["effective_date"] = metadata.get("effective_date", "2026-01-01")

    return metadata