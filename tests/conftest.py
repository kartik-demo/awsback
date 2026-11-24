import importlib
import os
import secrets

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Keep app imports in tests on an in-memory database and a non-production key.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET"] = secrets.token_urlsafe(48)

main = importlib.import_module("main")
Base = main.Base
app = main.app
db_session = main.db_session


@pytest.fixture
def client(tmp_path):
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'test.sqlite3'}",
        connect_args={"check_same_thread": False},
    )
    test_session = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(test_engine)

    def override_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[db_session] = override_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        test_engine.dispose()
