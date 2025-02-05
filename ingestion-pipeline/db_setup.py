# db_setup.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Replace these with your actual PostgreSQL details
POSTGRES_USER = "fastapi_user"
POSTGRES_PASSWORD = "sri1234a"
POSTGRES_HOST = "34.100.139.218"  # e.g., "123.45.67.89" or "cloudsql-instance-ip"
POSTGRES_PORT = 5432                # default postgres port, adjust if needed
POSTGRES_DB = "Knowledge-Table"

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
