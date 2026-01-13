"""
图像识别 API 端点

提供图片上传和识别功能
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import io
from base64 import b64encode
from PIL import Image

from app.services.vision import VisionService
from app.core.config import settings


router = APIRouter(prefix="/api/v1/images", tags=["图像识别"])

# 初始化视觉服务
vision_service = VisionService()


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    student_age: int = Form(6)
):
    """
    上传图片并识别

    Args:
        file: 图片文件
        student_age: 学生年龄

    Returns:
        识别结果
    """
    # 验证文件类型（移到 try 块外，避免被外层捕获）
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="只支持图片文件 (jpg, png, etc.)"
        )

    try:
        # 读取图片内容
        image_bytes = await file.read()

        # 转换为 base64
        base64_image = b64encode(image_bytes).decode('utf-8')

        # 识别图片内容
        recognized_text = await vision_service.call_vision_api(
            base64_image,
            prompt="请识别这张图片中的数学题目或作业内容"
        )

        return JSONResponse({
            "success": True,
            "data": {
                "recognized_text": recognized_text,
                "image_size": len(image_bytes),
                "content_type": file.content_type
            }
        })

    except HTTPException:
        # HTTPException 直接向上传播
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"图片识别失败: {str(e)}"
        )


@router.post("/recognize")
async def recognize_image(
    file: UploadFile = File(...),
    prompt: str = Form("请识别这张图片中的数学题目")
):
    """
    识别图片内容

    Args:
        file: 图片文件
        prompt: 识别提示词

    Returns:
        识别的文本内容
    """
    # 验证文件类型（移到 try 块外）
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="只支持图片文件"
        )

    try:
        # 读取并编码图片
        image_bytes = await file.read()
        base64_image = b64encode(image_bytes).decode('utf-8')

        # 调用识别 API
        result = await vision_service.call_vision_api(base64_image, prompt)

        return JSONResponse({
            "success": True,
            "result": result
        })

    except HTTPException:
        # HTTPException 直接向上传播
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"识别失败: {str(e)}"
        )


@router.post("/guide")
async def guide_from_image(
    file: UploadFile = File(...),
    student_id: str = Form(...),
    student_age: int = Form(6),
    subject: str = Form("数学")
):
    """
    上传图片并获得引导式教学响应

    这是最常用的端点：学生拍照后直接获得小芽老师的引导式讲解

    Args:
        file: 图片文件（作业题）
        student_id: 学生 ID
        student_age: 学生年龄
        subject: 科目

    Returns:
        引导式教学响应
    """
    # 验证文件类型（移到 try 块外）
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="只支持图片文件"
        )

    try:
        # 读取并编码图片
        image_bytes = await file.read()
        base64_image = b64encode(image_bytes).decode('utf-8')

        # 识别图片并生成引导式响应
        response = await vision_service.call_vision_api(
            base64_image,
            prompt=f"""你是小芽老师，一位面向 {student_age} 岁学生的温柔家教。

请识别这张图片中的{subject}题目，然后用引导式的方式讲解。

**重要要求**：
1. 绝对不要直接给答案
2. 使用具象比喻（糖果、苹果、小兔子等）
3. 用提问引导学生思考
4. 语气温柔耐心
5. 给予鼓励

请开始你的讲解："""
        )

        return JSONResponse({
            "success": True,
            "data": {
                "student_id": student_id,
                "subject": subject,
                "response": response,
                "image_size": len(image_bytes)
            }
        })

    except HTTPException:
        # HTTPException 直接向上传播
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成引导式响应失败: {str(e)}"
        )


@router.post("/extract-problem")
async def extract_math_problem(file: UploadFile = File(...)):
    """
    从图片中提取数学问题

    Args:
        file: 图片文件

    Returns:
        提取的数学问题
    """
    # 验证文件类型（移到 try 块外）
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="只支持图片文件"
        )

    try:
        # 读取并编码图片
        image_bytes = await file.read()
        base64_image = b64encode(image_bytes).decode('utf-8')

        # 提取数学问题
        problem = await vision_service.call_vision_api(
            base64_image,
            prompt="请提取这张图片中的数学问题，只返回问题本身，不要解释。"
        )

        return JSONResponse({
            "success": True,
            "problem": problem.strip()
        })

    except HTTPException:
        # HTTPException 直接向上传播
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"提取问题失败: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """健康检查"""
    return JSONResponse({
        "status": "healthy",
        "service": "图像识别服务",
        "vision_model": settings.ai_vision_model
    })
