"""
错题本 API 单元测试（Phase 2.2 - US3 - T031）

TDD Phase: Red - 先写失败的测试
测试错题本的记录、查询、统计和练习推荐功能
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch


class TestGetWrongAnswersList:
    """测试获取错题列表"""

    def test_get_wrong_answers_success(self, client: TestClient):
        """
        测试成功获取错题列表

        验收场景：
        给定学生有多条错题记录
        那么系统应返回分页的错题列表
        """
        # Mock the service layer
        with patch('app.api.wrong_answers.practice_service') as mock_service:

            # Mock wrong answers query
            mock_service.get_wrong_answers.return_value = {
                "total": 2,
                "page": 1,
                "page_size": 10,
                "wrong_answers": [
                    {
                        "id": 1,
                        "student_id": 1,
                        "question_content": "3 + 5 = ?",
                        "student_answer": "7",
                        "correct_answer": "8",
                        "error_type": "calculation",
                        "is_resolved": False,
                        "attempts_count": 1,
                        "created_at": "2026-01-12T10:00:00"
                    },
                    {
                        "id": 2,
                        "student_id": 1,
                        "question_content": "你有 5 个苹果，吃掉 3 个，还剩几个？",
                        "student_answer": "8",
                        "correct_answer": "2",
                        "error_type": "concept",
                        "is_resolved": False,
                        "attempts_count": 2,
                        "created_at": "2026-01-12T10:05:00"
                    }
                ]
            }

            response = client.get("/api/v1/wrong-answers?student_id=1&page=1&page_size=10")

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2
            assert len(data["wrong_answers"]) == 2
            assert data["wrong_answers"][0]["error_type"] == "calculation"

    def test_get_wrong_answers_with_filters(self, client: TestClient):
        """
        测试按筛选条件获取错题

        验收场景：
        给定请求包含错误类型和解决状态筛选
        那么系统应返回符合筛选条件的错题
        """
        with patch('app.api.wrong_answers.practice_service') as mock_service:

            mock_service.get_wrong_answers.return_value = {
                "total": 1,
                "page": 1,
                "page_size": 10,
                "wrong_answers": [
                    {
                        "id": 1,
                        "student_id": 1,
                        "question_content": "2 + 3 = ?",
                        "student_answer": "4",
                        "correct_answer": "5",
                        "error_type": "calculation",
                        "is_resolved": False,
                        "attempts_count": 1
                    }
                ]
            }

            response = client.get("/api/v1/wrong-answers?student_id=1&error_type=calculation&is_resolved=false")

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert data["wrong_answers"][0]["error_type"] == "calculation"


class TestGetWrongAnswerDetail:
    """测试获取错题详情"""

    def test_get_wrong_answer_detail_success(self, client: TestClient):
        """
        测试成功获取错题详情

        验收场景：
        给定错题记录 ID
        那么系统应返回该错题的详细信息
        """
        with patch('app.api.wrong_answers.practice_service') as mock_service:

            mock_service.get_wrong_answer_detail.return_value = {
                "id": 1,
                "student_id": 1,
                "question_content": "3 + 5 = ?",
                "student_answer": "7",
                "correct_answer": "8",
                "error_type": "calculation",
                "guidance_type": "hint",
                "guidance_content": "让我来帮你想一想。要不要试试用手指或画图的方式数一数？",
                "is_resolved": False,
                "attempts_count": 1,
                "last_attempt_at": "2026-01-12T10:00:00",
                "created_at": "2026-01-12T10:00:00"
            }

            response = client.get("/api/v1/wrong-answers/1")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1
            assert data["error_type"] == "calculation"
            assert "guidance_content" in data

    def test_get_wrong_answer_not_found(self, client: TestClient):
        """
        测试获取不存在的错题

        验收场景：
        给定错题记录不存在
        那么系统应返回 404 错误
        """
        with patch('app.api.wrong_answers.practice_service') as mock_service:

            mock_service.get_wrong_answer_detail.return_value = None

            response = client.get("/api/v1/wrong-answers/999")

            assert response.status_code == 404


class TestUpdateWrongAnswerStatus:
    """测试更新错题状态"""

    def test_mark_wrong_answer_resolved(self, client: TestClient):
        """
        测试标记错题为已解决

        验收场景：
        给定学生答对了之前的错题
        那么系统应更新错题状态为已解决
        """
        with patch('app.api.wrong_answers.practice_service') as mock_service:

            mock_service.update_wrong_answer_status.return_value = {
                "id": 1,
                "is_resolved": True,
                "resolved_at": "2026-01-12T11:00:00"
            }

            request_data = {
                "is_resolved": True
            }
            response = client.patch("/api/v1/wrong-answers/1", json=request_data)

            assert response.status_code == 200
            data = response.json()
            assert data["is_resolved"] is True
            assert "resolved_at" in data

    def test_update_wrong_answer_invalid_input(self, client: TestClient):
        """
        测试无效的状态更新

        验收场景：
        给定请求包含无效数据
        那么系统应返回 422 错误
        """
        request_data = {
            "invalid_field": "value"
        }
        response = client.patch("/api/v1/wrong-answers/1", json=request_data)

        assert response.status_code == 422


class TestGetWrongAnswerStatistics:
    """测试获取错题统计"""

    def test_get_statistics_success(self, client: TestClient):
        """
        测试成功获取错题统计

        验收场景：
        给定学生有多条错题记录
        那么系统应返回按错误类型分组的统计数据
        """
        with patch('app.api.wrong_answers.practice_service') as mock_service:

            mock_service.get_statistics.return_value = {
                "student_id": 1,
                "total_wrong_answers": 10,
                "resolved_count": 3,
                "unresolved_count": 7,
                "by_error_type": {
                    "calculation": 5,
                    "concept": 3,
                    "understanding": 1,
                    "careless": 1
                },
                "most_common_errors": ["calculation", "concept"]
            }

            response = client.get("/api/v1/wrong-answers/statistics?student_id=1")

            assert response.status_code == 200
            data = response.json()
            assert data["total_wrong_answers"] == 10
            assert data["resolved_count"] == 3
            assert data["by_error_type"]["calculation"] == 5


class TestGetPracticeRecommendations:
    """测试获取练习推荐"""

    def test_get_recommendations_success(self, client: TestClient):
        """
        测试成功获取练习推荐

        验收场景：
        给定学生有错题记录
        那么系统应生成针对性的练习推荐
        """
        with patch('app.api.wrong_answers.practice_service') as mock_service:

            mock_service.generate_recommendations.return_value = {
                "student_id": 1,
                "recommendations": [
                    {
                        "priority": "high",
                        "error_type": "calculation",
                        "similar_questions": [
                            {
                                "id": 101,
                                "question_content": "4 + 6 = ?",
                                "difficulty_level": 1,
                                "question_type": "addition"
                            },
                            {
                                "id": 102,
                                "question_content": "7 + 3 = ?",
                                "difficulty_level": 1,
                                "question_type": "addition"
                            }
                        ],
                        "reason": "该学生在加法计算中多次出错，建议加强练习"
                    },
                    {
                        "priority": "medium",
                        "error_type": "concept",
                        "similar_questions": [
                            {
                                "id": 201,
                                "question_content": "你有 8 个苹果，吃掉 5 个，还剩几个？",
                                "difficulty_level": 1,
                                "question_type": "subtraction"
                            }
                        ],
                        "reason": "该学生对减法概念理解有偏差，建议巩固基础"
                    }
                ],
                "total_count": 2
            }

            response = client.get("/api/v1/wrong-answers/recommendations?student_id=1&limit=5")

            assert response.status_code == 200
            data = response.json()
            assert len(data["recommendations"]) == 2
            assert data["recommendations"][0]["priority"] == "high"
            assert len(data["recommendations"][0]["similar_questions"]) == 2

    def test_get_recommendations_no_wrong_answers(self, client: TestClient):
        """
        测试没有错题时的推荐

        验收场景：
        给定学生没有错题记录
        那么系统应返回空推荐列表
        """
        with patch('app.api.wrong_answers.practice_service') as mock_service:

            mock_service.generate_recommendations.return_value = {
                "student_id": 1,
                "recommendations": [],
                "total_count": 0
            }

            response = client.get("/api/v1/wrong-answers/recommendations?student_id=1")

            assert response.status_code == 200
            data = response.json()
            assert len(data["recommendations"]) == 0
            assert data["total_count"] == 0
