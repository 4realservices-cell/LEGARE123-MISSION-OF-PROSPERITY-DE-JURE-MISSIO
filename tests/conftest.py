import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app as main_app
from app.routers import domain as domain_module

temp_db_fd, temp_db_path = tempfile.mkstemp(prefix="test_db_", suffix=".sqlite")
TEST_DATABASE_URL = f"sqlite:///{temp_db_path}"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def app():
    main_app.dependency_overrides[get_db] = override_get_db
    main_app.dependency_overrides[domain_module.VERIFY_OPERATOR] = lambda: {"sub": "test-user", "role": "operator"}
    yield main_app
    main_app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def client(app):
    with TestClient(app) as c:
        yield c


def pytest_sessionfinish(session, exitstatus):
    try:
        Base.metadata.drop_all(bind=engine)
    except Exception:
        pass
    finally:
        try:
            os.close(temp_db_fd)
        except OSError:
            pass
        try:
            os.remove(temp_db_path)
        except OSError:
            pass
