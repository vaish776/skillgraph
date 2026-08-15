import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


# Load environment variables from .env
load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")


# Connect to CognoDB
driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def get_people_and_skills(tx):
    """
    Query 1:
    Find every person and the skills they have.
    """

    query = """
    MATCH (p:Person)-[:HAS_SKILL]->(s:Skill)
    RETURN p.name AS person,
           p.title AS title,
           collect(s.name) AS skills
    ORDER BY p.name
    """

    result = tx.run(query)

    return list(result)


def find_people_with_related_skill(tx, skill_id):
    """
    Query 2:
    Multi-hop graph traversal.

    Person
      -> HAS_SKILL
      -> Skill
      -> RELATED_TO
      -> Target Skill
    """

    query = """
    MATCH (p:Person)-[:HAS_SKILL]->(person_skill:Skill)
    MATCH (person_skill)-[:RELATED_TO*1..2]->(target:Skill)
    WHERE target.id = $skill_id
    RETURN DISTINCT
        p.name AS person,
        p.title AS title,
        person_skill.name AS matched_skill,
        target.name AS target_skill
    ORDER BY p.name
    """

    result = tx.run(
        query,
        skill_id=skill_id
    )

    return list(result)


def find_people_for_project(tx, project_id):
    """
    Find people whose skills match the skills required by a project.

    A person can match a required skill either:
    1. Directly:
       Person -> HAS_SKILL -> Required Skill

    2. Through one related skill:
       Person -> HAS_SKILL -> Skill -> RELATED_TO -> Required Skill
    """

    query = """
    MATCH (project:Project {id: $project_id})
          -[:REQUIRES_SKILL]->(required:Skill)

    MATCH (person:Person)
          -[:HAS_SKILL]->(person_skill:Skill)

    MATCH path =
          (person_skill)-[:RELATED_TO*0..1]->(required)

    WITH person,
         required,
         person_skill,
         length(path) AS distance

    RETURN
        person.name AS person,
        person.title AS title,
        collect(
            DISTINCT person_skill.name
        ) AS matched_skills,
        count(DISTINCT required) AS match_count,
        min(distance) AS closest_distance

    ORDER BY match_count DESC, closest_distance ASC, person
    """

    result = tx.run(
        query,
        project_id=project_id
    )

    return list(result)


def main():
    print("\nPeople and their skills")
    print("=" * 50)

    try:
        with driver.session() as session:

            # -------------------------------------------------
            # Query 1: People and their direct skills
            # -------------------------------------------------

            records = session.execute_read(
                get_people_and_skills
            )

            for record in records:
                print(f"\n{record['person']}")
                print(f"Title: {record['title']}")
                print("Skills:")

                for skill in record["skills"]:
                    print(f"  - {skill}")

            # -------------------------------------------------
            # Query 2: Multi-hop graph traversal
            # -------------------------------------------------

            print(
                "\n\nPeople with skills related to "
                "Machine Learning"
            )

            print("=" * 50)

            related_people = session.execute_read(
                find_people_with_related_skill,
                "machine-learning"
            )

            for record in related_people:
                print(
                    f"{record['person']} "
                    f"({record['title']}) - "
                    f"{record['matched_skill']} → "
                    f"{record['target_skill']}"
                )
                # -------------------------------------------------
            # Query 3: Project recommendations
            # -------------------------------------------------

            print(
                "\n\nRecommended people for "
                "Recommendation Engine"
            )

            print("=" * 50)

            project_people = session.execute_read(
                find_people_for_project,
                "recommendation-engine"
            )

            for record in project_people:
                print(
                    f"{record['person']} "
                    f"({record['title']})"
                )

                print(
    f"Matching skills: "
    f"{record['matched_skills']}"
)

                print(
                    f"Match count: "
                    f"{record['match_count']}"
                )

                print()
    except Exception as e:
        print("Error:", e)

    finally:
        # Always close the database connection
        driver.close()


if __name__ == "__main__":
    main()