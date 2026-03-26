import re

PREG_RE = re.compile(r"\b(pregnan(t|cy)|expecting|gestation(al)?|prenatal|antenatal|(?:first|second|third)\s+trimester|\d+\s*(?:weeks?|wks?|wk)\s+pregnan(t|cy))\b", re.I)
ACTION_RE = re.compile(r"\b(should i|restart|stop|stopped|start|adjust|increase|decrease|change|yesterday|today)\b", re.I)

# Postpartum
POSTPARTUM_RE = re.compile(r"\b(breast\s*feeding|breastfeeding|nursing|lactation|post[-\s]?partum|after\s+(delivery|birth))\b", re.I)