"""
知识点图谱 API 单元测试（Phase 2.2 - US4 - T041）

TDD Phase: Red - 先写失败的测试
测试知识点图谱的建立、掌握度追踪和学习路径推荐功能
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch


class TestGetKnowledgePoints:
    """测试获取知识点列表"""

    def test_get_knowledge_points_success(self, client: TestClient):
        """
        测试成功获取知识点列表

        验收场景：
        给定系统中有多个知识点
        那么系统应返回知识点列表，支持按科目和难度筛选
        """
        with patch('app.api.knowledge.KnowledgeTrackerService') as mock_service:
            mock_instance = Mock()
            mock_service.return_value = mock_instance

            mock_instance.get_knowledge_points.return_value = {
                "total": 3,
                "knowledge_points": [
                    {
                        "id": 1,
                        "name": "加法基础",
                        "subject": "math",
                        "difficulty_level": 1,
                        "description": "10 以内的加法运算",
                        "parent_id": None
                    },
                    {
                        "id": 2,
                        "name": "减法基础",
                        "subject": "math",
                        "difficulty_level": 1,
                        "description": "10 以内的减法运算",
                        "parent_id": None
                    },
                    {
                        "id": 3,
                        "name": "进位加法",
                        "subject": "math",
                        "difficulty_level": 2,
                        "description": "20 以内的进位加法",
                        "parent_id": 1
                    }
                ]
            }

            response = client.get("/api/v1/knowledge-points?subject=math")

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 3
            assert len(data["knowledge_points"]) == 3

    def test_get_knowledge_points_with_filters(self, client: TestClient):
        """
        测试按筛选条件获取知识点

        验收场景：
        给定请求包含科目和难度筛选
        那么系统应返回符合筛选条件的知识点
        """
        with patch('app.api.knowledge.KnowledgeTrackerService') as mock_service:
            mock_instance = Mock()
            mock_service.return_value = mock_instance

            mock_instance.get_knowledge_points.return_value = {
                "total": 2,
                "knowledge_points": [
                    {
                        "id": 1,
                        "name": "加法基础",
                        "subject": "math",
                        "difficulty_level": 1
                    },
                    {
                        "id": 2,
                        "name": "减法基础",
                        "subject": "math",
                        "difficulty_level": 1
                    }
                ]
            }

            response = client.get("/api/v1/knowledge-points?subject=math&difficulty_level=1")

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2


class TestGetKnowledgePointDetail:
    """测试获取知识点详情"""

    def test_get_knowledge_point_detail_success(self, client: TestClient):
        """
        测试成功获取知识点详情

        验收场景：
        给定知识点 ID
        那么系统应返回该知识点的详细信息
        """
        with patch('app.api.knowledge.KnowledgeTrackerService') as mock_service:
            mock_instance = Mock()
            mock_service.return_value = mock_instance

            mock_instance.get_knowledge_point_detail.return_value = {
                "id": 1,
                "name": "加法基础",
                "subject": "math",
                "difficulty_level": 1,
                "description": "10 以内的加法运算",
                "parent_id": None,
                "prerequisites": [],
                "children": [
                    {"id": 3, "name": "进位加法"}
                ]
            }

            response = client.get("/api/v1/knowledge-points/1")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1
            assert data["name"] == "加法基础"

    def test_get_knowledge_point_not_found(self, client: TestClient):
        """
        测试获取不存在的知识点

        验收场景：
        给定知识点 ID 不存在
        那么系统应返回 404 错误
        """
        with patch('app.api.knowledge.KnowledgeTrackerService') as mock_service:
            mock_instance = Mock()
            mock_service.return_value = mock_instance

            mock_instance.get_knowledge_point_detail.return_value = None

            response = client.get("/api/v1/knowledge-points/999")

            assert response.status_code == 404


class TestGetKnowledgeGraph:
    """测试获取知识点图谱"""

    def test_get_knowledge_graph_success(self, client: TestClient):
        """
        测试成功获取知识点图谱

        验收场景：
        给定请求获取知识点图谱
        那么系统应返回 DAG 结构的图谱
        """
        with patch('app.api.knowledge.KnowledgeTrackerService') as mock_service:
            mock_instance = Mock()
            mock_service.return_value = mock_instance

            mock_instance.get_knowledge_graph.return_value = {
                "nodes": [
                    {"id": 1, "name": "加法基础", "subject": "math"},
                    {"id": 2, "name": "减法基础", "subject": "math"},
                    {"id": 3, "name": "进位加法", "subject": "math"}
                ],
                "edges": [
                    {"from": 1, "to": 3, "type": "prerequisite"},
                    {"from": 2, "to": 3, "type": "related"}
                ]
            }

            response = client.get("/api/v1/knowledge-points/graph?subject=math")

            assert response.status_code == 200
            data = response.json()
            assert "nodes" in data
            assert "edges" in data
            assert len(data["nodes"]) == 3


class TestGetKnowledgeMastery:
    """测试查询知识点掌握情况"""

    def test_get_mastery_success(self, client: TestClient):
        """
        测试成功获取知识点掌握情况

        验收场景：
        给定学生 ID
        那么系统应返回该学生的知识点掌握情况
        """
        with patch('app.api.knowledge.KnowledgeTrackerService') as mock_service:
            mock_instance = Mock()
            mock_service.return_value = mock_instance

            mock_instance.get_student_mastery.return_value = {
                "student_id": 1,
                "total_points": 10,
                "mastered_count": 7,
                "in_progress_count": 2,
                "not_started_count": 1,
                "mastery_records": [
                    {
                        "id": 1,
                        "knowledge_point_id": 1,
                        "knowledge_point_name": "加法基础",
                        "mastery_percentage": 85.5,
                        "status": "mastered"
                    },
                    {
                        "id": 2,
                        "knowledge_point_id": 2,
                        "knowledge_point_name": "减法基础",
                        "mastery_percentage": 60.0,
                        "status": "in_progress"
                    }
                ]
            }

            response = client.get("/api/v1/knowledge-mastery?student_id=1")

            assert response.status_code == 200
            data = response.json()
            assert data["student_id"] == 1
            assert data["mastered_count"] == 7
            assert len(data["mastery_records"]) == 2


class TestUpdateKnowledgeMastery:
    """测试更新知识点掌握度"""

    def test_update_mastery_success(self, client: TestClient):
        """
        测试成功更新知识点掌握度

        验收场景：
        给定掌握度更新请求
        那么系统应更新掌握度并返回更新后的记录
        """
        with patch('app.api.knowledge.KnowledgeTrackerService') as mock_service:
            mock_instance = Mock()
            mock_service.return_value = mock_instance

            mock_instance.update_mastery.return_value = {
                "id": 1,
                "student_id": 1,
                "knowledge_point_id": 1,
                "mastery_percentage": 90.0,
                "status": "mastered"
            }

            request_data = {
                "mastery_percentage": 90.0
            }
            response = client.patch("/api/v1/knowledge-mastery/1", json=request_data)

            assert response.status_code == 200
            data = response.json()
            assert data["mastery_percentage"] == 90.0
            assert data["status"] == "mastered"


class TestGetLearningPathRecommendations:
    """测试获取学习路径推荐"""

    def test_get_learning_path_success(self, client: TestClient):
        """
        测试成功获取学习路径推荐

        验收场景：
        给定学生 ID
        那么系统应基于前置知识点生成学习路径推荐
        """
        with patch('app.api.knowledge.KnowledgeTrackerService') as mock_service:
            mock_instance = Mock()
            mock_service.return_value = mock_instance

            mock_instance.generate_learning_path.return_value = {
                "student_id": 1,
                "recommended_path": [
                    {
                        "order": 1,
                        "knowledge_point": {
                            "id": 1,
                            "name": "加法基础",
                            "difficulty_level": 1
                        },
                        "prerequisites_met": True,
                        "reason": "前置知识点已掌握，可以开始学习"
                    },
                    {
                        "order": 2,
                        "knowledge_point": {
                            "id": 3,
                            "name": "进位加法",
                            "difficulty_level": 2
                        },
                        "prerequisites_met": False,
                        "reason": "需要先掌握加法基础"
                    }
                ]
            }

            response = client.get("/api/v1/knowledge-mastery/recommendations?student_id=1")

            assert response.status_code == 200
            data = response.json()
            assert len(data["recommended_path"]) == 2
            assert data["recommended_path"][0]["order"] == 1

    def test_get_learning_path_no_prerequisites(self, client: TestClient):
        """
        测试没有前置知识点时的推荐

        验收场景：
        给定学生学习的是基础知识点（无前置）
        那么系统应推荐直接开始学习
        """
        with patch('app.api.knowledge.KnowledgeTrackerService') as mock_service:
            mock_instance = Mock()
            mock_service.return_value = mock_instance

            mock_instance.generate_learning_path.return_value = {
                "student_id": 1,
                "recommended_path": [
                    {
                        "order": 1,
                        "knowledge_point": {
                            "id": 1,
                            "name": "加法基础",
                            "difficulty_level": 1
                        },
                        "prerequisites_met": True,
                        "reason": "基础知识点，可以直接开始学习"
                    }
                ]
            }

            response = client.get("/api/v1/knowledge-mastery/recommendations?student_id=1")

            assert response.status_code == 200
            data = response.json()
            assert len(data["recommended_path"]) == 1
            assert data["recommended_path"][0]["prerequisites_met"] is True
