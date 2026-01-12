"""
Pytest 配置文件和共享 fixtures
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client() -> TestClient:
    """
    FastAPI 测试客户端 fixture

    用于单元测试 API 端点
    """
    with TestClient(app) as test_client:
        yield test_client
