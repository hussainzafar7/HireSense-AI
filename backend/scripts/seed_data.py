"""
HireSense-AI – Seed script.

Creates default companies and 18 realistic job postings for testing.

Run from the backend/ directory:
    venv\Scripts\activate
    python scripts/seed_data.py

Idempotent – skips records if the company email already exists.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db, bcrypt
from models import User, Company, Job

app = create_app()

DEFAULT_PASSWORD = "Test@1234"

COMPANIES = [
    {
        "email": "hr@techcorp.com",
        "company_name": "TechCorp Solutions",
        "industry": "Technology",
        "website": "https://techcorp.com",
        "location": "San Francisco, CA",
        "company_size": "1000-5000",
        "description": "Leading enterprise software company building next-gen cloud infrastructure.",
    },
    {
        "email": "hr@finwave.com",
        "company_name": "FinWave Analytics",
        "industry": "Finance",
        "website": "https://finwave.io",
        "location": "New York, NY",
        "company_size": "500-1000",
        "description": "AI-powered fintech platform revolutionizing real-time market analysis.",
    },
    {
        "email": "hr@healthbase.com",
        "company_name": "HealthBase Inc.",
        "industry": "Healthcare",
        "website": "https://healthbase.com",
        "location": "Boston, MA",
        "company_size": "200-500",
        "description": "Digital health startup building remote patient monitoring solutions.",
    },
]

JOBS = [
    # ---- TechCorp (company index 0) ----
    {
        "company_idx": 0,
        "title": "Senior Frontend Engineer",
        "description": "Build and maintain responsive web applications used by millions. Work with React, TypeScript, and modern CSS frameworks to deliver pixel-perfect UIs.",
        "responsibilities": "Develop new features for customer-facing dashboard; optimize Core Web Vitals; mentor junior engineers; participate in code reviews.",
        "qualifications": "B.S. in Computer Science or equivalent; 5+ years frontend experience; strong portfolio of deployed apps.",
        "required_skills": "React, TypeScript, CSS, JavaScript, HTML, Git",
        "preferred_skills": "Next.js, GraphQL, Tailwind CSS, Docker, Playwright",
        "location": "San Francisco, CA",
        "employment_type": "Full-time",
        "experience_level": "Senior",
        "min_experience_years": 5.0,
        "salary_min": 140000,
        "salary_max": 180000,
        "remote_allowed": True,
    },
    {
        "company_idx": 0,
        "title": "Backend Engineer \u2013 Python",
        "description": "Design and scale distributed microservices powering real-time data pipelines. Own critical APIs handling 10M+ requests/day.",
        "responsibilities": "Architect new microservices; improve database query performance; write unit/integration tests; document APIs.",
        "qualifications": "B.S. in Computer Science; 3+ years building production Python services.",
        "required_skills": "Python, FastAPI, PostgreSQL, Redis, Docker, REST APIs",
        "preferred_skills": "Kubernetes, AWS, Kafka, Celery, SQLAlchemy",
        "location": "San Francisco, CA",
        "employment_type": "Full-time",
        "experience_level": "Mid-Senior",
        "min_experience_years": 3.0,
        "salary_min": 130000,
        "salary_max": 170000,
        "remote_allowed": True,
    },
    {
        "company_idx": 0,
        "title": "DevOps Engineer",
        "description": "Manage multi-cloud infrastructure and CI/CD pipelines. Drive reliability, cost optimization, and incident response.",
        "responsibilities": "Maintain Kubernetes clusters; automate deployments with Terraform; monitor SLOs; conduct post-mortems.",
        "qualifications": "3+ years DevOps/SRE experience; deep knowledge of Linux internals.",
        "required_skills": "Kubernetes, Docker, Terraform, AWS, Linux, CI/CD, Python",
        "preferred_skills": "Helm, Prometheus, Grafana, ArgoCD, GitHub Actions",
        "location": "San Francisco, CA",
        "employment_type": "Full-time",
        "experience_level": "Mid-Senior",
        "min_experience_years": 3.0,
        "salary_min": 135000,
        "salary_max": 175000,
        "remote_allowed": True,
    },
    {
        "company_idx": 0,
        "title": "Data Scientist",
        "description": "Develop ML models that power product recommendations and anomaly detection. Collaborate with product teams on data-driven decisions.",
        "responsibilities": "Build and deploy classification/regression models; perform A/B test analysis; maintain feature store; present findings to stakeholders.",
        "qualifications": "M.S. or Ph.D. in Data Science, Statistics, or related field; 2+ years applied ML experience.",
        "required_skills": "Python, SQL, scikit-learn, Pandas, NumPy, Machine Learning",
        "preferred_skills": "PyTorch, Spark, MLflow, Airflow, Snowflake",
        "location": "San Francisco, CA",
        "employment_type": "Full-time",
        "experience_level": "Mid",
        "min_experience_years": 2.0,
        "salary_min": 145000,
        "salary_max": 190000,
        "remote_allowed": False,
    },
    {
        "company_idx": 0,
        "title": "Product Manager \u2013 Platform",
        "description": "Own the developer platform roadmap. Define requirements, prioritise features, and drive cross-team execution.",
        "responsibilities": "Lead quarterly planning; write PRDs; conduct user research; coordinate engineering, design, and marketing.",
        "qualifications": "4+ years product management experience in B2B SaaS.",
        "required_skills": "Product Management, Agile, JIRA, Data Analysis, A/B Testing",
        "preferred_skills": "Technical background, API products, Figma, SQL",
        "location": "San Francisco, CA",
        "employment_type": "Full-time",
        "experience_level": "Senior",
        "min_experience_years": 4.0,
        "salary_min": 150000,
        "salary_max": 200000,
        "remote_allowed": True,
    },
    {
        "company_idx": 0,
        "title": "Junior Software Engineer",
        "description": "Join our rotational program. Work across frontend, backend, and infrastructure teams to build a strong foundation.",
        "responsibilities": "Implement features under senior guidance; write tests; fix bugs; participate in agile ceremonies.",
        "qualifications": "Recent graduate in Computer Science or bootcamp graduate with a strong portfolio.",
        "required_skills": "Python or JavaScript, Git, HTML, CSS, SQL",
        "preferred_skills": "React, Flask, Docker, Linux",
        "location": "San Francisco, CA",
        "employment_type": "Full-time",
        "experience_level": "Entry",
        "min_experience_years": 0.0,
        "salary_min": 80000,
        "salary_max": 110000,
        "remote_allowed": False,
    },
    # ---- FinWave (company index 1) ----
    {
        "company_idx": 1,
        "title": "Quantitative Developer",
        "description": "Build low-latency trading systems and pricing models. Work at the intersection of finance and software engineering.",
        "responsibilities": "Develop C++ trading engines; implement pricing algorithms; optimise order-book data pipelines.",
        "qualifications": "M.S. in Computer Science, Financial Engineering, or equivalent; 3+ years in quantitative finance.",
        "required_skills": "C++, Python, Financial Modeling, Algorithms, Linux",
        "preferred_skills": "CUDA, FPGAs, KDB+/Q, ZeroMQ, Market Microstructure",
        "location": "New York, NY",
        "employment_type": "Full-time",
        "experience_level": "Senior",
        "min_experience_years": 3.0,
        "salary_min": 200000,
        "salary_max": 350000,
        "remote_allowed": False,
    },
    {
        "company_idx": 1,
        "title": "Full-Stack Engineer \u2013 FinTech",
        "description": "Build the next-generation trading dashboard. Deliver real-time data visualisations and intuitive user experiences.",
        "responsibilities": "Build reactive UI components; connect WebSocket data streams; optimize chart rendering; collaborate with quant team.",
        "qualifications": "3+ years full-stack experience; strong understanding of real-time systems.",
        "required_skills": "TypeScript, React, Node.js, PostgreSQL, WebSockets, Git",
        "preferred_skills": "D3.js, Chart.js, Redis, AWS Lambda, GraphQL",
        "location": "New York, NY",
        "employment_type": "Full-time",
        "experience_level": "Mid",
        "min_experience_years": 3.0,
        "salary_min": 140000,
        "salary_max": 180000,
        "remote_allowed": True,
    },
    {
        "company_idx": 1,
        "title": "Risk Analyst",
        "description": "Monitor portfolio risk and develop quantitative risk models. Present insights to the investment committee.",
        "responsibilities": "Build VaR models; perform stress testing; produce daily risk reports; maintain risk dashboards.",
        "qualifications": "B.S. in Finance, Economics, or STEM; 2+ years risk analysis experience.",
        "required_skills": "Python, SQL, Excel, Statistical Analysis, Risk Management",
        "preferred_skills": "R, Bloomberg Terminal, Tableau, CFA certification",
        "location": "New York, NY",
        "employment_type": "Full-time",
        "experience_level": "Mid",
        "min_experience_years": 2.0,
        "salary_min": 110000,
        "salary_max": 140000,
        "remote_allowed": False,
    },
    {
        "company_idx": 1,
        "title": "Data Engineer",
        "description": "Design and maintain the data lake powering all analytics and ML workflows. Own ETL pipelines processing TBs daily.",
        "responsibilities": "Build reliable ETL pipelines; manage data warehouse schemas; optimize query performance; monitor data quality.",
        "qualifications": "3+ years data engineering; strong SQL and Python skills.",
        "required_skills": "Python, SQL, Spark, Airflow, AWS, Data Warehousing",
        "preferred_skills": "dbt, Snowflake, Kafka, Terraform, Great Expectations",
        "location": "New York, NY",
        "employment_type": "Full-time",
        "experience_level": "Mid-Senior",
        "min_experience_years": 3.0,
        "salary_min": 130000,
        "salary_max": 170000,
        "remote_allowed": True,
    },
    {
        "company_idx": 1,
        "title": "Compliance Officer",
        "description": "Ensure the firm operates within regulatory frameworks. Conduct audits and advise on new regulations.",
        "responsibilities": "Review trading activity for compliance; draft compliance policies; coordinate with regulators; deliver training.",
        "qualifications": "5+ years compliance experience in financial services; knowledge of SEC/FINRA rules.",
        "required_skills": "Regulatory Compliance, Risk Assessment, Audit, Communication",
        "preferred_skills": "Series 7/24 licensed, AML/KYC, Juris Doctor",
        "location": "New York, NY",
        "employment_type": "Full-time",
        "experience_level": "Senior",
        "min_experience_years": 5.0,
        "salary_min": 120000,
        "salary_max": 160000,
        "remote_allowed": False,
    },
    {
        "company_idx": 1,
        "title": "UX Designer \u2013 Trading Platforms",
        "description": "Design interfaces for professional traders. Simplify complex financial data into actionable visual tools.",
        "responsibilities": "Conduct user research; create wireframes and prototypes; run usability tests; maintain design system.",
        "qualifications": "3+ years UX design experience; portfolio demonstrating complex data-heavy interfaces.",
        "required_skills": "Figma, User Research, Prototyping, Design Systems, Usability Testing",
        "preferred_skills": "Motion design, financial domain knowledge, HTML/CSS",
        "location": "New York, NY",
        "employment_type": "Full-time",
        "experience_level": "Mid",
        "min_experience_years": 3.0,
        "salary_min": 120000,
        "salary_max": 155000,
        "remote_allowed": True,
    },
    # ---- HealthBase (company index 2) ----
    {
        "company_idx": 2,
        "title": "Mobile Engineer \u2013 React Native",
        "description": "Build cross-platform patient-facing mobile apps. Deliver a seamless telehealth experience on iOS and Android.",
        "responsibilities": "Develop new features in React Native; integrate HIPAA-compliant APIs; optimize app performance; publish to App Store and Play Store.",
        "qualifications": "3+ years mobile development; published apps on at least one app store.",
        "required_skills": "React Native, TypeScript, iOS, Android, Git, REST APIs",
        "preferred_skills": "Firebase, HealthKit, Google Fit, Detox, Storybook",
        "location": "Boston, MA",
        "employment_type": "Full-time",
        "experience_level": "Mid",
        "min_experience_years": 3.0,
        "salary_min": 120000,
        "salary_max": 155000,
        "remote_allowed": True,
    },
    {
        "company_idx": 2,
        "title": "Clinical Data Specialist",
        "description": "Manage and analyze clinical trial data. Ensure data integrity and regulatory compliance across studies.",
        "responsibilities": "Design case report forms; perform data validation; generate safety reports; coordinate with clinical teams.",
        "qualifications": "B.S. in Life Sciences or related; 2+ years clinical data management experience.",
        "required_skills": "Data Management, Clinical Trials, EDC Systems, Excel, Attention to Detail",
        "preferred_skills": "SAS, R, CDISC standards, Medidata Rave",
        "location": "Boston, MA",
        "employment_type": "Full-time",
        "experience_level": "Mid",
        "min_experience_years": 2.0,
        "salary_min": 85000,
        "salary_max": 110000,
        "remote_allowed": True,
    },
    {
        "company_idx": 2,
        "title": "Security Engineer \u2013 Healthcare",
        "description": "Protect patient data and ensure HIPAA compliance. Lead security architecture and incident response.",
        "responsibilities": "Conduct security assessments; implement IAM policies; manage SIEM; perform penetration testing; lead compliance audits.",
        "qualifications": "4+ years security engineering experience; knowledge of healthcare regulations.",
        "required_skills": "Network Security, AWS Security, IAM, SIEM, Penetration Testing, Python",
        "preferred_skills": "HIPAA/HITRUST, SOC 2, CISSP, Kubernetes Security, WAF",
        "location": "Boston, MA",
        "employment_type": "Full-time",
        "experience_level": "Senior",
        "min_experience_years": 4.0,
        "salary_min": 145000,
        "salary_max": 185000,
        "remote_allowed": False,
    },
    {
        "company_idx": 2,
        "title": "Product Designer \u2013 Health",
        "description": "Design accessible, patient-friendly health applications. Simplify complex medical workflows into intuitive interfaces.",
        "responsibilities": "Design end-to-end patient journey flows; prototype new features; collaborate with clinicians; conduct accessibility audits.",
        "qualifications": "3+ years product design experience; portfolio showing health or complex B2B products.",
        "required_skills": "Figma, User Research, Prototyping, Accessibility, Visual Design",
        "preferred_skills": "Healthcare domain experience, motion design, HTML/CSS",
        "location": "Boston, MA",
        "employment_type": "Full-time",
        "experience_level": "Mid",
        "min_experience_years": 3.0,
        "salary_min": 110000,
        "salary_max": 145000,
        "remote_allowed": True,
    },
    {
        "company_idx": 2,
        "title": "QA Automation Engineer",
        "description": "Build and maintain the automated test suite for web and mobile apps. Champion quality across the engineering org.",
        "responsibilities": "Write end-to-end and integration tests; set up CI test pipelines; track quality metrics; mentor on testing best practices.",
        "qualifications": "3+ years QA automation; strong programming skills in at least one language.",
        "required_skills": "Selenium, Cypress, JavaScript, Python, API Testing, CI/CD",
        "preferred_skills": "Playwright, Appium, Jenkins, Load Testing, Docker",
        "location": "Boston, MA",
        "employment_type": "Full-time",
        "experience_level": "Mid",
        "min_experience_years": 3.0,
        "salary_min": 100000,
        "salary_max": 135000,
        "remote_allowed": True,
    },
    {
        "company_idx": 2,
        "title": "Technical Writer",
        "description": "Create clear, accurate documentation for clinicians, patients, and engineering teams. Own the knowledge base.",
        "responsibilities": "Write API docs, user guides, and release notes; maintain internal wiki; review docs for accuracy; manage translation pipeline.",
        "qualifications": "2+ years technical writing experience; ability to understand complex technical concepts.",
        "required_skills": "Technical Writing, Markdown, Git, Documentation, API Documentation",
        "preferred_skills": "ReadMe, Swagger/OpenAPI, healthcare domain, DITA XML",
        "location": "Boston, MA",
        "employment_type": "Full-time",
        "experience_level": "Mid",
        "min_experience_years": 2.0,
        "salary_min": 85000,
        "salary_max": 110000,
        "remote_allowed": True,
    },
]


def seed():
    with app.app_context():
        existing = User.query.filter_by(email=COMPANIES[0]["email"]).first()
        if existing:
            print("[Seed] Data already exists \u2014 skipping.")
            return

        company_users = []

        for c in COMPANIES:
            pw_hash = bcrypt.generate_password_hash(DEFAULT_PASSWORD).decode("utf-8")
            user = User(
                email=c["email"],
                password_hash=pw_hash,
                role="company",
            )
            db.session.add(user)
            db.session.flush()

            profile = Company(
                user_id=user.id,
                company_name=c["company_name"],
                industry=c["industry"],
                website=c["website"],
                location=c["location"],
                company_size=c["company_size"],
                description=c["description"],
            )
            db.session.add(profile)
            db.session.flush()
            company_users.append(profile)

        for j in JOBS:
            company = company_users[j["company_idx"]]
            job = Job(
                company_id=company.id,
                title=j["title"],
                description=j["description"],
                responsibilities=j.get("responsibilities", ""),
                qualifications=j.get("qualifications", ""),
                required_skills=j["required_skills"],
                preferred_skills=j.get("preferred_skills", ""),
                location=j["location"],
                employment_type=j["employment_type"],
                experience_level=j["experience_level"],
                min_experience_years=j["min_experience_years"],
                salary_min=j["salary_min"],
                salary_max=j["salary_max"],
                remote_allowed=j["remote_allowed"],
                status="open",
            )
            db.session.add(job)

        db.session.commit()

        print(f"[Seed] Created {len(COMPANIES)} companies and {len(JOBS)} jobs.")
        print(f"[Seed] Default password for all companies: {DEFAULT_PASSWORD}")
        for c in COMPANIES:
            print(f"  \u2022 {c['company_name']} \u2014 {c['email']}")


if __name__ == "__main__":
    seed()
