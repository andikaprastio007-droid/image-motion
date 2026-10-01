import re
STOP = {"the","a","of","and","as","in","to","with","from","original","image","scene","shown","source","main","subject"}

def check(a):
    r = []
    r.append(("warn", "Text detected") if a.get("has_text") else ("ok", "No text detected" if "has_text" in a else "Text: unchecked (no AI vision)"))
    r.append(("warn", "Logo detected") if a.get("has_logo") else ("ok", "No logo detected" if "has_logo" in a else "Logo: unchecked (no AI vision)"))
    r.append(("warn", "Face detected: keep motion minimal") if a.get("has_face") else ("ok", "No face flagged" if "has_face" in a else "Face: unchecked (no AI vision)"))
    r.append(("warn", "Possible AI artifact: " + ", ".join(a.get("risk_elements", [])[:2])) if a.get("risk_elements") else ("ok", "Clean composition"))
    return [{"level": l, "msg": m} for l, m in r]

def metadata(a, variation=None):
    words = []
    for k in ("subject", "environment", "lighting", "composition", "background"):
        words += re.findall(r"[a-zA-Z]{4,}", str(a.get(k, "")).lower())
    base = ["cinematic", "footage", "motion", "video", "stock", "background", "loop", "4k", "commercial", "slow motion"]
    if variation:
        words += re.findall(r"[a-zA-Z]{4,}", variation["name"].lower())
    seen, kws = set(), []
    for w in words + base:
        if w not in STOP and w not in seen:
            seen.add(w); kws.append(w)
    subj = str(a.get("subject", "scene"))
    title = f"{subj[:60].strip().capitalize()} cinematic motion footage"
    desc = (f"Cinematic motion footage. {a.get('environment','')}. {a.get('lighting','')}. "
            f"Subtle, realistic camera movement suitable for commercial and editorial use. No logos or watermarks.")
    return {"title": title[:100], "description": desc[:400], "keywords": kws[:50]}
