
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os

# Find the .env file in the project root
PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL not found. Check your project-root .env file."
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 15},
)

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Database connection successful!")
        print("Test query result:", result.scalar())
except Exception as error:
    print("Database connection failed.")
    print("Error type:", type(error).__name__)
    print("Check your connection settings and credentials.")
    raise
finally:
    engine.dispose()