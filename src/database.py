"""Database (placeholder)"""
from sqlalchemy import create_engine
def engine(db_path="sqlite:///data/oneflow.db"):
    return create_engine(db_path, future=True)
