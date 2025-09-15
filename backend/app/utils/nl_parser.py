import re
from typing import Dict, Any
from typing import Optional

DELV_MAP = {
    "online": "online",
    "offline": "offline",
    "on campus": "offline",
    "on-campus": "offline",
    "hybrid": "hybrid",
}

LEVEL_MAP = {
    "ug": "UG",
    "undergrad": "UG",
    "undergraduate": "UG",
    "pg": "PG",
    "postgrad": "PG",
    "postgraduate": "PG",
    "masters": "PG",
}

def parse_money(text: str) -> Optional[int]:
    # Support '50k', '50,000', '1 lakh', '1.5 lakh', '100000'
    text = text.replace(",", " ").lower()
    m1 = re.search(r"(?:under|below|less than|<=?)\s*(\d+(?:\.\d+)?)\s*(lakh|lac|k|thousand|rs|inr|₹)?", text)
    if m1:
        num = float(m1.group(1))
        unit = m1.group(2) or ""
        if unit in ["lakh", "lac"]:
            return int(num * 100000)
        if unit in ["k", "thousand"]:
            return int(num * 1000)
        return int(num)
    m2 = re.search(r"(\d+(?:\,\d{3})+|\d+)", text)
    if m2:
        val = int(m2.group(1).replace(",", ""))
        return val
    return None

def parse_question(q: str) -> Dict[str, Any]:
    ql = q.lower()

    out: Dict[str, Any] = {}

    # fee cap
    fee = None
    # explicit "under/below/less than X"
    m = re.search(r"(under|below|less than|<=?)\s*([\d,\.]+)\s*(k|lakh|lac|thousand|inr|rs|₹)?", ql)
    if m:
        raw = m.group(2).replace(",", "")
        unit = (m.group(3) or "").lower()
        val = float(raw)
        if unit in ["lakh", "lac"]:
            fee = int(val * 100000)
        elif unit in ["k", "thousand"]:
            fee = int(val * 1000)
        else:
            fee = int(val)
    else:
        # generic number: treat as max fee if words like fee/tuition present
        if re.search(r"(fee|tuition)", ql):
            fee = parse_money(ql)
    if fee:
        out["max_fee"] = fee

    # rating
    m = re.search(r"(?:rating|rated)\s*(?:>=|at least|above)?\s*(\d(?:\.\d)?)", ql)
    if m:
        try:
            out["min_rating"] = float(m.group(1))
        except:
            pass
    else:
        # phrases like "rating 4 and above"
        m2 = re.search(r"(\d(?:\.\d)?)\s*\+\s*rating", ql)
        if m2:
            out["min_rating"] = float(m2.group(1))

    # level
    for k,v in LEVEL_MAP.items():
        if re.search(rf"\b{k}\b", ql):
            out["level"] = v
            break

    # delivery mode
    for k,v in DELV_MAP.items():
        if re.search(rf"\b{k}\b", ql):
            out["delivery_mode"] = v
            break

    # department: take first capitalized word like CS/Math/Economics/Business/Psychology or keywords
    dep_words = ["cs","computer","math","mathematics","economics","business","psychology"]
    for w in dep_words:
        if re.search(rf"\b{w}\b", ql):
            if w in ["cs","computer"]:
                out["department"] = "CS"
            elif w in ["math","mathematics"]:
                out["department"] = "Math"
            elif w == "economics":
                out["department"] = "Economics"
            elif w == "business":
                out["department"] = "Business"
            elif w == "psychology":
                out["department"] = "Psychology"
            break

    # credits
    m = re.search(r"(?:credits?)\s*(?:>=|at least)?\s*(\d+)", ql)
    if m:
        out["min_credits"] = int(m.group(1))

    # duration in weeks
    m = re.search(r"(?:weeks?)\s*(?:<=|under|less than)?\s*(\d+)", ql)
    if m and ("under" in ql or "less than" in ql or "<=" in ql):
        out["max_duration_weeks"] = int(m.group(1))

    # year offered
    m = re.search(r"(?:year|offered)\s*(\d{4})", ql)
    if m:
        out["year"] = int(m.group(1))

    # search keyword
    m = re.search(r"(?:about|on|for)\s+([a-zA-Z ]{3,})$", ql)
    if m:
        out["q"] = m.group(1).strip()

    return out
