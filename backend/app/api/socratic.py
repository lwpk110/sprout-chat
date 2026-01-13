"""
苏格拉底响应 API 端点 (LWP-13)

提供 RESTful API 用于生成苏格拉底引导式响应
"""
from fastapi import APIRouter, HTTPException, status
from app.models.socratic import (
    SocraticRequest,
    SocraticResponse,
    SocraticError
)
from app.services.socratic_response import SocraticResponseService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/socratic", tags=["苏格拉底教学"])

# 创建服务实例
socratic_service = SocraticResponseService()


@router.post("/generate", response_model=SocraticResponse)
async def generate_socratic_response(request: SocraticRequest):
    """
    生成苏格拉底引导式响应

    ## 功能说明
    通过 Claude API 生成符合苏格拉底教学法的引导式响应，引导学生思考而不是直接给出答案。

    ## 请求参数
    - **student_message**: 学生的输入消息（必需）
    - **problem_context**: 问题背景（可选，如 OCR 识别的题目）
    - **scaffolding_level**: 脚手架层级（默认: moderate）
      - `highly_guided`: 高度引导（学生完全不懂）
      - `moderate`: 中度引导（学生有一些思路）
      - `minimal`: 最小引导（学生理解较好）
    - **conversation_id**: 会话 ID（可选）
    - **conversation_history**: 对话历史（可选）
    - **student_level**: 学生年级水平（可选）

    ## 响应示例
    ```json
    {
        "response": "🌱 你觉得如果有 1 个苹果，妈妈又给了你 1 个，现在有几个呢？",
        "is_socratic": true,
        "validation_score": 0.95,
        "scaffolding_level": "moderate",
        "validation_result": {
            "is_valid": true,
            "contains_question": true,
            "contains_direct_answer": false,
            "tone_appropriate": true,
            "length_appropriate": true,
            "score": 0.95,
            "reasons": ["包含引导性问题", "语气温柔鼓励", "长度适中"]
        },
        "metadata": {
            "model": "claude-3-5-sonnet",
            "provider": "anthropic",
            "conversation_id": "conv-123"
        }
    }
    ```

    ## 错误响应
    ```json
    {
        "error": "ValidationError",
        "message": "学生消息不能为空",
        "details": {}
    }
    ```

    ## 使用示例
    ```python
    import requests

    response = requests.post("http://localhost:8000/api/v1/socratic/generate", json={
        "student_message": "1 + 1 = ?",
        "problem_context": "数学加法题",
        "scaffolding_level": "moderate"
    })

    print(response.json())
    ```
    """
    try:
        # 调用服务生成响应
        response = await socratic_service.generate_response(
            student_message=request.student_message,
            problem_context=request.problem_context,
            scaffolding_level=request.scaffolding_level.value,
            conversation_history=request.conversation_history,
            conversation_id=request.conversation_id,
            student_level=request.student_level
        )

        logger.info(
            f"生成苏格拉底响应成功: "
            f"is_socratic={response.is_socratic}, "
            f"score={response.validation_score:.2f}"
        )

        return response

    except ValueError as e:
        # 输入验证错误
        logger.error(f"输入验证错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "ValidationError",
                "message": str(e),
                "details": {}
            }
        )

    except Exception as e:
        # 服务器错误
        logger.error(f"生成苏格拉底响应失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalError",
                "message": "生成响应时发生错误，请稍后重试",
                "details": {
                    "raw_error": str(e) if logger.level <= logging.DEBUG else None
                }
            }
        )


@router.get("/health")
async def health_check():
    """
    健康检查端点

    用于监控服务状态
    """
    return {
        "status": "healthy",
        "service": "socratic-response",
        "version": "1.0.0"
    }


@router.get("/scaffolding-levels")
async def get_scaffolding_levels():
    """
    获取支持的脚手架层级

    返回所有可用的脚手架层级及其说明
    """
    return {
        "scaffolding_levels": [
            {
                "value": "highly_guided",
                "label": "高度引导",
                "description": "适用于学生完全不懂，需要较多帮助的场景",
                "example": "让我们先看看题目里有几个数字。你找到了吗？"
            },
            {
                "value": "moderate",
                "label": "中度引导",
                "description": "适用于学生有一些思路，需要适度引导的场景（默认）",
                "example": "你觉得这道题应该先算哪一步？为什么？"
            },
            {
                "value": "minimal",
                "label": "最小引导",
                "description": "适用于学生理解较好，只需要点拨的场景",
                "example": "你的方法很有创意！还有其他方法吗？"
            }
        ]
    }
