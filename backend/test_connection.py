import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


# Load the credentials from .env
load_dotenv()

uri = os.getenv("COGNODB_URI")
username = os.getenv("COGNODB_USERNAME")
password = os.getenv("COGNODB_PASSWORD")

print("Connecting to CognoDB...")

driver = GraphDatabase.driver(
    uri,
    auth=(username, password)
)

try:
    # Check whether the database is reachable
    driver.verify_connectivity()

    print("Successfully connected to CognoDB!")

    # Run a very simple Cypher query
    with driver.session() as session:
        result = session.run("RETURN 1 AS result")
        record = result.single()

        print("Database test result:", record["result"])

except Exception as e:
    print("Could not connect to CognoDB.")
    print("Error:", e)

finally:
    driver.close()