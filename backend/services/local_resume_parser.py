import json
import re
from pathlib import Path


def _extract_name(lines, text):
    for line in lines[:5]:
        line = line.strip()
        if re.match(r"^[A-Z][A-Za-z.'-]+\s+[A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+)?$", line):
            return line
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            import subprocess, sys
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=False, timeout=180)
            nlp = spacy.load("en_core_web_sm")
        first_lines = "\n".join(lines[:5])
        doc = nlp(first_lines)
        for ent in doc.ents:
            if ent.label_ == "PERSON" and 1 <= len(ent.text.split()) <= 4:
                return ent.text.strip()
    except Exception:
        pass
    return lines[0].strip() if lines else "Unknown Candidate"


def _extract_email(text):
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else ""


def _extract_phone(text):
    match = re.search(r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}", text)
    return match.group(0) if match else ""


def _extract_location(text):
    lines = text.splitlines()
    for line in lines[:8]:
        line = line.strip()
        if re.search(r"(?:,?\s*(?:[A-Z][a-z]+\s+)+(?:India|USA|UK|Canada|Australia|Germany|France|Singapore|UAE|Dubai|London|New\s*York|San\s*Francisco|Bangalore|Mumbai|Delhi|Hyderabad|Chennai|Pune|Kolkata|Austin|Seattle|Chicago|Boston|Toronto|Berlin|Paris|Sydney|Melbourne|London|Dublin|Amsterdam|Zurich|Stockholm|Helsinki|Oslo|Copenhagen|Singapore|Tokyo|Shanghai|Beijing|Seoul))", line):
            return line.strip()
        if re.search(r"[A-Za-z\s]+,\s*[A-Z]{2}", line):
            return line.strip()
    return ""


def _extract_url(text, pattern):
    match = re.search(pattern, text, re.I)
    return match.group(0) if match else ""


def _extract_section(text, heading):
    pattern = rf"(?is)(?:{heading})\s*[:\-]?\s*(.*?)(?:\n\s*(?:education|experience|projects|certifications|skills|summary|technical\s*skills|work\s*history|employment|training|internship|achievements|languages|interests|publications)\s*[:\-]?|$)"
    match = re.search(pattern, text)
    if not match:
        return []
    content = match.group(1) or ""
    items = [part.strip() for part in re.split(r"\n\s*(?=\d+[\.\)]|\•|\-|\*)", content) if part.strip()]
    return items or [content.strip()]


def _extract_skills(text):
    skills_file = Path(__file__).parent.parent / "data" / "skills_master.json"
    master_skills = []
    if skills_file.exists():
        try:
            raw = json.loads(skills_file.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                for cat_list in raw.values():
                    master_skills.extend(cat_list)
            else:
                master_skills = raw
        except Exception:
            master_skills = []
    if not master_skills:
        master_skills = [
            "Python", "Java", "C++", "C", "JavaScript", "TypeScript", "Go", "Rust", "PHP", "Ruby", "Swift", "Kotlin",
            "R", "MATLAB", "Scala", "Perl", "Shell", "Bash", "SQL", "NoSQL", "HTML", "CSS", "React", "Angular",
            "Vue.js", "Node.js", "Express.js", "Django", "Flask", "FastAPI", "Spring Boot", "Laravel", "ASP.NET",
            "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Terraform", "Jenkins", "Git", "GitHub", "GitLab",
            "MongoDB", "PostgreSQL", "MySQL", "Redis", "Elasticsearch", "Cassandra", "PyTorch", "TensorFlow",
            "Keras", "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn", "NLP", "Computer Vision",
            "Machine Learning", "Deep Learning", "Data Science", "Data Analysis", "Statistics", "Tableau",
            "Power BI", "Linux", "REST API", "GraphQL", "gRPC", "WebSockets", "OAuth", "JWT", "CI/CD",
            "Agile", "Scrum", "Jira", "Confluence", "Figma", "Photoshop", "UI/UX", "Android", "iOS",
            "React Native", "Flutter", "Dart", "Hadoop", "Spark", "Kafka", "Airflow", "Snowflake",
            "BigQuery", "Redshift", "Selenium", "Cypress", "Jest", "PyTest", "Mocha", "Chai",
        ]
    lower_text = text.lower()
    found = []
    for skill in master_skills:
        s = skill.lower()
        pattern = r"(?<![a-z0-9+#])" + re.escape(s) + r"(?![a-z0-9+#])"
        if re.search(pattern, lower_text):
            found.append(skill)
    return sorted(set(found), key=lambda x: x.lower())


def _extract_experience(text):
    items = _extract_section(text, "experience|work experience|employment|work history")
    experience = []
    for item in items[:10]:
        years = 0.0
        for match in re.finditer(r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)", item, re.I):
            years = max(years, float(match.group(1)))
        year_nums = [int(y) for y in re.findall(r"\b(20\d{2}|19\d{2})\b", item)]
        if len(year_nums) >= 2:
            years = max(years, max(year_nums) - min(year_nums))
        title = ""
        title_match = re.search(r"(?i)(?:^|\n)\s*([A-Z][A-Za-z\s&]+)(?:\s*[–\-]\s*|at\s+|@\s+)", item)
        if title_match:
            title = title_match.group(1).strip()
        company = ""
        company_match = re.search(r"(?i)(?:at|@|–|-)\s+([A-Za-z0-9\s&.]+)(?:\s*[–\-]|\s*\n|$)", item)
        if company_match:
            company = company_match.group(1).strip()
        experience.append({
            "title": title or item.split(".")[0][:80],
            "company": company,
            "years": years,
            "description": item[:500],
        })
    return experience


def _extract_education(text):
    items = _extract_section(text, "education|academic|academics")
    education = []
    for item in items[:5]:
        degree = ""
        for d in [r"B\.?Tech", r"M\.?Tech", r"B\.?S\.?", r"M\.?S\.?", "PhD", r"Ph\.?D\.?", r"B\.?E\.?", r"M\.?B\.?A\.?",
                   "Bachelor", "Master", "Doctorate", r"B\.?Com", r"M\.?Com", r"B\.?Sc", r"M\.?Sc", "BBA", "MBA",
                   "High School", "Associate", "Diploma", r"B\.?Arch", r"M\.?Arch", r"LL\.?B", r"LL\.?M"]:
            if re.search(d, item, re.I):
                degree = d.replace("\\.?", ".") if "\\.?" in d else d
                break
        institution = ""
        inst_match = re.search(r"(?i)(?:at|from|–|-|,)\s+([A-Za-z0-9\s&.,]+(?:University|College|Institute|School|Academy))", item)
        if inst_match:
            institution = inst_match.group(1).strip()
        if not institution:
            for kw in ["University", "College", "Institute", "School", "Academy"]:
                idx = item.lower().find(kw.lower())
                if idx >= 0:
                    start = max(0, item.rfind(" ", 0, idx) + 1)
                    institution = item[start:idx + len(kw)].strip()
                    break
        year = ""
        year_match = re.search(r"\b(20\d{2})\b", item)
        if year_match:
            year = year_match.group(1)
        education.append({
            "degree": degree or item.split(",")[0].strip()[:80],
            "institution": institution,
            "year": year,
            "description": item[:300],
        })
    return education


def _extract_projects(text):
    items = _extract_section(text, "projects|project work|personal projects|academic projects")
    projects = []
    for item in items[:6]:
        title = ""
        title_match = re.match(r"\s*(?:Project\s*\d*\s*[:\-]\s*)?([A-Z][A-Za-z0-9\s\-_]+)", item)
        if title_match:
            title = title_match.group(1).strip()
        projects.append({
            "title": title or item.split(".")[0][:80],
            "description": item[:500],
            "technologies": [],
        })
    return projects


def _extract_certifications(text):
    items = _extract_section(text, "certifications|certification|certificates|certificate|licenses|licensure")
    certs = []
    for item in items[:8]:
        name = item.split(".")[0].strip() if "." in item else item.strip()
        issuer = ""
        issuer_match = re.search(r"(?i)(?:from|by|–|-)\s+([A-Za-z0-9\s&.]+)", item)
        if issuer_match:
            issuer = issuer_match.group(1).strip()[:80]
        year = ""
        year_match = re.search(r"\b(20\d{2})\b", item)
        if year_match:
            year = year_match.group(1)
        certs.append({
            "name": name[:150] if name else item.strip()[:150],
            "issuer": issuer,
            "year": year,
        })
    return certs


def _extract_languages(text):
    items = _extract_section(text, "languages")
    langs = []
    for item in items[:6]:
        lang = item.strip().rstrip(".")
        parts = re.split(r"[•\-–,:()]", lang)
        name = parts[0].strip()
        proficiency = parts[1].strip() if len(parts) > 1 else ""
        if name:
            langs.append({"language": name, "proficiency": proficiency})
    if not langs:
        known = ["English", "Hindi", "Spanish", "French", "German", "Mandarin", "Arabic", "Portuguese",
                 "Bengali", "Russian", "Japanese", "Korean", "Italian", "Dutch", "Tamil", "Telugu",
                 "Marathi", "Urdu", "Gujarati", "Kannada", "Malayalam", "Punjabi"]
        lower = text.lower()
        for lang in known:
            if lang.lower() in lower:
                langs.append({"language": lang, "proficiency": ""})
    return langs


def calculate_resume_strength(parsed):
    score = 0
    if parsed.get("name") and parsed["name"] not in ("Unknown Candidate", ""):
        score += 5
    if parsed.get("email"):
        score += 5
    if parsed.get("phone"):
        score += 5
    if parsed.get("location"):
        score += 5
    skills = parsed.get("skills", [])
    score += min(len(skills), 30)
    projects = parsed.get("projects", [])
    score += min(len(projects) * 5, 15)
    certs = parsed.get("certifications", [])
    score += min(len(certs) * 4, 12)
    education = parsed.get("education", [])
    score += min(len(education) * 4, 12)
    experience = parsed.get("experience", [])
    score += min(len(experience) * 4, 12)
    summary = parsed.get("summary", "")
    if summary:
        score += 4
    return min(score, 100)


def parse_resume(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    compact = re.sub(r"\s+", " ", text or " ").strip()
    email = _extract_email(compact)
    phone = _extract_phone(compact)
    location = _extract_location(text)
    name = _extract_name(lines, compact)
    skills = _extract_skills(text)
    experience = _extract_experience(text)
    education = _extract_education(text)
    projects = _extract_projects(text)
    certifications = _extract_certifications(text)
    languages = _extract_languages(text)
    linkedin = _extract_url(compact, r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9\-_/%]+")
    github = _extract_url(compact, r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9\-_/]+")
    portfolio = _extract_url(compact, r"(?:https?://)?(?:www\.)?[A-Za-z0-9\-_]+\.(?:com|io|dev|app|me|tech)/?[A-Za-z0-9\-_/]*")
    summary = ""
    summary_items = _extract_section(text, "summary|professional summary|profile|objective|about me")
    if summary_items:
        summary = summary_items[0][:500]
    action_words = {"developed", "designed", "implemented", "managed", "created", "built", "led", "achieved",
                    "improved", "delivered", "optimized", "architected", "engineered", "launched", "spearheaded",
                    "coordinated", "established", "generated", "increased", "reduced", "resolved", "mentored",
                    "authored", "deployed", "configured", "integrated", "migrated", "transformed", "accelerated"}
    action_word_count = sum(1 for w in action_words if re.search(r"\b" + re.escape(w) + r"\b", compact, re.I))

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "location": location,
        "linkedin": linkedin,
        "github": github,
        "portfolio": portfolio if portfolio and "linkedin" not in portfolio and "github" not in portfolio else "",
        "summary": summary,
        "skills": skills,
        "languages": languages,
        "experience": experience,
        "education": education,
        "projects": projects,
        "certifications": certifications,
        "action_word_count": action_word_count,
    }
