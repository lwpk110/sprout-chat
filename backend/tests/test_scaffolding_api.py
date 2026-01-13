"""
脚手架管理 API 测试 (LWP-15)

测试脚手架管理 API 的所有端点
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.database import Base
from app.models.scaffolding import ScaffoldingLevelRecord, PerformanceMetric
from app.models.socratic import ScaffoldingLevel


# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///./test_scaffolding_api.db"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# 覆盖数据库依赖
def override_get_db():
    """测试数据库会话"""
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


from app.models.database import get_db
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """测试客户端"""
    with TestClient(app) as test_client:
        yield test_client


class TestScaffoldingAPI:
    """测试脚手架管理 API"""

    def test_get_scaffolding_level_new_student(self, client):
        """测试：获取新学生的脚手架层级"""
        # Given: 新学生 ID
        student_id = 201

        # When: 获取脚手架层级
        response = client.get(f"/api/v1/scaffolding/students/{student_id}/level")

        # Then: 应该返回默认层级
        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == student_id
        assert data["problem_domain"] == "general"
        assert data["level"] == "moderate"

    def test_get_scaffolding_level_with_domain(self, client):
        """测试：获取特定领域的脚手架层级"""
        # Given: 学生 ID 和问题领域
        student_id = 202  # 使用独特的 ID
        problem_domain = "math"

        # When: 获取脚手架层级
        response = client.get(
            f"/api/v1/scaffolding/students/{student_id}/level",
            params={"problem_domain": problem_domain}
        )

        # Then: 应该返回对应领域的层级
        assert response.status_code == 200
        data = response.json()
        assert data["problem_domain"] == problem_domain
        assert data["level"] == "moderate"

    def test_set_scaffolding_level(self, client):
        """测试：设置脚手架层级"""
        # Given: 学生 ID
        student_id = 203  # 使用独特的 ID

        # When: 设置新的脚手架层级
        response = client.post(
            f"/api/v1/scaffolding/students/{student_id}/level",
            json={
                "level": "minimal",
                "problem_domain": "math"
            }
        )

        # Then: 应该返回更新后的层级
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == "minimal"
        assert data["problem_domain"] == "math"

        # 验证层级确实被更新
        get_response = client.get(
            f"/api/v1/scaffolding/students/{student_id}/level",
            params={"problem_domain": "math"}
        )
        assert get_response.json()["level"] == "minimal"

    def test_get_performance_metrics_empty(self, client):
        """测试：获取空的表现指标"""
        # Given: 学生 ID
        student_id = 204  # 使用独特的 ID

        # When: 获取表现指标
        response = client.get(f"/api/v1/scaffolding/students/{student_id}/performance")

        # Then: 应该返回空列表
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_performance_metrics_with_domain(self, client):
        """测试：获取特定领域的表现指标"""
        # Given: 学生 ID 和问题领域
        student_id = 205  # 使用独特的 ID
        problem_domain = "math"

        # When: 获取表现指标
        response = client.get(
            f"/api/v1/scaffolding/students/{student_id}/performance",
            params={"problem_domain": problem_domain, "limit": 5}
        )

        # Then: 应该返回成功
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_performance_stats(self, client):
        """测试：获取表现统计"""
        # Given: 学生 ID
        student_id = 206  # 使用独特的 ID

        # When: 获取表现统计
        response = client.get(
            f"/api/v1/scaffolding/students/{student_id}/performance/stats",
            params={"problem_domain": "math"}
        )

        # Then: 应该返回统计数据
        assert response.status_code == 200
        data = response.json()
        assert "total_attempts" in data
        assert "correct_count" in data
        assert "accuracy" in data
        assert "avg_hints_needed" in data
        assert "current_level" in data
