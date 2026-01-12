"""
Unit test configuration with mocked dependencies
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app


@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock()


@pytest.fixture
def client(mock_db) -> TestClient:
    """
    FastAPI test client with mocked database dependency

    This fixture overrides the get_db dependency to avoid database access
    in unit tests, ensuring they remain fast and isolated.
    """
    def override_get_db():
        yield mock_db

    from app.models.database import get_db
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_knowledge_tracker_service():
    """Mock KnowledgeTrackerService"""
    with patch('app.services.knowledge_tracker.KnowledgeTrackerService') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_practice_recommender_service():
    """Mock PracticeRecommenderService"""
    with patch('app.services.practice_recommender.PracticeRecommenderService') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_socratic_teacher_service():
    """Mock SocraticTeacherService"""
    with patch('app.services.socratic_teacher.SocraticTeacherService') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance
