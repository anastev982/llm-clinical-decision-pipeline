from typing import List, Dict, Optional

OVERCONFIDENCE_PHRASES = [ "sigurno", "nema sumnje", "uvek", "nikada", "definitivno",
    "100%", "bez ikakve sumnje"]

SOURCE_HINTS = ["http", "www", "doi", "pubmed", "nice", "who", "cdc", "guideline", "smernic"]

def detect_single_q_flags(
    answer: str, 
    query_text: str
    ) -> List[str]:
    
    # Check for overconfidence flags in the answer
    flags: List[str] = []
    a = answer.lower()
    q = query_text.lower()
    
    # Missing sources
    if not any(h in a for h in SOURCE_HINTS):
        flags.append("missing_sources")
        
    #Overconfidence
    if any(p in a for p in OVERCONFIDENCE_PHRASES):
        flags.append("overconfidence")
        
    # If the question needs some additional context to be answered, but the answer doesn't ask for it, flag it as "missing context".
    if ("doza" in q or "dijagnoza" in q) and "?" not in a:
        flags.append("missing_context")
        
    return flags