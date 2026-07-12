import json
import random
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def load_bank():
    bank_path = DATA_DIR / "question_bank.json"
    if not bank_path.exists():
        bank_path = DATA_DIR / "processed" / "question_bank.json"
    if bank_path.exists():
        return json.loads(bank_path.read_text(encoding="utf-8"))
    return []


def _fmt(text, max_len=200):
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_len] + "..." if len(text) > max_len else text


def generate_questions(skills, job_role="software engineer", n=12):
    bank = load_bank()
    if not bank:
        bank = _default_bank()
    skill_domain_map = {
        "python": "programming_fundamentals", "java": "programming_fundamentals", "c++": "programming_fundamentals",
        "sql": "databases", "mongodb": "databases", "redis": "databases", "postgresql": "databases",
        "react": "web_development", "javascript": "web_development", "node.js": "web_development",
        "docker": "cloud_devops", "kubernetes": "cloud_devops", "aws": "cloud_devops", "gcp": "cloud_devops",
        "pytorch": "deep_learning", "tensorflow": "deep_learning",
        "pandas": "data_science", "numpy": "data_science", "machine learning": "machine_learning",
        "encryption": "cybersecurity_fundamentals", "oauth": "cybersecurity_fundamentals",
        "android": "mobile_development", "flutter": "mobile_development",
    }
    domains = []
    for s in skills:
        s_lower = s.lower()
        for key, domain in skill_domain_map.items():
            if key in s_lower or s_lower in key:
                domains.append(domain)
    role = (job_role or "").lower()
    if "data" in role:
        domains += ["data_science", "machine_learning", "databases"]
    elif "frontend" in role or "web" in role:
        domains += ["web_development"]
    elif "security" in role:
        domains += ["cybersecurity_fundamentals"]
    elif "devops" in role or "cloud" in role:
        domains += ["cloud_devops"]
    if not domains:
        domains = ["programming_fundamentals", "data_structures", "algorithms", "software_engineering"]
    domains = list(dict.fromkeys(domains))
    pool = [q for q in bank if q.get("domain") in domains] if domains else bank
    if not pool:
        pool = bank
    rng = random.Random(hash(tuple(sorted(skills[:8]))) & 0xFFFF)
    selected = []
    seen = set()
    difficulties = ["beginner", "intermediate", "advanced"]
    diff_weights = [2, 5, 3] if len(skills) > 5 else [4, 4, 2]
    for _ in range(n * 3):
        diff = rng.choices(difficulties, weights=diff_weights, k=1)[0]
        candidates = [q for q in pool if q.get("difficulty") == diff and q.get("id", q.get("question")) not in seen]
        if not candidates:
            candidates = [q for q in pool if q.get("id", q.get("question")) not in seen]
        if not candidates:
            break
        item = rng.choice(candidates)
        item_id = item.get("id", item.get("question"))
        seen.add(item_id)
        selected.append(item)
        if len(selected) >= n:
            break
    if len(selected) < n:
        fallback = [q for q in pool if q.get("id", q.get("question")) not in seen]
        for q in fallback:
            selected.append(q)
            if len(selected) >= n:
                break
    final = []
    seen_text = set()
    for q in selected:
        text = q.get("question", "")
        if text and text not in seen_text:
            final.append(q)
            seen_text.add(text)
        if len(final) >= n:
            break
    return final


def _default_bank():
    return [
        {"id": "ds_1", "domain": "data_structures", "difficulty": "beginner", "question": "What is the difference between an array and a linked list?", "reference_answer": "Arrays store elements contiguously in memory with O(1) index access, while linked lists store elements in nodes with pointers and have O(n) access but O(1) insertion/deletion at ends.", "keywords": ["array", "linked list", "contiguous", "pointer", "O(1)", "O(n)"]},
        {"id": "ds_2", "domain": "data_structures", "difficulty": "intermediate", "question": "How does a hash table work and how are collisions handled?", "reference_answer": "A hash table uses a hash function to map keys to buckets. Collisions are handled via chaining (linked lists in each bucket) or open addressing (probing for the next empty slot).", "keywords": ["hash table", "hash function", "collision", "chaining", "open addressing", "probing"]},
        {"id": "ds_3", "domain": "data_structures", "difficulty": "advanced", "question": "Explain how a balanced binary search tree differs from an array when implementing a sorted set.", "reference_answer": "A balanced BST (like AVL or Red-Black) provides O(log n) search, insert, and delete, while a sorted array offers O(log n) search via binary search but O(n) insert/delete.", "keywords": ["balanced BST", "AVL", "Red-Black", "O(log n)", "binary search", "sorted array"]},
        {"id": "algo_1", "domain": "algorithms", "difficulty": "beginner", "question": "What is Big O notation and why is it used?", "reference_answer": "Big O notation describes the upper bound of an algorithm runtime or space usage relative to input size, allowing comparison of algorithm efficiency independent of hardware.", "keywords": ["Big O", "time complexity", "space complexity", "upper bound", "input size"]},
        {"id": "algo_2", "domain": "algorithms", "difficulty": "intermediate", "question": "Describe how binary search works and its time complexity.", "reference_answer": "Binary search repeatedly divides a sorted array in half, comparing the target to the middle element, achieving O(log n) time complexity.", "keywords": ["binary search", "sorted", "divide", "O(log n)", "middle element"]},
        {"id": "algo_3", "domain": "algorithms", "difficulty": "advanced", "question": "Explain dynamic programming with an example.", "reference_answer": "Dynamic programming solves problems by breaking them into overlapping subproblems, storing results to avoid recomputation. Example: Fibonacci with memoization reduces from O(2^n) to O(n).", "keywords": ["dynamic programming", "overlapping subproblems", "memoization", "tabulation", "optimal substructure"]},
        {"id": "prog_1", "domain": "programming_fundamentals", "difficulty": "beginner", "question": "What is object-oriented programming and its main principles?", "reference_answer": "OOP is a paradigm using objects with data and methods. Main principles are encapsulation, inheritance, polymorphism, and abstraction.", "keywords": ["OOP", "encapsulation", "inheritance", "polymorphism", "abstraction", "object"]},
        {"id": "prog_2", "domain": "programming_fundamentals", "difficulty": "intermediate", "question": "Explain the difference between compiled and interpreted languages.", "reference_answer": "Compiled languages (e.g., C, Go) are translated to machine code before execution, offering faster runtime. Interpreted languages (e.g., Python, JS) are executed line-by-line, offering portability and easier debugging.", "keywords": ["compiled", "interpreted", "machine code", "runtime", "portability", "debugging"]},
        {"id": "prog_3", "domain": "programming_fundamentals", "difficulty": "advanced", "question": "Describe memory management in Python vs C++.", "reference_answer": "Python uses automatic garbage collection with reference counting, while C++ requires manual memory management with new/delete, giving more control but risk of leaks.", "keywords": ["memory management", "garbage collection", "reference counting", "new/delete", "memory leak"]},
        {"id": "web_1", "domain": "web_development", "difficulty": "beginner", "question": "What is the difference between REST and GraphQL?", "reference_answer": "REST uses fixed endpoints returning predefined data structures, while GraphQL allows clients to query exactly the fields they need from a single endpoint.", "keywords": ["REST", "GraphQL", "endpoint", "query", "fields", "API"]},
        {"id": "web_2", "domain": "web_development", "difficulty": "intermediate", "question": "How does JWT authentication work?", "reference_answer": "JWT (JSON Web Token) encodes a payload with a signature using a secret key. The server issues a token on login; the client sends it in the Authorization header for subsequent requests.", "keywords": ["JWT", "authentication", "token", "signature", "Authorization", "payload"]},
        {"id": "web_3", "domain": "web_development", "difficulty": "advanced", "question": "Explain how React's virtual DOM improves performance.", "reference_answer": "React maintains a virtual DOM in memory, computes the diff between updates, and applies minimal real DOM changes via reconciliation, reducing expensive layout recalculations.", "keywords": ["virtual DOM", "reconciliation", "diff", "real DOM", "performance", "React"]},
        {"id": "db_1", "domain": "databases", "difficulty": "beginner", "question": "What is the difference between SQL and NoSQL databases?", "reference_answer": "SQL databases use structured schemas with tables and relations, enforcing ACID. NoSQL databases offer flexible schemas (document, key-value, graph) and scale horizontally with BASE consistency.", "keywords": ["SQL", "NoSQL", "schema", "ACID", "BASE", "horizontal scaling"]},
        {"id": "db_2", "domain": "databases", "difficulty": "intermediate", "question": "Explain database indexing and when it is useful.", "reference_answer": "An index is a data structure (B-tree or hash) that speeds up SELECT queries by reducing scan range. Useful for columns used in WHERE, JOIN, and ORDER BY, but adds write overhead.", "keywords": ["index", "B-tree", "query performance", "SELECT", "WHERE", "JOIN"]},
        {"id": "db_3", "domain": "databases", "difficulty": "advanced", "question": "Describe ACID properties with examples.", "reference_answer": "Atomicity (all or nothing), Consistency (valid state), Isolation (concurrent transactions don't interfere), Durability (committed data persists). Example: bank transfer debiting one account and crediting another.", "keywords": ["ACID", "Atomicity", "Consistency", "Isolation", "Durability", "transaction"]},
        {"id": "cloud_1", "domain": "cloud_devops", "difficulty": "beginner", "question": "What is Docker and how does it differ from a virtual machine?", "reference_answer": "Docker containers share the host OS kernel and are lightweight, starting in seconds. VMs include a full OS with a hypervisor, using more resources but providing stronger isolation.", "keywords": ["Docker", "container", "VM", "hypervisor", "OS kernel", "lightweight"]},
        {"id": "cloud_2", "domain": "cloud_devops", "difficulty": "intermediate", "question": "How does Kubernetes manage container orchestration?", "reference_answer": "Kubernetes automates deployment, scaling, and management of containers using pods, services, deployments, and ingress controllers, with self-healing and rolling updates.", "keywords": ["Kubernetes", "pod", "service", "deployment", "scaling", "orchestration"]},
        {"id": "cloud_3", "domain": "cloud_devops", "difficulty": "advanced", "question": "Explain the principle of infrastructure as code.", "reference_answer": "Infrastructure as Code (IaC) manages infrastructure via machine-readable config files (e.g., Terraform, CloudFormation), enabling version control, reproducibility, and automated provisioning.", "keywords": ["IaC", "Terraform", "CloudFormation", "version control", "reproducibility", "provisioning"]},
        {"id": "ml_1", "domain": "machine_learning", "difficulty": "beginner", "question": "What is the difference between supervised and unsupervised learning?", "reference_answer": "Supervised learning uses labeled data to predict outcomes (e.g., classification, regression). Unsupervised learning finds patterns in unlabeled data (e.g., clustering, dimensionality reduction).", "keywords": ["supervised", "unsupervised", "labeled", "classification", "regression", "clustering"]},
        {"id": "ml_2", "domain": "machine_learning", "difficulty": "intermediate", "question": "Explain overfitting and how to prevent it.", "reference_answer": "Overfitting occurs when a model learns noise instead of signal, performing well on training but poorly on test data. Prevention: cross-validation, regularization (L1/L2), more data, dropout, pruning.", "keywords": ["overfitting", "generalization", "regularization", "cross-validation", "dropout", "bias-variance"]},
        {"id": "ml_3", "domain": "machine_learning", "difficulty": "advanced", "question": "Describe the bias-variance tradeoff.", "reference_answer": "Bias is error from wrong assumptions; variance is error from sensitivity to training data. High bias underfits; high variance overfits. The goal is to find the sweet spot minimizing total error.", "keywords": ["bias", "variance", "underfit", "overfit", "tradeoff", "generalization"]},
        {"id": "dl_1", "domain": "deep_learning", "difficulty": "beginner", "question": "What is a neural network activation function and why is it needed?", "reference_answer": "Activation functions introduce non-linearity, allowing neural networks to learn complex patterns. Examples: ReLU, sigmoid, tanh. Without them, the network would be a linear model.", "keywords": ["activation function", "non-linearity", "ReLU", "sigmoid", "tanh", "neural network"]},
        {"id": "dl_2", "domain": "deep_learning", "difficulty": "intermediate", "question": "How does backpropagation work?", "reference_answer": "Backpropagation computes gradients of the loss with respect to weights using the chain rule, propagating error backward from output to input layers, enabling gradient descent optimization.", "keywords": ["backpropagation", "gradient", "chain rule", "loss", "weight update", "gradient descent"]},
        {"id": "dl_3", "domain": "deep_learning", "difficulty": "advanced", "question": "Explain the Transformer architecture and attention mechanism.", "reference_answer": "Transformers use self-attention to weigh input token importance, enabling parallel processing. Multi-head attention captures different representation subspaces, with positional encoding for sequence order.", "keywords": ["Transformer", "self-attention", "multi-head attention", "positional encoding", "encoder", "decoder"]},
        {"id": "cyber_1", "domain": "cybersecurity_fundamentals", "difficulty": "beginner", "question": "What is the difference between authentication and authorization?", "reference_answer": "Authentication verifies identity (who you are), while authorization determines access rights (what you can do). Example: login is authentication; role-based access is authorization.", "keywords": ["authentication", "authorization", "identity", "access control", "login", "RBAC"]},
        {"id": "cyber_2", "domain": "cybersecurity_fundamentals", "difficulty": "intermediate", "question": "How does OAuth 2.0 work?", "reference_answer": "OAuth 2.0 delegates authorization via tokens. The client requests authorization, gets a code, exchanges it for an access token, and uses the token to access protected resources.", "keywords": ["OAuth 2.0", "authorization", "token", "client", "authorization code", "access token"]},
        {"id": "mobile_1", "domain": "mobile_development", "difficulty": "beginner", "question": "What is the difference between native and cross-platform mobile development?", "reference_answer": "Native development uses platform-specific languages (Swift/Kotlin) for optimal performance and full API access. Cross-platform (React Native, Flutter) shares code across platforms, reducing development time.", "keywords": ["native", "cross-platform", "Swift", "Kotlin", "React Native", "Flutter"]},
        {"id": "mobile_2", "domain": "mobile_development", "difficulty": "intermediate", "question": "Explain the component lifecycle in React Native.", "reference_answer": "React Native components mount (constructor, render, componentDidMount), update (shouldComponentUpdate, render, componentDidUpdate), and unmount (componentWillUnmount), mirroring React's lifecycle.", "keywords": ["React Native", "lifecycle", "mount", "update", "unmount", "componentDidMount"]},
        {"id": "se_1", "domain": "software_engineering", "difficulty": "beginner", "question": "What is the difference between Agile and Waterfall methodologies?", "reference_answer": "Agile is iterative with incremental delivery, adapting to change. Waterfall is sequential with distinct phases (requirements, design, implementation, testing), working best with fixed requirements.", "keywords": ["Agile", "Waterfall", "iterative", "sequential", "phases", "adaptability"]},
        {"id": "se_2", "domain": "software_engineering", "difficulty": "intermediate", "question": "Explain the SOLID principles.", "reference_answer": "SOLID: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion. These principles guide maintainable and extensible object-oriented design.", "keywords": ["SOLID", "Single Responsibility", "Open/Closed", "Liskov", "Interface Segregation", "Dependency Inversion"]},
        {"id": "se_3", "domain": "software_engineering", "difficulty": "advanced", "question": "Describe the CAP theorem.", "reference_answer": "CAP theorem states a distributed system can guarantee at most two of Consistency, Availability, and Partition Tolerance. CP systems prioritize consistency, AP systems prioritize availability during partitions.", "keywords": ["CAP theorem", "Consistency", "Availability", "Partition Tolerance", "distributed system", "CP", "AP"]},
        {"id": "net_1", "domain": "computer_networks", "difficulty": "beginner", "question": "What is the difference between TCP and UDP?", "reference_answer": "TCP is connection-oriented with reliable delivery, ordering, and flow control. UDP is connectionless with no guarantee of delivery, offering lower latency for real-time applications.", "keywords": ["TCP", "UDP", "connection-oriented", "reliable", "connectionless", "latency"]},
        {"id": "net_2", "domain": "computer_networks", "difficulty": "intermediate", "question": "How does DNS resolution work?", "reference_answer": "DNS resolves domain names to IP addresses. The client queries a recursive resolver, which queries root, TLD, and authoritative nameservers, returning the IP address to the client.", "keywords": ["DNS", "domain name", "IP address", "resolver", "nameserver", "recursive"]},
    ]
