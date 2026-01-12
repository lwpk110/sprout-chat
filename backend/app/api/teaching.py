"""
引导教学 API 端点（Phase 2.2 - US2）

提供苏格拉底式引导教学的 API 接口
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel, Field

from app.services.socratic_teacher import SocraticTeacherService
from app.services.wrong_analyzer import WrongAnswerClassifier
from app.services.response_validator import ResponseValidator


router = APIRouter(prefix="/api/v1/teaching", tags=["引导教学"])

# 服务实例
socratic_service = SocraticTeacherService()
wrong_classifier = WrongAnswerClassifier()
response_validator = ResponseValidator()


# =============================================================================
# 请求/响应模型
# =============================================================================

class GenerateGuidanceRequest(BaseModel):
    """生成引导式反馈请求"""
    question: str = Field(..., min_length=1, max_length=1000, description="问题内容")
    student_answer: str = Field(..., min_length=1, max_length=500, description="学生答案")
    correct_answer: str = Field(..., min_length=1, max_length=500, description="正确答案")
    error_type: str = Field(
        default=None,
        description="错误类型（可选，系统会自动判断）"
    )
    attempts: int = Field(default=1, ge=1, le=10, description="尝试次数")


class ValidateGuidanceRequest(BaseModel):
    """验证引导式反馈请求"""
    response: str = Field(..., min_length=1, max_length=2000, description="引导式响应内容")
    question: str = Field(..., min_length=1, max_length=1000, description="问题内容")
    correct_answer: str = Field(..., min_length=1, max_length=500, description="正确答案")


class GenerateGuidanceResponse(BaseModel):
    """生成引导式反馈响应"""
    guidance_type: str = Field(..., description="引导类型")
    content: str = Field(..., description="引导内容")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class ValidateGuidanceResponse(BaseModel):
    """验证引导式反馈响应"""
    valid: bool = Field(..., description="是否通过验证")
    reason: str = Field(..., description="原因说明")
    layer: int = Field(..., description="验证层级")


class GuidanceTypeInfo(BaseModel):
    """引导类型信息"""
    type: str = Field(..., description="类型代码")
    name: str = Field(..., description="类型名称")
    description: str = Field(..., description="类型描述")
    applicable_scenarios: List[str] = Field(default_factory=list, alias="适用场景", description="适用场景")

    model_config = {"populate_by_name": True}


class GuidanceTypesResponse(BaseModel):
    """引导类型列表响应"""
    guidance_types: List[GuidanceTypeInfo] = Field(..., description="引导类型列表")


# =============================================================================
# API 端点
# =============================================================================

@router.post("/guidance", response_model=GenerateGuidanceResponse, status_code=200)
async def generate_guidance(request: GenerateGuidanceRequest) -> GenerateGuidanceResponse:
    """
    生成引导式反馈（T025）

    根据学生的错误答案，生成苏格拉底式引导反馈，帮助学生自己思考找到正确答案。

    ## 功能说明
    - 自动判断错误类型（如果未提供）
    - 根据错误类型和尝试次数选择合适的引导策略
    - 生成不包含直接答案的引导式反馈
    - 验证响应不泄露答案

    ## 引导类型
    1. **clarify** (澄清型): 澄清学生的理解
    2. **hint** (提示型): 给出提示但不直接给答案
    3. **break_down** (分解型): 将问题分解为小步骤
    4. **visualize** (可视化型): 建议用画图等可视化方式
    5. **check_work** (检查型): 引导学生检查自己的答案
    6. **alternative_method** (替代方法型): 建议用其他方法
    7. **encourage** (鼓励型): 给予鼓励和信心

    ## 错误类型
    - **calculation**: 计算错误（运算步骤正确但结果错误）
    - **concept**: 概念错误（混淆运算方法）
    - **understanding**: 理解错误（题意理解偏差）
    - **careless**: 粗心错误（笔误、抄错数字）

    ## 示例
    ```json
    {
      "question": "3 + 5 = ?",
      "student_answer": "7",
      "correct_answer": "8",
      "attempts": 1
    }
    ```

    ## 响应时间
    - 目标：< 3 秒（SC-002）
    """
    try:
        # 如果未提供错误类型，自动判断
        error_type = request.error_type
        if error_type is None:
            error_type = wrong_classifier.classify(
                question=request.question,
                student_answer=request.student_answer,
                correct_answer=request.correct_answer,
                attempts=request.attempts
            )

        # 生成引导式反馈
        guidance = socratic_service.generate_guidance(
            question=request.question,
            student_answer=request.student_answer,
            correct_answer=request.correct_answer,
            error_type=error_type,
            attempts=request.attempts
        )

        return GenerateGuidanceResponse(
            guidance_type=guidance["guidance_type"],
            content=guidance["content"],
            metadata=guidance["metadata"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成引导式反馈失败: {str(e)}"
        )


@router.post("/guidance/validate", response_model=ValidateGuidanceResponse, status_code=200)
async def validate_guidance(request: ValidateGuidanceRequest) -> ValidateGuidanceResponse:
    """
    验证引导式反馈（T025）

    验证引导式响应是否包含直接答案，确保不违反教学原则。

    ## 功能说明
    - **Layer 1**: 关键词检测（"答案是"、"等于"等）
    - **Layer 2**: 答案检测（数字匹配、表达式匹配）
    - **Layer 3**: AI 二次验证（可选）

    ## 验证标准
    - 响应不应包含直接答案
    - 响应应通过提问引导学生思考
    - 目标准确率：95%（SC-003）

    ## 示例
    ```json
    {
      "response": "让我来帮你检查一下。用手指或画图的方式数一数，3 加 5 等于多少呢？",
      "question": "3 + 5 = ?",
      "correct_answer": "8"
    }
    ```

    ## 响应
    - **valid**: true - 通过验证（不包含答案）
    - **valid**: false - 未通过验证（包含答案）
    - **reason**: 原因说明
    - **layer**: 验证层级（1-3）
    """
    try:
        result = response_validator.validate_response(
            response=request.response,
            correct_answer=request.correct_answer,
            question=request.question
        )

        return ValidateGuidanceResponse(
            valid=result["valid"],
            reason=result.get("reason", ""),
            layer=result.get("layer", 0)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"验证引导式反馈失败: {str(e)}"
        )


@router.get("/guidance/types", response_model=GuidanceTypesResponse, status_code=200)
async def get_guidance_types() -> GuidanceTypesResponse:
    """
    获取引导类型列表（T025）

    返回所有支持的引导类型及其说明。

    ## 引导类型说明

    ### 1. clarify (澄清型)
    - **适用场景**: 学生对问题理解有偏差
    - **示例**: "让我确认一下你的理解。题目说的是你一共有多少个苹果，还是需要吃掉多少个？"

    ### 2. hint (提示型)
    - **适用场景**: 学生需要一点提示
    - **示例**: "让我来帮你想一想。要不要试试用手指或画图的方式数一数？"

    ### 3. break_down (分解型)
    - **适用场景**: 复杂问题，需要分解步骤
    - **示例**: "我们把这个问题分解一下。先看第一步应该做什么？"

    ### 4. visualize (可视化型)
    - **适用场景**: 抽象问题，需要可视化
    - **示例**: "我们可以画个图来理解这个问题。要不要试试？"

    ### 5. check_work (检查型)
    - **适用场景**: 学生的答案接近但不完全正确
    - **示例**: "让我帮你检查一下。你能不能再数一遍，看看是不是正确？"

    ### 6. alternative_method (替代方法型)
    - **适用场景**: 当前方法行不通
    - **示例**: "让我们试试另一种方法。也许换个角度思考这个问题？"

    ### 7. encourage (鼓励型)
    - **适用场景**: 学生需要鼓励和信心
    - **示例**: "你已经很接近了！继续加油，再试一次？"

    ## 错误类型与引导类型的映射

    | 错误类型 | 首次尝试 | 多次尝试 |
    |---------|---------|---------|
    | calculation | hint, check_work | break_down, visualize |
    | concept | clarify, break_down | visualize, alternative_method |
    | understanding | clarify | break_down, hint |
    | careless | check_work, encourage | encourage, check_work |
    """
    guidance_types = [
        GuidanceTypeInfo(
            type="clarify",
            name="澄清型",
            description="通过提问澄清学生的理解，帮助学生理解题意",
            applicable_scenarios=["对题意理解有偏差", "需要确认学生想法"]
        ),
        GuidanceTypeInfo(
            type="hint",
            name="提示型",
            description="给出有针对性的提示，但不直接给出答案",
            applicable_scenarios=["需要一点提示", "初次出错"]
        ),
        GuidanceTypeInfo(
            type="break_down",
            name="分解型",
            description="将复杂问题分解为简单步骤，引导学生逐步解决",
            applicable_scenarios=["复杂问题", "多次尝试仍不正确"]
        ),
        GuidanceTypeInfo(
            type="visualize",
            name="可视化型",
            description="建议学生用画图、实物模拟等可视化方式帮助理解",
            applicable_scenarios=["抽象问题", "空间概念"]
        ),
        GuidanceTypeInfo(
            type="check_work",
            name="检查型",
            description="引导学生检查自己的答案和解题过程",
            applicable_scenarios=["答案接近但不完全正确", "可能的粗心错误"]
        ),
        GuidanceTypeInfo(
            type="alternative_method",
            name="替代方法型",
            description="建议学生尝试不同的解题方法",
            applicable_scenarios=["当前方法行不通", "拓展思路"]
        ),
        GuidanceTypeInfo(
            type="encourage",
            name="鼓励型",
            description="给予学生鼓励，建立信心，同时引导思考",
            applicable_scenarios=["需要鼓励和信心", "多次受挫"]
        ),
    ]

    return GuidanceTypesResponse(
        guidance_types=guidance_types
    )


@router.get("/health")
async def health_check():
    """
    健康检查

    验证引导教学服务是否正常运行
    """
    return {
        "status": "healthy",
        "service": "引导教学服务",
        "features": {
            "guidance_generation": "available",
            "response_validation": "available",
            "error_classification": "available"
        }
    }
