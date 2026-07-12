import argparse
import json
import random
import re
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW = PROJECT_ROOT / "data" / "raw"
PROCESSED = PROJECT_ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

CS_DOMAINS = {
    "programming_fundamentals": ["variables", "loops", "functions", "recursion", "OOP", "data types", "exception handling", "file I/O", "memory management"],
    "data_structures": ["arrays", "linked lists", "stacks", "queues", "trees", "graphs", "hash tables", "heaps", "tries", "segment trees"],
    "algorithms": ["sorting", "searching", "dynamic programming", "greedy algorithms", "divide and conquer", "graph algorithms", "BFS", "DFS", "Dijkstra", "complexity analysis", "Big O notation"],
    "databases": ["SQL", "normalization", "indexing", "transactions", "ACID", "NoSQL", "MongoDB", "Redis", "ER diagrams", "query optimization"],
    "operating_systems": ["processes", "threads", "scheduling", "memory management", "virtual memory", "file systems", "deadlock", "synchronization", "semaphores", "mutexes"],
    "computer_networks": ["OSI model", "TCP/IP", "HTTP/HTTPS", "DNS", "routing", "IP addressing", "subnetting", "firewalls", "sockets", "REST API"],
    "software_engineering": ["SDLC", "Agile", "Scrum", "design patterns", "SOLID principles", "testing", "CI/CD", "Git", "code review", "refactoring"],
    "web_development": ["HTML/CSS", "JavaScript", "React", "Node.js", "REST vs GraphQL", "authentication", "JWT", "cookies", "sessions", "WebSockets", "responsive design", "DOM manipulation"],
    "machine_learning": ["supervised learning", "unsupervised learning", "neural networks", "CNN", "RNN", "LSTM", "transformers", "overfitting", "regularization", "gradient descent", "backpropagation", "feature engineering", "model evaluation", "cross-validation", "bias-variance tradeoff"],
    "deep_learning": ["PyTorch", "TensorFlow", "Keras", "attention mechanism", "BERT", "GPT", "transfer learning", "embeddings", "loss functions", "optimizers", "batch normalization", "dropout"],
    "cloud_devops": ["AWS", "GCP", "Azure", "Docker", "Kubernetes", "microservices", "serverless", "load balancing", "auto-scaling", "monitoring", "infrastructure as code", "Terraform"],
    "cybersecurity_fundamentals": ["encryption", "hashing", "SSL/TLS", "OAuth", "firewalls", "VPN", "zero trust", "authentication", "authorization", "PKI", "digital signatures", "secure coding", "HTTPS", "certificates"],
    "graphic_design_cs": ["Photoshop basics", "color theory", "vector vs raster", "UI/UX principles", "Figma", "wireframing", "prototyping", "typography", "design systems"],
    "mobile_development": ["Android", "iOS", "React Native", "Flutter", "Dart", "app lifecycle", "push notifications", "SQLite mobile", "API calls"],
    "data_science": ["pandas", "numpy", "matplotlib", "seaborn", "statistical analysis", "hypothesis testing", "A/B testing", "data cleaning", "EDA", "feature selection", "dimensionality reduction", "PCA"],
}

DOMAIN_DESCRIPTIONS = {
    "programming_fundamentals": "core programming constructs that make software predictable, maintainable, and testable",
    "data_structures": "ways to organize data so operations such as lookup, insertion, deletion, and traversal are efficient",
    "algorithms": "step-by-step problem-solving methods analyzed by correctness and time or space complexity",
    "databases": "systems and techniques for storing, querying, indexing, and protecting structured or unstructured data",
    "operating_systems": "resource management concepts that coordinate CPU, memory, files, processes, and concurrent execution",
    "computer_networks": "protocols and infrastructure that move data reliably and securely between machines",
    "software_engineering": "practices for designing, building, testing, reviewing, and evolving production software",
    "web_development": "browser, server, API, and state-management concepts used to build interactive web applications",
    "machine_learning": "methods that learn patterns from data and generalize with measurable predictive performance",
    "deep_learning": "neural network techniques using layered differentiable models, embeddings, attention, and optimization",
    "cloud_devops": "automation and platform practices for deploying, scaling, monitoring, and operating services",
    "cybersecurity_fundamentals": "controls and defensive design practices for preserving confidentiality, integrity, availability, and trust",
    "graphic_design_cs": "visual design and UX methods for making digital interfaces clear, consistent, and usable",
    "mobile_development": "platform concepts for building reliable applications on Android, iOS, and cross-platform stacks",
    "data_science": "data preparation, exploration, statistics, visualization, and modeling workflows for insight generation",
}

CONCEPT_DETAILS = {
    "recursion": ("a technique where a function calls itself to solve smaller versions of a problem", ["base case", "recursive case", "stack", "subproblem"]),
    "Big O notation": ("a notation that describes how runtime or memory grows as input size increases", ["complexity", "input size", "upper bound", "scalability"]),
    "SQL": ("a language for defining, querying, and manipulating relational database data", ["tables", "joins", "queries", "schema"]),
    "ACID": ("database transaction properties: atomicity, consistency, isolation, and durability", ["atomicity", "consistency", "isolation", "durability"]),
    "JWT": ("a signed token format for transmitting claims between parties", ["claims", "signature", "expiration", "stateless"]),
    "Docker": ("a containerization platform that packages an application and dependencies into portable images", ["image", "container", "isolation", "deployment"]),
    "Kubernetes": ("an orchestration system for deploying and scaling containers", ["pods", "services", "deployment", "scaling"]),
    "transformers": ("neural architectures using self-attention to model relationships in sequences", ["attention", "tokens", "embeddings", "context"]),
    "SQL injection": ("a vulnerability where attacker-controlled input changes database queries", ["parameterized queries", "input validation", "escaping", "least privilege"]),
}

QUESTION_PATTERNS = [
    "What is {concept} and why is it important?",
    "Explain how {concept} works in practical systems.",
    "Describe a real-world use case for {concept}.",
    "What are common mistakes when using {concept}?",
    "How would you evaluate or debug a problem involving {concept}?",
    "Compare {concept} with related approaches in {domain_label}.",
]

DIFFICULTY_SUFFIX = {
    "beginner": "Focus on the core definition and a simple example.",
    "intermediate": "Include trade-offs, practical constraints, and implementation details.",
    "advanced": "Discuss edge cases, scalability, failure modes, and design decisions.",
}


def normalize_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def concept_reference(domain: str, concept: str, difficulty: str) -> tuple[str, list[str]]:
    if concept in CONCEPT_DETAILS:
        definition, keywords = CONCEPT_DETAILS[concept]
    else:
        domain_desc = DOMAIN_DESCRIPTIONS[domain]
        definition = f"{concept} is part of {domain.replace('_', ' ')} and relates to {domain_desc}"
        keywords = [w for w in re.split(r"[ /_-]+", concept) if len(w) > 1][:3]
        keywords += [domain.split("_")[0], "trade-offs", "implementation"]
    mechanism = {
        "beginner": "identifying the main idea, expected inputs, and observable output",
        "intermediate": "choosing suitable abstractions, measuring trade-offs, and validating behavior with tests",
        "advanced": "handling scale, failure modes, maintainability, security, and operational constraints",
    }[difficulty]
    answer = (
        f"{concept} is {definition}. It works by {mechanism}. "
        f"A strong answer should connect the idea to practical usage, explain important trade-offs, "
        f"and mention key terms such as {', '.join(keywords[:4])}. In an interview, examples and limitations show deeper understanding."
    )
    return answer, list(dict.fromkeys(k.lower() for k in keywords))[:6]


def generate_question_bank() -> tuple[list[dict], dict]:
    bank: list[dict] = []
    refs: dict[str, dict] = {}
    for domain, concepts in CS_DOMAINS.items():
        domain_label = domain.replace("_", " ")
        per_domain: list[dict] = []
        idx = 0
        while len(per_domain) < 52:
            concept = concepts[idx % len(concepts)]
            pattern = QUESTION_PATTERNS[(idx // len(concepts)) % len(QUESTION_PATTERNS)]
            difficulty = ["beginner", "intermediate", "advanced"][idx % 3]
            question = pattern.format(concept=concept, domain_label=domain_label)
            question = f"{question} {DIFFICULTY_SUFFIX[difficulty]}"
            ref, keywords = concept_reference(domain, concept, difficulty)
            item = {
                "id": f"{domain}_{len(per_domain)+1:03d}",
                "question": question,
                "domain": domain,
                "difficulty": difficulty,
                "reference_answer": ref,
                "keywords": keywords,
                "concept": concept,
            }
            per_domain.append(item)
            key = normalize_key(question)
            refs[key] = {
                "domain": domain,
                "difficulty": difficulty,
                "reference_answer": ref,
                "keywords": keywords,
                "min_score_keywords": max(1, min(3, len(keywords) // 2 or 1)),
            }
            idx += 1
        bank.extend(per_domain)
    return bank, refs


def synthetic_rows(question_bank: list[dict], min_rows: int = 5000) -> list[dict]:
    random.seed(42)
    rows = []
    off_topic = [
        "I do not know the answer to this question.",
        "This is mostly about communication and teamwork, not the technical concept.",
        "It is a tool that people use in computers, but I cannot explain details.",
    ]
    for item in question_bank:
        concept = item["concept"]
        ref = item["reference_answer"]
        kws = item["keywords"]
        excellent = ref
        good = f"{concept} means {ref.split('.')[0].lower()}. It is useful in real projects and involves {', '.join(kws[:2])}."
        average = f"{concept} is related to {kws[0] if kws else 'software'} and is used in {item['domain'].replace('_', ' ')}."
        poor = random.choice(off_topic)
        rows.extend([
            {"question": item["question"], "candidate_answer": excellent, "reference_answer": ref, "score_label": 3, "domain": item["domain"], "keywords": ",".join(kws)},
            {"question": item["question"], "candidate_answer": good, "reference_answer": ref, "score_label": 2, "domain": item["domain"], "keywords": ",".join(kws)},
            {"question": item["question"], "candidate_answer": average, "reference_answer": ref, "score_label": 1, "domain": item["domain"], "keywords": ",".join(kws)},
            {"question": item["question"], "candidate_answer": poor, "reference_answer": ref, "score_label": 0, "domain": item["domain"], "keywords": ",".join(kws)},
        ])
    i = 0
    while len(rows) < min_rows:
        item = question_bank[i % len(question_bank)]
        concept = item["concept"]
        kws = item["keywords"]
        label = i % 4
        if label == 3:
            ans = f"{item['reference_answer']} For example, I would test it, monitor behavior, and document trade-offs for maintainability."
        elif label == 2:
            ans = f"{concept} is important because it helps with {kws[0] if kws else 'quality'} and {kws[1] if len(kws)>1 else 'design'}. A practical example should include trade-offs."
        elif label == 1:
            ans = f"{concept} is a technical topic and I know it is used in projects, but I would need to review the details."
        else:
            ans = random.choice(off_topic)
        rows.append({"question": item["question"], "candidate_answer": ans, "reference_answer": item["reference_answer"], "score_label": label, "domain": item["domain"], "keywords": ",".join(kws)})
        i += 1
    return rows


def parse_squad_rows(limit: int = 1200) -> list[dict]:
    path = RAW / "squad_train.json"
    if not path.exists():
        return []
    rows = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        for article in data.get("data", []):
            for para in article.get("paragraphs", []):
                context = para.get("context", "")
                for qa in para.get("qas", []):
                    answers = qa.get("answers") or []
                    if not answers:
                        continue
                    answer = answers[0].get("text", "")
                    question = qa.get("question", "")
                    if question and answer:
                        rows.append({"question": question, "candidate_answer": answer, "reference_answer": answer, "score_label": 3, "domain": "general_qa", "keywords": ""})
                        rows.append({"question": question, "candidate_answer": context[:120], "reference_answer": answer, "score_label": 1, "domain": "general_qa", "keywords": ""})
                    if len(rows) >= limit:
                        return rows
    except Exception as exc:
        print(f"[WARN] Could not parse SQuAD: {exc}")
    return rows


def generate_resume_training() -> pd.DataFrame:
    random.seed(7)
    rows = []
    for i in range(1800):
        skills_count = random.randint(0, 35)
        has_email = random.randint(0, 1)
        has_phone = random.randint(0, 1)
        has_name = random.randint(0, 1)
        word_count = random.randint(80, 1100)
        education_count = random.randint(0, 3)
        exp_years = round(random.random() * 12, 1)
        project_count = random.randint(0, 6)
        cert_count = random.randint(0, 5)
        section_count = random.randint(1, 8)
        heuristic = (
            min(skills_count / 25, 1) * 25
            + (has_email + has_phone + has_name) / 3 * 15
            + min(education_count, 2) / 2 * 15
            + min(exp_years / 5, 1) * 20
            + min(project_count / 4, 1) * 10
            + min(cert_count / 3, 1) * 5
            + (10 if 350 <= word_count <= 900 else 4)
        )
        label = 2 if heuristic >= 70 else 1 if heuristic >= 40 else 0
        rows.append({
            "skills_count": skills_count,
            "has_email": has_email,
            "has_phone": has_phone,
            "has_name": has_name,
            "word_count": word_count,
            "education_count": education_count,
            "experience_years": exp_years,
            "project_count": project_count,
            "cert_count": cert_count,
            "section_count": section_count,
            "ats_label": label,
            "heuristic_score": round(heuristic, 2),
        })
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    q_path = PROCESSED / "question_bank.json"
    r_path = PROCESSED / "reference_answers.json"
    t_path = PROCESSED / "training_data.csv"
    resume_path = PROCESSED / "resume_training_data.csv"
    if not args.force and all(p.exists() for p in [q_path, r_path, t_path, resume_path]):
        print("Processed files already exist. Use --force to regenerate.")
        return

    question_bank, refs = generate_question_bank()
    rows = parse_squad_rows() + synthetic_rows(question_bank, 5000)
    df = pd.DataFrame(rows).dropna()
    if len(df) < 5000:
        raise RuntimeError(f"training_data.csv would have only {len(df)} rows")
    if len(question_bank) < 750:
        raise RuntimeError(f"question_bank.json would have only {len(question_bank)} questions")
    if len(refs) < 500:
        raise RuntimeError(f"reference_answers.json would have only {len(refs)} entries")

    q_path.write_text(json.dumps(question_bank, indent=2), encoding="utf-8")
    r_path.write_text(json.dumps(refs, indent=2), encoding="utf-8")
    df.to_csv(t_path, index=False)
    generate_resume_training().to_csv(resume_path, index=False)
    print(f"Wrote {q_path} ({len(question_bank)} questions)")
    print(f"Wrote {r_path} ({len(refs)} reference answers)")
    print(f"Wrote {t_path} ({len(df)} training rows)")
    print(f"Wrote {resume_path}")


if __name__ == "__main__":
    main()
