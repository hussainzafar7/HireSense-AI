import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DOMAINS = {
    "programming_fundamentals": {
        "topics": ["OOP", "recursion", "pointers", "memory management", "SOLID", "exception handling",
                   "generics", "lambda", "concurrency", "multithreading", "async/await", "closures", "interfaces"],
        "languages": ["Python", "Java", "C++", "JavaScript", "TypeScript"]
    },
    "data_structures": {
        "topics": ["arrays", "linked lists", "stacks", "queues", "trees", "BST", "graphs",
                   "hash tables", "heaps", "tries", "segment trees", "BFS", "DFS", "topological sort"]
    },
    "algorithms": {
        "topics": ["Big O notation", "bubble/merge/quick sort", "binary search", "dynamic programming",
                   "greedy", "divide and conquer", "Dijkstra", "Floyd-Warshall", "two pointers",
                   "sliding window", "backtracking", "KMP string matching"]
    },
    "databases": {
        "topics": ["SQL joins", "normalization 1NF-3NF", "indexing", "ACID transactions",
                   "NoSQL vs SQL", "MongoDB", "Redis", "query optimization", "stored procedures",
                   "ER diagrams", "sharding", "replication", "connection pooling"]
    },
    "operating_systems": {
        "topics": ["process vs thread", "CPU scheduling", "deadlock", "memory management",
                   "virtual memory", "paging", "file systems", "semaphores", "mutexes",
                   "context switching", "system calls", "IPC"]
    },
    "computer_networks": {
        "topics": ["OSI model", "TCP vs UDP", "HTTP/HTTPS", "DNS", "IP addressing",
                   "subnetting", "routing protocols", "REST API", "WebSockets", "CDN",
                   "load balancing", "TLS/SSL", "HTTP/2 vs HTTP/3"]
    },
    "software_engineering": {
        "topics": ["SDLC", "Agile", "Scrum", "Git workflow", "CI/CD", "unit testing",
                   "integration testing", "code review", "refactoring", "technical debt",
                   "microservices", "monolith vs microservices", "API design", "versioning"]
    },
    "web_development": {
        "topics": ["HTML/CSS", "JavaScript event loop", "React hooks", "Redux",
                   "Next.js SSR vs CSR", "REST vs GraphQL", "JWT", "OAuth 2.0",
                   "responsive design", "browser storage", "DOM manipulation", "webpack", "PWA"]
    },
    "machine_learning": {
        "topics": ["supervised vs unsupervised", "overfitting", "regularization",
                   "gradient descent", "backpropagation", "feature engineering",
                   "cross-validation", "bias-variance tradeoff", "ensemble methods",
                   "SVM", "decision trees", "random forests", "k-means", "PCA", "ROC AUC"]
    },
    "deep_learning": {
        "topics": ["CNN architecture", "RNN/LSTM", "transformers", "attention mechanism",
                   "transfer learning", "batch normalization", "dropout", "Adam optimizer",
                   "loss functions", "word embeddings", "BERT", "fine-tuning", "GANs"]
    },
    "cloud_devops": {
        "topics": ["Docker", "Kubernetes", "CI/CD pipelines", "AWS S3/EC2/Lambda",
                   "infrastructure as code", "Terraform", "monitoring", "logging",
                   "auto-scaling", "serverless", "container orchestration", "blue-green deployment"]
    },
    "graphic_design_cs": {
        "topics": ["UI/UX principles", "Figma", "wireframing", "color theory",
                   "typography", "responsive design", "accessibility WCAG", "design systems",
                   "prototyping", "vector vs raster", "information architecture"]
    },
    "mobile_development": {
        "topics": ["React Native", "Flutter", "Dart", "app lifecycle", "state management",
                   "SQLite mobile", "push notifications", "native vs cross-platform",
                   "app store deployment", "deep linking", "offline storage"]
    },
    "data_science": {
        "topics": ["pandas", "numpy", "EDA", "statistical analysis", "hypothesis testing",
                   "A/B testing", "data cleaning", "feature selection", "PCA", "Jupyter",
                   "data visualization", "correlation vs causation", "outlier detection"]
    },
    "behavioral": {
        "topics": ["teamwork", "conflict resolution", "leadership", "time management",
                   "failure and learning", "career goals", "work style", "adaptability"]
    },
    "behavioral_experience": {
        "topics": ["past project", "biggest challenge", "debugging hard bug",
                   "learning new technology", "working under pressure", "mentoring others",
                   "disagreement with team", "deadline management"]
    },
    "problem_solving": {
        "topics": ["algorithm design", "system design basics", "debugging approach",
                   "optimization thinking", "trade-off analysis", "estimation problems",
                   "scalability thinking"]
    }
}

def generate_domain_questions(domain_name, domain_config):
    questions = []
    topics = domain_config.get("topics", [])
    languages = domain_config.get("languages", [])

    for topic in topics:
        # Conceptual
        questions.append({
            "question": f"Explain {topic} in your own words with practical examples.",
            "difficulty": "beginner",
            "tags": [topic.lower(), domain_name],
            "keywords": [topic.lower(), "concept", "example"],
            "concepts": ["definition", "application", "example"],
            "follow_up": "Can you provide a real-world scenario where this is useful?",
            "reference_answer": f"{topic} is a core concept in {domain_name}. It involves understanding the fundamental principles and applying them in practical situations."
        })

        # Comparison (if we have pairs)
        if topics and len(topics) >= len(questions) % len(topics) + 1:
            idx = len(questions) % len(topics)
            other = topics[(topics.index(topic) + 1) % len(topics)]
            questions.append({
                "question": f"What is the difference between {topic} and {other}? When would you use each?",
                "difficulty": "intermediate",
                "tags": [topic.lower(), other.lower(), domain_name],
                "keywords": [topic.lower(), other.lower(), "compare", "contrast"],
                "concepts": ["comparison", "trade-offs", "use cases"],
                "follow_up": "What are the performance implications of choosing one over the other?",
                "reference_answer": f"The main difference between {topic} and {other} lies in their approach. {topic} is better suited for certain scenarios while {other} excels in others. The choice depends on your specific requirements."
            })

        # Application
        questions.append({
            "question": f"When would you use {topic} in a real project? Describe the implementation approach.",
            "difficulty": "intermediate",
            "tags": [topic.lower(), domain_name, "practical"],
            "keywords": [topic.lower(), "implementation", "use case", "real-world"],
            "concepts": ["application", "architecture", "implementation"],
            "follow_up": "What alternatives exist and why would you choose this over them?",
            "reference_answer": f"{topic} is applied in real projects when specific requirements demand its unique capabilities. The implementation involves careful planning, following best practices, and testing thoroughly."
        })

        # Deep dive
        questions.append({
            "question": f"What are the implications of {topic} on system performance and scalability?",
            "difficulty": "advanced",
            "tags": [topic.lower(), domain_name, "performance"],
            "keywords": [topic.lower(), "performance", "scalability", "complexity"],
            "concepts": ["performance analysis", "scalability", "optimization"],
            "follow_up": "How would you optimize a system that heavily relies on this concept?",
            "reference_answer": f"The performance implications of {topic} can be significant. It affects memory usage, processing time, and system responsiveness. Proper optimization requires understanding the underlying mechanics."
        })

        # Practical scenario
        questions.append({
            "question": f"Describe a situation where {topic} caused issues in production and how you would resolve them.",
            "difficulty": "advanced",
            "tags": [topic.lower(), domain_name, "troubleshooting"],
            "keywords": [topic.lower(), "debugging", "production", "resolution"],
            "concepts": ["troubleshooting", "problem-solving", "debugging"],
            "follow_up": "What preventive measures would you put in place to avoid similar issues?",
            "reference_answer": f"Production issues with {topic} typically arise from misconfiguration or edge cases. Resolution involves systematic debugging, monitoring, and applying targeted fixes."
        })

    # Language-specific questions for programming domains
    for lang in languages:
        questions.append({
            "question": f"How does {lang} implement or handle {topics[len(questions) % len(topics)]}? What are the best practices?",
            "difficulty": "intermediate",
            "tags": [lang.lower(), domain_name, topics[len(questions) % len(topics)].lower()],
            "keywords": [lang.lower(), "implementation", "best practices"],
            "concepts": ["language features", "idioms", "best practices"],
            "follow_up": "How does this compare to other languages?",
            "reference_answer": f"{lang} provides specific mechanisms for handling this concept. The idiomatic approach follows language conventions and leverages built-in features for optimal results."
        })

    return questions

def generate_all():
    bank = {}
    for domain_name, domain_config in DOMAINS.items():
        questions = generate_domain_questions(domain_name, domain_config)
        bank[domain_name] = {"questions": questions}
        print(f"  {domain_name}: {len(questions)} questions")

    output_path = DATA_DIR / "question_bank.json"
    with open(output_path, "w") as f:
        json.dump(bank, f, indent=2)

    total = sum(len(v["questions"]) for v in bank.values())
    print(f"\nTotal questions generated: {total}")
    return bank

if __name__ == "__main__":
    print("Generating question bank...")
    generate_all()

    print("\nCaching sentence-transformer model...")
    try:
        from sentence_transformers import SentenceTransformer
        model_path = Path(__file__).parent / "models_cache" / "sentence_transformer"
        model_path.parent.mkdir(parents=True, exist_ok=True)
        model = SentenceTransformer("all-MiniLM-L6-v2")
        model.save(str(model_path))
        print(f"Model cached to {model_path}")
    except Exception as e:
        print(f"[WARN] sentence-transformers not available: {e}")
        print("The system will use TF-IDF fallback for answer evaluation.")

    print("\nDone! Question bank ready.")
