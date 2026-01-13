"""
响应验证 API 端点 (LWP-16)

提供响应验证的 HTTP API
"""
from fastapi import APIRouter, HTTPException
from app.models.validation import ValidationRequest, ValidationResult
from app.services.response_validation import ResponseValidationService
from app.models.socratic import ScaffoldingLevel

router = APIRouter(prefix="/api/v1/validation", tags=["validation"])


@router.post("/validate-response", response_model=ValidationResult)
async def validate_response(request: ValidationRequest):
    """
    验证 AI 生成的响应

    五维验证系统：
    1. 引导性问题检测 (pattern-based)
    2. 直接答案检测 (pattern-based + AI-based)
    3. 脚手架层级对齐检测
    4. 问题质量评估 (AI-based)
    5. 上下文相关性验证 (AI-based)

    Args:
        request: 验证请求，包含响应、脚手架层级、学生上下文

    Returns:
        ValidationResult: 验证结果，包含各维度分数和失败原因

    Example:
        ```json
        {
            "response": "🌱 你觉得如果有 1 个苹果，妈妈又给了你 1 个，现在有几个呢？",
            "scaffolding_level": "moderate",
            "student_context": {
                "grade": 1,
                "problem_type": "math",
                "previous_attempts": ["1 + 1 = 2"]
            }
        }
        ```

    Returns:
        ```json
        {
            "is_valid": true,
            "overall_score": 0.95,
            "guiding_question_score": 1.0,
            "direct_answer_violation": false,
            "scaffolding_alignment_score": 0.9,
            "question_quality_score": 0.95,
            "context_relevance_score": 0.9,
            "failure_reasons": [],
            "suggestions": []
        }
        ```
    """
    try:
        # 创建验证服务
        validator = ResponseValidationService()

        # 执行验证
        result = await validator.validate_socratic_response(
            response=request.response,
            scaffolding_level=request.scaffolding_level,
            student_context=request.student_context
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"验证失败: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "validation"}
