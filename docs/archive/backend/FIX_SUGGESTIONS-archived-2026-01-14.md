# OCR 图片上传功能 - 问题修复建议

本文档提供测试中发现问题的详细修复方案，供 Dev 参考。

---

## 问题 1: 非 400 状态码问题（P1）

### 问题描述
上传非图片文件时，API 返回 500 错误而非 400 错误

### 测试用例
```python
# tests/test_image_upload_api.py::TestErrorHandling::test_upload_non_image_file
def test_upload_non_image_file(self):
    text_file = BytesIO(b"This is not an image")

    response = client.post(
        "/api/v1/images/upload",
        files={"file": ("test.txt", text_file, "text/plain")},
        data={"student_age": 6}
    )

    # 期望: 400
    # 实际: 500
    assert response.status_code == 400
```

### 当前代码（有问题）
```python
# backend/app/api/images.py
@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    student_age: int = Form(6)
):
    try:
        # 验证文件类型
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="只支持图片文件 (jpg, png, etc.)"
            )

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

    except Exception as e:
        # 问题：这里捕获了所有异常，包括 HTTPException
        raise HTTPException(
            status_code=500,
            detail=f"图片识别失败: {str(e)}"
        )
```

### 问题分析
1. 代码在 try 块中抛出 `HTTPException(status_code=400, ...)`
2. 外层 `except Exception as e` 捕获了这个异常
3. 然后重新抛出 `HTTPException(status_code=500, ...)`
4. 结果：400 错误被转换为 500 错误

### 修复方案 1：将验证移到 try 块外（推荐）

```python
@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    student_age: int = Form(6)
):
    # 验证文件类型（移到 try 块外）
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
        # 如果是 HTTPException，直接向上传播
        raise
    except Exception as e:
        # 其他异常转换为 500 错误
        raise HTTPException(
            status_code=500,
            detail=f"图片识别失败: {str(e)}"
        )
```

### 修复方案 2：使用自定义异常类

```python
# 定义自定义异常
class ImageValidationError(Exception):
    """图片验证错误"""
    pass

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    student_age: int = Form(6)
):
    try:
        # 验证文件类型
        if not file.content_type.startswith("image/"):
            raise ImageValidationError("只支持图片文件 (jpg, png, etc.)")

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

    except ImageValidationError as e:
        # 验证错误返回 400
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 其他错误返回 500
        raise HTTPException(
            status_code=500,
            detail=f"图片识别失败: {str(e)}"
        )
```

### 修复方案 3：精确捕获 HTTPException（最简单）

```python
@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    student_age: int = Form(6)
):
    try:
        # 验证文件类型
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="只支持图片文件 (jpg, png, etc.)"
            )

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
        # HTTPException 直接向上传播，不包装
        raise
    except Exception as e:
        # 其他异常包装为 500 错误
        raise HTTPException(
            status_code=500,
            detail=f"图片识别失败: {str(e)}"
        )
```

### 需要修改的所有端点

同一个问题影响以下所有端点，都需要修复：

1. `/api/v1/images/upload` (line 24-72)
2. `/api/v1/images/recognize` (line 75-114)
3. `/api/v1/images/guide` (line 117-181)
4. `/api/v1/images/extract-problem` (line 184-222)

### 批量修复示例

```python
# 创建通用验证函数
def validate_image_file(file: UploadFile):
    """验证图片文件"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="只支持图片文件 (jpg, png, etc.)"
        )

# 在每个端点使用
@router.post("/upload")
async def upload_image(file: UploadFile = File(...), student_age: int = Form(6)):
    # 验证
    validate_image_file(file)

    try:
        # ... 业务逻辑
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片识别失败: {str(e)}")
```

---

## 问题 2: API 余额不足（P0）

### 问题描述
智谱 GLM-4.6v API 返回错误："余额不足或无可用资源包,请充值。"

### 错误信息
```json
{
  "error": {
    "code": "1113",
    "message": "余额不足或无可用资源包,请充值。"
  }
}
```

### 解决方案

#### 方案 1: 充值 API 余额
联系智谱 AI 官网充值：https://open.bigmodel.cn/

#### 方案 2: 配置 Mock OCR 服务（用于测试）

创建 Mock 服务：
```python
# app/services/vision_mock.py
class VisionServiceMock:
    """Mock Vision Service for testing"""

    async def call_vision_api(self, image_data: str, prompt: str) -> str:
        """Mock OCR 识别"""
        # 基于图片数据或 prompt 返回模拟结果
        if "5" in prompt or "5" in image_data[:50]:
            return "这是一道数学题：5 + 3 = ?"
        elif "10" in prompt:
            return "这是一道数学题：10 - 4 = ?"
        else:
            return "这是一道数学题"

# 在测试中使用
@pytest.fixture
def mock_vision_service():
    return VisionServiceMock()
```

#### 方案 3: 使用本地 OCR 模型

使用 PaddleOCR：
```python
# 安装：pip install paddleocr paddlepaddle
from paddleocr import PaddleOCR

class LocalVisionService:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ch')

    async def call_vision_api(self, image_data: str, prompt: str) -> str:
        """本地 OCR 识别"""
        import base64
        from io import BytesIO

        # 解码 base64
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))

        # OCR 识别
        result = self.ocr.ocr(np.array(image))

        # 提取文本
        texts = []
        for line in result[0]:
            texts.append(line[1][0])

        return "\n".join(texts)
```

---

## 测试验证

### 运行测试
```bash
# 运行所有图片上传测试
pytest tests/test_image_upload_api.py -v

# 运行特定测试
pytest tests/test_image_upload_api.py::TestErrorHandling::test_upload_non_image_file -v

# 运行测试并查看覆盖率
pytest tests/test_image_upload_api.py --cov=app/api/images --cov-report=html
```

### 预期结果
修复后，所有测试应该通过：
```bash
================================ test session starts ====================
platform linux -- Python 3.12.4, pytest-9.0.2
collected: 28 items

tests/test_vision.py::TestVisionServiceInit::test_service_creation PASSED
tests/test_vision.py::TestImageRecognition::test_recognize_simple_addition PASSED
...
tests/test_image_upload_api.py::TestErrorHandling::test_upload_non_image_file PASSED
...

========================= 28 passed in 15.23s =========================
```

---

## 其他改进建议

### 1. 添加请求大小限制
```python
from fastapi import Form

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # 验证文件大小
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"文件过大，最大支持 {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # 继续处理...
```

### 2. 添加文件格式验证
```python
ALLOWED_FORMATS = {"image/jpeg", "image/png", "image/jpg"}

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # 验证文件格式
    if file.content_type not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式，请使用: {', '.join(ALLOWED_FORMATS)}"
        )

    # 继续处理...
```

### 3. 统一错误响应格式
```python
from typing import Optional

class ErrorResponse(BaseModel):
    """统一错误响应"""
    error_code: str
    message: str
    details: Optional[dict] = None

# 使用
@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        # ... 处理逻辑
    except ImageValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "INVALID_FILE_TYPE",
                "message": str(e),
                "details": {"allowed_types": ["jpg", "png"]}
            }
        )
```

---

## 总结

### 优先级
1. **P0**: API 余额问题（外部依赖）
2. **P1**: 修复非 400 状态码问题（代码缺陷）

### 预计工作量
- P1 修复：30 分钟 - 1 小时
- P0 解决：取决于方案选择（充值/Mock/本地 OCR）

### 下一步
1. 修复 P1 问题
2. 解决 P0 问题
3. 运行完整测试套件
4. 验证所有测试通过

---

**文档版本**: v1.0
**创建时间**: 2026-01-13
**创建者**: QA Agent
