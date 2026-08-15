SkillGraph

SkillGraph is a graph-powered talent discovery application built using CognoDB, FastAPI, and JavaScript.

The application models people, skills, companies, and projects as connected entities in a graph. Users can explore professionals and their skills, view connected projects and companies, and discover people whose skills match a project's requirements.

Use Case

SkillGraph addresses a talent discovery problem: finding people whose skills are relevant to a particular project.

Instead of treating people and skills as independent records, SkillGraph represents their relationships directly in a graph.

For example:

Person → HAS_SKILL → Skill
Person → WORKS_AT → Company
Person → WORKS_ON → Project
Project → REQUIRES_SKILL → Skill
Skill → RELATED_TO → Skill

This allows the application to discover connections between people, skills, and projects.

Why a Graph Database?

A graph database is a natural fit for SkillGraph because the application's important questions are about relationships and connections, rather than simple record retrieval.

For example, SkillGraph can:

Find the skills connected to a person.
Find projects connected to a person.
Find people who have the skills required by a project.
Traverse relationships between related skills.
Rank people based on how many skills they share with a project.

In a relational database, these relationships would typically require multiple junction tables and joins. As the number of relationships and traversal depth increases, the queries can become more complicated.

With CognoDB, relationships are first-class graph relationships and Cypher provides a natural way to express multi-hop traversals.

For example:

Person
  ↓ HAS_SKILL
Skill
  ↓ RELATED_TO
Related Skill

This makes graph traversal and relationship-based recommendations easier to express and maintain.

Technology Stack
Backend
Python 3.13
FastAPI
Uvicorn
Official Neo4j Python Driver
openCypher
Database
CognoDB Cloud
Bolt protocol
Graph database
Frontend
HTML
CSS
JavaScript
Development
Visual Studio Code
Git
GitHub
Graph Data Model

SkillGraph contains four primary node types.

Person

Represents a professional.

Example properties:

id
name
title
Skill

Represents a technical or professional skill.

Example properties:

id
name
Company

Represents an organization.

Example properties:

id
name
Project

Represents a project.

Example properties:

id
name
description
Relationships

The graph uses typed relationships:

(Person)-[:HAS_SKILL]->(Skill)


(Skill)-[:RELATED_TO]->(Skill)


(Person)-[:WORKS_AT]->(Company)


(Person)-[:WORKS_ON]->(Project)


(Project)-[:REQUIRES_SKILL]->(Skill)
Data Model Diagram
Example Graph

A simplified example of the data model:

                 ┌──────────────┐
                 │    Skill     │
                 │   Python     │
                 └──────┬───────┘
                        │
                    HAS_SKILL
                        │
                        ▼
                 ┌──────────────┐
                 │    Person    │
                 │Alice Johnson │
                 └──────┬───────┘
                        │
             ┌──────────┴──────────┐
             │                     │
         WORKS_AT              WORKS_ON
             │                     │
             ▼                     ▼
      ┌─────────────┐      ┌──────────────────┐
      │   Company   │      │     Project      │
      │   TechNova  │      │Recommendation    │
      │             │      │     Engine       │
      └─────────────┘      └────────┬─────────┘
                                    │
                              REQUIRES_SKILL
                                    │
                                    ▼
                             ┌──────────────┐
                             │    Skill     │
                             │Machine       │
                             │Learning      │
                             └──────────────┘
Seed Data

The repository contains a database seeding script:

backend/seed.py

The seed script creates realistic sample data including:

8 people
Multiple technical skills
Companies
Projects
Person-to-skill relationships
Skill-to-skill relationships
Person-to-company relationships
Person-to-project relationships
Project-to-skill requirements

The database can be populated by running:

python seed.py
Main Cypher Queries
1. People and Their Skills

The application retrieves people and their directly connected skills.

MATCH (p:Person)-[:HAS_SKILL]->(s:Skill)
RETURN
    p.name AS person,
    p.title AS title,
    collect(s.name) AS skills
ORDER BY p.name

This traverses the graph from a Person node to its connected Skill nodes.

The result is used to display each person's name, job title, and skills.

2. Multi-Hop Skill Traversal

SkillGraph uses a multi-hop graph traversal to find people whose skills are related to a target skill.

MATCH (p:Person)-[:HAS_SKILL]->(person_skill:Skill)
MATCH (person_skill)-[:RELATED_TO*1..2]->(target:Skill)
WHERE target.id = $skill_id
RETURN DISTINCT
    p.name AS person,
    p.title AS title,
    person_skill.name AS matched_skill,
    target.name AS target_skill
ORDER BY p.name

The important part is:

[:RELATED_TO*1..2]

This allows the query to traverse one or two RELATED_TO relationships.

The target skill is passed as a parameter:

$skill_id

rather than being inserted into the Cypher query using string concatenation.

This demonstrates a 2-hop graph traversal, as required by the assignment.

3. Project Skill Matching

The recommendation feature compares the skills required by a project with the skills connected to people.

The graph structure is:

Person
   │
   │ HAS_SKILL
   ▼
 Skill
   ▲
   │ REQUIRES_SKILL
   │
Project

For example, the Recommendation Engine project requires:

Python
Machine Learning
Data Science

The application finds people connected to those skills and ranks them according to their matching skills.

Example result:

Alice Johnson
Matching skills: Python, Machine Learning, Data Science
Match count: 3


Carol Williams
Matching skills: Python, Machine Learning, Data Science
Match count: 3

This relationship-based recommendation is one of the main reasons a graph database is useful for this application.

Parameterized Queries

The application uses parameterized Cypher queries through the official Neo4j Python driver.

For example:

result = tx.run(
    query,
    skill_id=skill_id
)

The Cypher query uses:

$skill_id

instead of concatenating user input into the query string.

This keeps query structure separate from parameter values and avoids string-concatenated Cypher.

Application Features
Dashboard

Provides an overview of the SkillGraph network, including people, skills, projects, and graph information.

People

Users can browse professionals and their connected skills.

Person Profile

Users can open an individual profile and view:

Name
Job title
Skills
Company
Connected projects
Skills

Users can explore the skills available in the graph and the people connected to them.

Projects

Users can explore projects and their required skills.

Project Matching

Users can select a project and see people ranked by matching skills.

API

The backend is implemented using FastAPI.

Method	Endpoint	Description
GET	/	API welcome message
GET	/health	Check API and database connectivity
GET	/api/people	Get all people
GET	/api/people/{person_id}	Get an individual person's profile
GET	/api/skills	Get all skills
GET	/api/projects	Get all projects
GET	/api/projects/{project_id}/matches	Get people matching a project
Example
GET /api/projects/recommendation-engine/matches

This returns people ranked by their matching skills.

Project Structure
skillgraph/
│
├── backend/
│   ├── app.py
│   ├── database.py
│   ├── queries.py
│   ├── seed.py
│   ├── test_connection.py
│   └── .gitignore
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
│
├── .gitignore
└── README.md
CognoDB Setup
1. Create a CognoDB Account

Create an account at:

https://console.cognodb.com/signup

The free tier does not require a credit card.

2. Create a Free Instance

From the CognoDB Cloud console:

Create a new instance.
Select the free c0 tier.
Select a region.
Wait for the instance to become available.
3. Get Connection Details

CognoDB provides a Bolt connection URI and a generated password.

The username is:

cognodb

Use the exact Bolt URI provided by the CognoDB console.

Do not commit the database password to GitHub.

Environment Variables

Create a file:

backend/.env

with:

NEO4J_URI=bolt+s://<your-cognodb-instance>
NEO4J_USERNAME=cognodb
NEO4J_PASSWORD=<your-password>

Replace the placeholder values with your CognoDB credentials.

The .env file is excluded from Git using .gitignore.

Backend Setup

Open PowerShell in the project directory:

cd backend

Create a virtual environment:

python -m venv venv

Activate it:

.\venv\Scripts\Activate.ps1

Install dependencies:

pip install fastapi uvicorn neo4j python-dotenv
Test the Database Connection

Run:

python test_connection.py

A successful connection should show:

Connecting to CognoDB...
Successfully connected to CognoDB!
Database test result: 1
Seed the Database

Run:

python seed.py

Expected result:

Connecting to CognoDB...
Database seeded successfully!
Run the Backend

From the backend directory:

uvicorn app:app --reload

The API will be available at:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs

Health check:

http://127.0.0.1:8000/health
Run the Frontend

The frontend is a static HTML, CSS, and JavaScript application.

Open:

frontend/index.html

using VS Code Live Server.

The frontend communicates with the FastAPI backend.

Error Handling

The application includes error handling for database connectivity failures.

The /health endpoint can be used to verify whether the application can connect to CognoDB.

API database operations return appropriate HTTP errors when the graph database is unavailable instead of exposing database credentials or connection details.

Security

Database credentials are loaded from environment variables and are never stored directly in application source code.

The following files are excluded from Git:

.env
venv/
__pycache__/
.vscode/

The actual CognoDB password is not included in this repository.

Screenshots

Screenshots of the application are included in the repository.

Dashboard

People

Skills

Person Profile

Project Matching

Screen Recording

A short screen recording demonstrates:

Opening the SkillGraph dashboard.
Browsing people.
Opening a person profile.
Exploring skills.
Browsing projects.
Opening the Recommendation Engine.
Viewing graph-based talent matches.

Recording:

https://drive.google.com/file/d/1Us561HxRU7XjMOYo_tmIDJGRZiJJ4QEX/view?usp=sharing

Future Improvements

Possible future improvements include:

Interactive graph visualization
User authentication
Larger real-world datasets
More advanced skill similarity scoring
Location and experience filters
Company-level talent analytics
Additional recommendation algorithms
Author

Vaishnavi
