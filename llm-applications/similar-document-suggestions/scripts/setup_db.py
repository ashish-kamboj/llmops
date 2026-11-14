# Setup Database + Run init_db.sql
Before running the pipeline, create the database and schema.

import subprocess
import os

# 1. Create the database if it doesn't exist
db_user = os.getenv("DB_USER", "postgres")
db_password = os.getenv("DB_PASSWORD", "postgres")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")

# Connect to default postgres DB to create confluence_recommendation
default_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/postgres"

print("Creating database confluence_recommendation...")
result = subprocess.run(
    ["psql", default_url, "-c", "CREATE DATABASE confluence_recommendation;"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("Database created successfully")
elif "already exists" in result.stderr:
    print("Database already exists")
else:
    print(f"Error: {result.stderr}")

# 2. Run init_db.sql on the new database
target_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/confluence_recommendation"

print("Running init_db.sql...")
result = subprocess.run(
    ["psql", target_url, "-f", "scripts/init_db.sql"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("Database schema created successfully")
else:
    print(f"Error: {result.stderr}")
