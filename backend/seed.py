import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")


driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


# ---------------------------------------------------------
# Sample data
# ---------------------------------------------------------

people = [
    {
        "id": "alice",
        "name": "Alice Johnson",
        "title": "Machine Learning Engineer",
        "company": "TechNova"
    },
    {
        "id": "bob",
        "name": "Bob Smith",
        "title": "Full Stack Developer",
        "company": "CloudWorks"
    },
    {
        "id": "carol",
        "name": "Carol Williams",
        "title": "Data Scientist",
        "company": "TechNova"
    },
    {
        "id": "david",
        "name": "David Kumar",
        "title": "Backend Engineer",
        "company": "DataFlow"
    },
    {
        "id": "emma",
        "name": "Emma Davis",
        "title": "AI Researcher",
        "company": "AI Labs"
    },
    {
        "id": "frank",
        "name": "Frank Wilson",
        "title": "Frontend Engineer",
        "company": "CloudWorks"
    },
    {
        "id": "grace",
        "name": "Grace Lee",
        "title": "NLP Engineer",
        "company": "AI Labs"
    },
    {
        "id": "henry",
        "name": "Henry Brown",
        "title": "DevOps Engineer",
        "company": "DataFlow"
    },
]


skills = [
    {"id": "python", "name": "Python"},
    {"id": "javascript", "name": "JavaScript"},
    {"id": "react", "name": "React"},
    {"id": "machine-learning", "name": "Machine Learning"},
    {"id": "nlp", "name": "Natural Language Processing"},
    {"id": "tensorflow", "name": "TensorFlow"},
    {"id": "pytorch", "name": "PyTorch"},
    {"id": "sql", "name": "SQL"},
    {"id": "docker", "name": "Docker"},
    {"id": "aws", "name": "AWS"},
    {"id": "data-science", "name": "Data Science"},
    {"id": "fastapi", "name": "FastAPI"},
    {"id": "nodejs", "name": "Node.js"},
    {"id": "typescript", "name": "TypeScript"},
]


projects = [
    {
        "id": "recommendation-engine",
        "name": "Recommendation Engine",
        "description": "A machine learning system that recommends products to customers."
    },
    {
        "id": "ai-chatbot",
        "name": "AI Customer Support",
        "description": "An NLP-powered customer support assistant."
    },
    {
        "id": "fraud-detection",
        "name": "Fraud Detection Platform",
        "description": "A system for detecting suspicious financial transactions."
    },
    {
        "id": "ecommerce",
        "name": "E-commerce Platform",
        "description": "A scalable online shopping platform."
    },
    {
        "id": "knowledge-graph",
        "name": "Knowledge Graph Explorer",
        "description": "An application for exploring connected information."
    },
]


# ---------------------------------------------------------
# Seed database
# ---------------------------------------------------------

def seed_database(tx):
    # Companies
    companies = [
        "TechNova",
        "CloudWorks",
        "DataFlow",
        "AI Labs",
    ]

    for company in companies:
        tx.run(
            """
            MERGE (c:Company {name: $name})
            """,
            name=company
        )

    # People
    for person in people:
        tx.run(
            """
            MERGE (p:Person {id: $id})
            SET p.name = $name,
                p.title = $title
            """,
            id=person["id"],
            name=person["name"],
            title=person["title"]
        )

        tx.run(
            """
            MATCH (p:Person {id: $id})
            MATCH (c:Company {name: $company})
            MERGE (p)-[:WORKS_AT]->(c)
            """,
            id=person["id"],
            company=person["company"]
        )

    # Skills
    for skill in skills:
        tx.run(
            """
            MERGE (s:Skill {id: $id})
            SET s.name = $name
            """,
            id=skill["id"],
            name=skill["name"]
        )

    # Projects
    for project in projects:
        tx.run(
            """
            MERGE (p:Project {id: $id})
            SET p.name = $name,
                p.description = $description
            """,
            id=project["id"],
            name=project["name"],
            description=project["description"]
        )

    # -----------------------------------------------------
    # Person -> Skill
    # -----------------------------------------------------

    person_skills = {
        "alice": [
            "python",
            "machine-learning",
            "tensorflow",
            "data-science",
        ],
        "bob": [
            "javascript",
            "react",
            "nodejs",
            "typescript",
            "python",
        ],
        "carol": [
            "python",
            "data-science",
            "machine-learning",
            "sql",
        ],
        "david": [
            "python",
            "fastapi",
            "docker",
            "sql",
        ],
        "emma": [
            "python",
            "pytorch",
            "machine-learning",
            "nlp",
        ],
        "frank": [
            "javascript",
            "react",
            "typescript",
            "docker",
        ],
        "grace": [
            "python",
            "nlp",
            "machine-learning",
            "pytorch",
        ],
        "henry": [
            "docker",
            "aws",
            "python",
            "sql",
        ],
    }

    for person_id, skill_ids in person_skills.items():
        for skill_id in skill_ids:
            tx.run(
                """
                MATCH (p:Person {id: $person_id})
                MATCH (s:Skill {id: $skill_id})
                MERGE (p)-[:HAS_SKILL]->(s)
                """,
                person_id=person_id,
                skill_id=skill_id
            )

    # -----------------------------------------------------
    # Project -> Required skills
    # -----------------------------------------------------

    project_skills = {
        "recommendation-engine": [
            "python",
            "machine-learning",
            "data-science",
        ],
        "ai-chatbot": [
            "python",
            "nlp",
            "machine-learning",
        ],
        "fraud-detection": [
            "python",
            "machine-learning",
            "sql",
        ],
        "ecommerce": [
            "javascript",
            "react",
            "nodejs",
        ],
        "knowledge-graph": [
            "python",
            "fastapi",
            "docker",
        ],
    }

    for project_id, skill_ids in project_skills.items():
        for skill_id in skill_ids:
            tx.run(
                """
                MATCH (p:Project {id: $project_id})
                MATCH (s:Skill {id: $skill_id})
                MERGE (p)-[:REQUIRES_SKILL]->(s)
                """,
                project_id=project_id,
                skill_id=skill_id
            )

    # -----------------------------------------------------
    # Skill relationships
    # -----------------------------------------------------

    related_skills = [
        ("python", "machine-learning"),
        ("machine-learning", "data-science"),
        ("machine-learning", "nlp"),
        ("machine-learning", "tensorflow"),
        ("machine-learning", "pytorch"),
        ("javascript", "typescript"),
        ("javascript", "react"),
        ("javascript", "nodejs"),
        ("docker", "aws"),
        ("python", "fastapi"),
        ("python", "sql"),
    ]

    for skill_a, skill_b in related_skills:
        tx.run(
            """
            MATCH (a:Skill {id: $skill_a})
            MATCH (b:Skill {id: $skill_b})
            MERGE (a)-[:RELATED_TO]->(b)
            """,
            skill_a=skill_a,
            skill_b=skill_b
        )

    # -----------------------------------------------------
    # Person -> Project
    # -----------------------------------------------------

    project_people = {
        "recommendation-engine": ["alice", "carol"],
        "ai-chatbot": ["alice", "emma", "grace"],
        "fraud-detection": ["carol", "david"],
        "ecommerce": ["bob", "frank"],
        "knowledge-graph": ["david", "alice", "henry"],
    }

    for project_id, person_ids in project_people.items():
        for person_id in person_ids:
            tx.run(
                """
                MATCH (p:Person {id: $person_id})
                MATCH (project:Project {id: $project_id})
                MERGE (p)-[:WORKED_ON]->(project)
                """,
                person_id=person_id,
                project_id=project_id
            )

    # -----------------------------------------------------
    # Collaboration relationships
    # -----------------------------------------------------

    collaborations = [
        ("alice", "carol"),
        ("alice", "emma"),
        ("alice", "david"),
        ("emma", "grace"),
        ("bob", "frank"),
        ("carol", "david"),
        ("david", "henry"),
    ]

    for person_a, person_b in collaborations:
        tx.run(
            """
            MATCH (a:Person {id: $person_a})
            MATCH (b:Person {id: $person_b})
            MERGE (a)-[:COLLABORATED_WITH]->(b)
            """,
            person_a=person_a,
            person_b=person_b
        )


def main():
    print("Connecting to CognoDB...")

    try:
        with driver.session() as session:
            session.execute_write(seed_database)

        print("✅ Database seeded successfully!")

    except Exception as e:
        print("❌ Seeding failed.")
        print("Error:", e)

    finally:
        driver.close()


if __name__ == "__main__":
    main()