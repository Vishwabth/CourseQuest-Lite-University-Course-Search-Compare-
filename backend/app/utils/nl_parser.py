import re
from typing import Dict, Any, Optional

DELV_MAP = {
    "online": "online",
    "offline": "offline",
    "on campus": "offline",
    "on-campus": "offline",
    "hybrid": "hybrid",
    "blended": "hybrid",
}

LEVEL_MAP = {
    "ug": "UG",
    "undergrad": "UG",
    "undergraduate": "UG",
    "bachelor": "UG",
    "pg": "PG",
    "postgrad": "PG",
    "postgraduate": "PG",
    "masters": "PG",
    "master": "PG",
}

DEPARTMENT_MAP = {
    "cs": "CS",
    "computer": "CS",
    "computing": "CS",
    "ai": "CS",
    "math": "Math",
    "mathematics": "Math",
    "statistics": "Math",
    "economics": "Economics",
    "business": "Business",
    "management": "Business",
    "finance": "Business",
    "accounting": "Business",
    "psychology": "Psychology",
    "cognitive": "Psychology",
    "biology": "Biology",
    "chemistry": "Chemistry",
    "physics": "Physics",
    "philosophy": "Philosophy",
    "humanities": "Humanities",
    "sociology": "Sociology",
    "anthropology": "Anthropology",
    "political": "Political Science",
}


def parse_money(text: str) -> Optional[int]:
    text = text.replace(",", " ").lower()
    # Match "under 50k", "less than 1.5 lakh"
    m1 = re.search(r"(?:under|below|less than|<=?)\s*(\d+(?:\.\d+)?)\s*(lakh|lac|k|thousand)?", text)
    if m1:
        num = float(m1.group(1))
        unit = m1.group(2) or ""
        if unit in ["lakh", "lac"]:
            return int(num * 100000)
        if unit in ["k", "thousand"]:
            return int(num * 1000)
        return int(num)

    # Match plain number if “fee/tuition/cost/price” mentioned
    if re.search(r"(fee|tuition|cost|price)", text):
        m2 = re.search(r"(\d+(?:\.\d+)?)", text)
        if m2:
            return int(float(m2.group(1)))
    return None


def parse_question(q: str) -> Dict[str, Any]:
    ql = q.lower()
    out: Dict[str, Any] = {}

    # ----- Fee -----
    fee = parse_money(ql)
    if fee:
        out["max_fee"] = fee

    # ----- Rating -----
    # Case 1: "under/below/less than rating X"
    m_under = re.search(r"(?:rating|rated)\s*(?:<=?|under|below|less than)\s*(\d(?:\.\d)?)", ql)
    if m_under:
        try:
            out["max_rating"] = float(m_under.group(1))
        except ValueError:
            pass

    # Case 2: "rating 4+" or "rating above 4"
    m_above = re.search(r"(?:rating|rated)?\s*(?:>=|at least|above)?\s*(\d(?:\.\d)?)\s*\+?", ql)
    if m_above:
        try:
            out["min_rating"] = float(m_above.group(1))
        except ValueError:
            pass

    # ----- Level -----
    for k, v in LEVEL_MAP.items():
        if re.search(rf"\b{k}\b", ql):
            out["level"] = v
            break

    # ----- Delivery mode -----
    for k, v in DELV_MAP.items():
        if re.search(rf"\b{k}\b", ql):
            out["delivery_mode"] = v
            break

    # ----- Department -----
    for k, v in DEPARTMENT_MAP.items():
        if re.search(rf"\b{k}\b", ql):
            out["department"] = v
            break

    # ----- Credits -----
    m = re.search(r"(?:at least|min|>=)\s*(\d+)\s*credits?", ql)
    if m:
        out["min_credits"] = int(m.group(1))
    m2 = re.search(r"(?:under|less than|<=)\s*(\d+)\s*credits?", ql)
    if m2:
        out["max_credits"] = int(m2.group(1))

    # ----- Duration (weeks) -----
    m = re.search(r"(?:under|less than|<=)\s*(\d+)\s*weeks?", ql)
    if m:
        out["max_duration_weeks"] = int(m.group(1))
    m2 = re.search(r"(?:at least|min|>=)\s*(\d+)\s*weeks?", ql)
    if m2:
        out["min_duration_weeks"] = int(m2.group(1))

    # ----- Year offered -----
    m = re.search(r"(?:year|offered)\s*(\d{4})", ql)
    if m:
        out["year"] = int(m.group(1))

    # ----- General keyword -----
    if not out.get("department"):
        m = re.search(r"(?:about|on|for)\s+([a-zA-Z ]{3,})$", ql)
        if m:
            out["q"] = m.group(1).strip()

    return out
