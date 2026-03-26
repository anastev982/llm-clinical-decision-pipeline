from typing import  List

STOP = {"the","a","an","is","are","to","of","and","in","on","for"}
NEG = {"not","no","never","without","contraindicated","avoid"}
POS = {"yes","can","allowed","recommended","safe","indicated"}
MISSING_HINTS = {
    "it depends",
    "not enough information",
    "insufficient information",
    "cannot determine",
    "need more information",
    "consult"
}
def _tokens(s: str) -> set[str]:
    words = [w.strip(".,!?;:()[]\"'").lower() for w in s.split()]
    return {w for w in words if len(w) > 2 and w not in STOP}

def detect_cross_answer_flags(answer: List[str]) -> List[str]:
    if len(answer) < 2:
        return []
    
    sets = [_tokens(a) for a in answer]
    flags = []
    
    # Instability, if the average similarity is low across all pair of answers.
    # All pairs of answers on one question using one model, with the same meaning.
    sims = []
    for i in range(len(sets)):            # Iterate though all pairs of answers. Jacquard similarity.
        for j in range(i+1, len(sets)):   # Compares answers i with the nex one in the list, to avoid duplicate comparisons. 
            a, b = sets[i], sets[j]
            sims.append(len(a & b) / max(1, len(a | b))) 
            # Avoid division with empty sets.
            if sims:
                avg_sim = sum(sims) / len(sims)   # Model stability for this question. High avg_sim - similar answer, low avg_sim - different answer.
                if avg_sim < 0.35:            # Proxy for semantic stability. Threshold to be tuned.
                    flags.append("answer_inconsistency")   #If the similarity is below the threshold, flag it as "answer_inconsistency".
                
    # Detection of contradiction: neg + pos signals in different answers
    has_neg = any(len(s & NEG) > 0 for s in sets)    # Intersection of each answer with the NEG set.
    has_pos = any(len(s & POS) > 0 for s in sets)    # Intersection with the POS set.
    if has_neg and has_pos:
        flags.append("answer_contradiction")          # Decision policy signals
    
    # Detection of missing context hints
    has_missing = any(len(s & MISSING_HINTS) > 0 for s in sets)
    if has_missing:
        flags.append("missing_context")
        
        
    return flags