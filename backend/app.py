from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import get_driver

app = FastAPI(
    title="SkillGraph API",
    description="Graph-powered talent discovery API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "message": "Welcome to SkillGraph API"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():
    driver = get_driver()

    try:
        driver.verify_connectivity()

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception:
        return {
            "status": "unhealthy",
            "database": "unavailable"
        }


# =========================================================
# GET ALL PEOPLE
# =========================================================

@app.get("/api/people")
def get_people():

    driver = get_driver()

    query = """
    MATCH (p:Person)
    OPTIONAL MATCH (p)-[:HAS_SKILL]->(s:Skill)

    RETURN
        p.id AS id,
        p.name AS name,
        p.title AS title,
        collect(s.name) AS skills

    ORDER BY p.name
    """

    try:

        with driver.session() as session:

            result = session.run(query)

            people = []

            for record in result:

                people.append({
                    "id": record["id"],
                    "name": record["name"],
                    "title": record["title"],
                    "skills": record["skills"]
                })

            return people

    except Exception as e:

        raise HTTPException(
            status_code=503,
            detail="Unable to connect to the graph database."
        )


# =========================================================
# GET ONE PERSON
# =========================================================

@app.get("/api/people/{person_id}")
def get_person(person_id: str):

    driver = get_driver()

    query = """
    MATCH (p:Person {id: $person_id})

    OPTIONAL MATCH (p)-[:HAS_SKILL]->(s:Skill)

    OPTIONAL MATCH (p)-[:WORKED_ON]->(project:Project)

    OPTIONAL MATCH (p)-[:WORKS_AT]->(company:Company)

    RETURN
        p.id AS id,
        p.name AS name,
        p.title AS title,
        collect(DISTINCT s.name) AS skills,
        collect(DISTINCT {
            id: project.id,
            name: project.name,
            description: project.description
        }) AS projects,
        collect(DISTINCT company.name) AS companies
    """

    try:

        with driver.session() as session:

            result = session.run(
                query,
                person_id=person_id
            )

            record = result.single()

            if record is None:

                raise HTTPException(
                    status_code=404,
                    detail="Person not found."
                )

            return {
                "id": record["id"],
                "name": record["name"],
                "title": record["title"],
                "skills": record["skills"],
                "projects": [
                    project
                    for project in record["projects"]
                    if project["id"] is not None
                ],
                "companies": [
                    company
                    for company in record["companies"]
                    if company is not None
                ]
            }

    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=503,
            detail="Unable to connect to the graph database."
        )


# =========================================================
# GET ALL SKILLS
# =========================================================

@app.get("/api/skills")
def get_skills():

    driver = get_driver()

    query = """
    MATCH (s:Skill)

    OPTIONAL MATCH (p:Person)-[:HAS_SKILL]->(s)

    RETURN
        s.id AS id,
        s.name AS name,
        count(p) AS people_count

    ORDER BY s.name
    """

    try:

        with driver.session() as session:

            result = session.run(query)

            skills = []

            for record in result:

                skills.append({
                    "id": record["id"],
                    "name": record["name"],
                    "people_count": record["people_count"]
                })

            return skills

    except Exception:

        raise HTTPException(
            status_code=503,
            detail="Unable to connect to the graph database."
        )


# =========================================================
# GET ALL PROJECTS
# =========================================================

@app.get("/api/projects")
def get_projects():

    driver = get_driver()

    query = """
    MATCH (project:Project)

    OPTIONAL MATCH
        (project)-[:REQUIRES_SKILL]->(skill:Skill)

    OPTIONAL MATCH
        (person:Person)-[:WORKED_ON]->(project)

    RETURN
        project.id AS id,
        project.name AS name,
        project.description AS description,
        collect(DISTINCT skill.name) AS required_skills,
        count(DISTINCT person) AS people_count

    ORDER BY project.name
    """

    try:

        with driver.session() as session:

            result = session.run(query)

            projects = []

            for record in result:

                projects.append({
                    "id": record["id"],
                    "name": record["name"],
                    "description": record["description"],
                    "required_skills": record["required_skills"],
                    "people_count": record["people_count"]
                })

            return projects

    except Exception:

        raise HTTPException(
            status_code=503,
            detail="Unable to connect to the graph database."
        )


# =========================================================
# PROJECT MATCHING
# =========================================================

@app.get("/api/projects/{project_id}/matches")
def get_project_matches(project_id: str):

    driver = get_driver()

    query = """
    MATCH (project:Project {id: $project_id})
          -[:REQUIRES_SKILL]->(required:Skill)

    MATCH (person:Person)
          -[:HAS_SKILL]->(person_skill:Skill)

    OPTIONAL MATCH
        (person_skill)-[:RELATED_TO]->(related_skill:Skill)

    WITH
        person,
        required,
        person_skill,
        related_skill

    WHERE
        person_skill.id = required.id
        OR related_skill.id = required.id

    RETURN
        person.id AS id,
        person.name AS name,
        person.title AS title,
        collect(DISTINCT person_skill.name) AS matched_skills,
        count(DISTINCT required) AS match_count

    ORDER BY
        match_count DESC,
        name
    """

    try:

        print("PROJECT MATCH REQUEST:", project_id)

        with driver.session() as session:

            result = session.run(
                query,
                project_id=project_id
            )

            matches = []

            for record in result:

                matches.append({
                    "id": record["id"],
                    "name": record["name"],
                    "title": record["title"],
                    "matched_skills": record["matched_skills"],
                    "match_count": record["match_count"]
                })

            print("PROJECT MATCH RESULT:", matches)

            return matches

    except Exception as e:

        print("PROJECT MATCH ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )