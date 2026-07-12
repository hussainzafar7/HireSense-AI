import json
import random
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUESTION_BANK_PATH = PROJECT_ROOT / "data" / "processed" / "question_bank.json"

SKILL_DOMAIN_HINTS = {
    "python": "programming_fundamentals", "java": "programming_fundamentals", "c++": "programming_fundamentals",
    "sql": "databases", "mongodb": "databases", "redis": "databases", "postgresql": "databases",
    "react": "web_development", "javascript": "web_development", "node.js": "web_development", "jwt": "web_development",
    "docker": "cloud_devops", "kubernetes": "cloud_devops", "aws": "cloud_devops", "gcp": "cloud_devops",
    "pytorch": "deep_learning", "tensorflow": "deep_learning", "bert": "deep_learning",
    "pandas": "data_science", "numpy": "data_science", "machine learning": "machine_learning",
    "encryption": "cybersecurity_fundamentals", "oauth": "cybersecurity_fundamentals", "sql injection": "cybersecurity_fundamentals",
    "android": "mobile_development", "flutter": "mobile_development", "figma": "graphic_design_cs",
}


def load_question_bank() -> list[dict]:
    if not QUESTION_BANK_PATH.exists():
        raise FileNotFoundError(f"Missing {QUESTION_BANK_PATH}. Run training/preprocess.py")
    return json.loads(QUESTION_BANK_PATH.read_text(encoding="utf-8"))


def estimate_years(resume: dict) -> float:
    vals = [float(x.get("years", 0) or 0) for x in resume.get("experience", [])]
    raw = resume.get("raw_text", "")
    for match in re.finditer(r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)", raw, flags=re.I):
        vals.append(float(match.group(1)))
    return max(vals) if vals else 0.0


def difficulty_weights(years: float) -> list[str]:
    if years <= 1:
        return ["beginner"] * 6 + ["intermediate"] * 3 + ["advanced"]
    if years <= 3:
        return ["beginner"] * 2 + ["intermediate"] * 5 + ["advanced"] * 3
    return ["intermediate"] * 3 + ["advanced"] * 7


def domain_for_skill(skill: str) -> str | None:
    s = skill.lower()
    for key, domain in SKILL_DOMAIN_HINTS.items():
        if key in s or s in key:
            return domain
    return None


def pick_questions(pool: list[dict], domains: list[str], difficulties: list[str], count: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    selected = []
    seen = set()
    for _ in range(count * 4):
        domain = rng.choice(domains) if domains else None
        diff = rng.choice(difficulties)
        candidates = [q for q in pool if (domain is None or q["domain"] == domain) and q["difficulty"] == diff and q["id"] not in seen]
        if not candidates:
            candidates = [q for q in pool if (domain is None or q["domain"] == domain) and q["id"] not in seen]
        if not candidates:
            candidates = [q for q in pool if q["id"] not in seen]
        if not candidates:
            break
        item = rng.choice(candidates)
        seen.add(item["id"])
        selected.append(item)
        if len(selected) >= count:
            break
    return selected


def generate_questions(resume: dict, job_role: str = "software engineer", n: int = 12) -> list[dict]:
    bank = load_question_bank()
    skills = resume.get("skills", [])
    inferred_domains = [domain_for_skill(s) for s in skills]
    inferred_domains = [d for d in inferred_domains if d]
    role = (job_role or "").lower()
    if "data" in role:
        inferred_domains += ["data_science", "machine_learning", "databases"]
    elif "frontend" in role or "web" in role:
        inferred_domains += ["web_development", "software_engineering"]
    elif "security" in role:
        inferred_domains += ["cybersecurity_fundamentals", "computer_networks"]
    elif "devops" in role or "cloud" in role:
        inferred_domains += ["cloud_devops", "operating_systems"]
    if not inferred_domains:
        inferred_domains = ["programming_fundamentals", "data_structures", "algorithms", "software_engineering"]
    domains = list(dict.fromkeys(inferred_domains))
    years = estimate_years(resume)
    selected = pick_questions(bank, domains, difficulty_weights(years), max(6, n - 2), seed=hash((resume.get("email", ""), tuple(skills[:8]), job_role)) & 0xFFFF)
    for project in resume.get("projects", [])[:3]:
        tech = ", ".join(project.get("technologies") or skills[:3])
        selected.append({
            "id": f"project_{len(selected)}",
            "question": f"In your project '{project.get('title', 'project')}', what architecture decision was most important and how did you evaluate trade-offs?",
            "domain": "software_engineering",
            "difficulty": "intermediate" if years < 3 else "advanced",
            "reference_answer": f"A strong project answer explains the goal, architecture, constraints, trade-offs, testing approach, and technologies such as {tech}.",
            "keywords": ["architecture", "trade-offs", "testing"] + ([tech] if tech else []),
        })
    selected.extend([
        {"id": "behavioral_debug", "question": "Describe a time you debugged a difficult technical issue. What evidence guided your solution?", "domain": "behavioral", "difficulty": "intermediate", "reference_answer": "A strong answer describes the problem, evidence collected, hypotheses tested, root cause, fix, and prevention steps.", "keywords": ["evidence", "root cause", "hypothesis", "prevention"]},
        {"id": "behavioral_learning", "question": "Tell me about a challenging project and how you learned what was needed to complete it.", "domain": "behavioral", "difficulty": "beginner", "reference_answer": "A strong answer explains the challenge, learning strategy, collaboration, implementation, and measurable result.", "keywords": ["challenge", "learning", "collaboration", "result"]},
    ])
    final = []
    seen_text = set()
    for q in selected:
        if q["question"] not in seen_text:
            final.append(q)
            seen_text.add(q["question"])
        if len(final) >= n:
            break
    return final
