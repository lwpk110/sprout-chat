# 小芽家教 (SproutChat)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.109+-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-18-61dafb.svg" alt="React">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

> 面向一年级学生的 AI-First 个性化家教助手，通过语音拍照交互和引导式教学，帮助学生在快乐中学习成长。

## ✨ 产品特色

- **🗣️ 语音交互**: 自然语音对话，识别儿童语言
- **📷 拍照识别**: 拍摄题目，自动识别内容
- **🎯 引导式教学**: 苏格拉底式提问，不直接给答案
- **📊 学习追踪**: 记录学习轨迹，生成学习报告
- **👨‍👩‍👧 家长模式**: 时间控制、难度调节、内容过滤
- **📚 多科目支持**: 数学、语文、英语、科学

## 🚀 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+ (前端开发)
- Git

### 1. 克隆项目

```bash
git clone https://github.com/lwpk110/sprout-chat.git
cd sprout-chat
```

### 2. 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或: .\venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 API 密钥
```

### 3. 启动后端

```bash
cd backend
uvicorn app.main:app --reload
```

后端服务运行在 `http://localhost:8000`

- API 文档: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 4. 前端设置 (待开发)

```bash
cd frontend
npm install
npm start
```

前端服务运行在 `http://localhost:3000`

## 📁 项目结构

```
sprout-chat/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   ├── conversations.py
│   │   │   ├── images.py
│   │   │   ├── learning.py
│   │   │   └── parental.py
│   │   ├── services/          # 业务逻辑
│   │   │   ├── engine.py      # 对话引擎
│   │   │   ├── vision.py      # 图像识别
│   │   │   ├── teaching_strategy.py  # 教学策略
│   │   │   ├── learning_tracker.py   # 学习追踪
│   │   │   ├── parental_control.py   # 家长控制
│   │   │   └── multi_subject.py      # 多科目
│   │   ├── models/            # 数据模型
│   │   ├── utils/             # 工具函数
│   │   └── main.py            # 应用入口
│   ├── tests/                 # 测试文件
│   ├── requirements.txt       # Python 依赖
│   └── .env.example           # 环境变量模板
├── frontend/                  # React 前端 (待开发)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
├── docs/                      # 文档
│   ├── PRD.md                 # 产品需求文档
│   ├── teacher-spec.md        # 教师人格规范
│   └── database_schema.md     # 数据库设计
├── CLAUDE.md                  # 项目记忆中枢
└── README.md                  # 本文件
```

## 🛠️ 技术栈

### 后端

| 技术 | 用途 |
|------|------|
| Python 3.11+ | 编程语言 |
| FastAPI | Web 框架 |
| Pydantic v2 | 数据验证 |
| SQLAlchemy | ORM (待集成) |
|智谱 GLM-4 | 对话生成 |
| GLM-4.6v | 图像识别 |

### 前端 (待开发)

| 技术 | 用途 |
|------|------|
| React 18 | UI 框架 |
| Tailwind CSS | 样式框架 |
| Axios | HTTP 客户端 |
| React Router | 路由管理 |

## 📚 API 文档

### 对话管理

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/conversations/create` | POST | 创建新会话 |
| `/api/v1/conversations/message` | POST | 发送消息 |
| `/api/v1/conversations/{id}/history` | GET | 获取历史 |

### 图像识别

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/images/upload` | POST | 上传图像 |
| `/api/v1/images/recognize` | POST | 识别内容 |
| `/api/v1/images/guide` | POST | 引导式响应 |

### 学习追踪

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/learning/record` | POST | 创建记录 |
| `/api/v1/learning/progress/{id}` | GET | 获取进度 |
| `/api/v1/learning/report` | POST | 生成报告 |

### 家长控制

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/parental/time-restriction` | POST | 时间限制 |
| `/api/v1/parental/difficulty` | PUT | 难度调节 |
| `/api/v1/parental/content-filter` | POST | 内容过滤 |

**总计**: 31 个 API 端点

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行测试并查看覆盖率
pytest --cov=app --cov-report=html

# 运行特定测试文件
pytest tests/test_engine.py -v
```

### 测试覆盖率

| 模块 | 覆盖率 |
|------|--------|
| engine.py | 68% |
| vision.py | 76% |
| teaching_strategy.py | 73% |
| learning_tracker.py | 87% |
| parental_control.py | 88% |
| multi_subject.py | 89% |
| **平均** | **80%** |

## 📝 开发指南

### 开发方法论

本项目采用 **规范驱动开发 (SDD)** + **TDD** 方法论：

1. 编写规范 → 2. 红灯测试 → 3. 绿灯实现 → 4. 重构优化

详见 [CLAUDE.md](./CLAUDE.md)

### 代码风格

```bash
# 格式化代码
black .
isort .

# 类型检查
mypy app/
```

### Git 提交规范

```
[TYPE](Task-ID): 简要描述

详细说明（可选）
- 完成项 1
- 完成项 2

Refs: Task-ID
```

TYPE 类型: `feat`, `fix`, `docs`, `style`, `refactor`, `test`

### 开发流程

```bash
# 1. 创建分支
git checkout -b feature/xxx

# 2. TDD 循环
# Red: 编写失败测试
pytest  # 确认失败
git commit -m "[LWP-X] test: xxx (Red)"

# Green: 编写功能代码
pytest  # 确认通过
git commit -m "[LWP-X] feat: xxx (Green)"

# Refactor: 重构代码
pytest  # 确认通过
git commit -m "[LWP-X] refactor: xxx (Refactor)"

# 3. 提交 PR
```

## 📖 文档

### 核心文档

| 文档 | 描述 |
|------|------|
| [开发协议](./development/development-guide.md) | TDD 开发流程规范 |
| [项目宪章](./.specify/memory/constitution.md) | 核心价值观和原则 |

### 架构决策 (ADR)

| 文档 | 描述 |
|------|------|
| [ADR-002: Taskmaster 本地模式](./adr/adr-002-taskmaster-local.md) | 采用 Taskmaster 本地模式 |
| [ADR-001: Linear 迁移评估](./adr/adr-001-linear-eval.md) | Linear 迁移可行性分析 |

### 开发指南

| 文档 | 描述 |
|------|------|
| [Taskmaster 最佳实践](./development/taskmaster-best-practices.md) | 任务管理工具使用指南 |
| [Ralph Loop 指南](./RALPH_LOOP_GUIDE.md) | 迭代开发快速开始 |
| [Ralph Loop 配置](./RALPH_LOOP_SETUP.md) | 配置说明和使用流程 |

### 技术文档

| 文档 | 描述 |
|------|------|
| [产品需求文档](./specifications/prd.md) | PRD 产品需求 |
| [教师人格规范](./specifications/teacher-spec.md) | 小芽人格定义 |
| [AI 配置](./technical/ai-config.md) | AI 模型配置 |
| [API 文档](./technical/api.md) | API 接口规范 |
| [数据库设计](./technical/database-schema.md) | 数据表结构 |
| [集成文档](./technical/integrations.md) | 第三方集成 |

### 项目记忆

| 文档 | 描述 |
|------|------|
| [CLAUDE.md](./CLAUDE.md) | 项目记忆中枢 |
| [PROMPT.md](./PROMPT.md) | 当前迭代任务 |

### 完成报告

| 文档 | 描述 |
|------|------|
| [MVP 完成报告](./reports/MVP_DELIVERY.md) | MVP 开发总结 |

## 🎯 路线图

### v1.0 (进行中)
- [x] 后端 API 开发 (MVP)
- [ ] 数据库持久化
- [ ] 用户认证系统
- [ ] 前端基础界面

### v2.0 (计划中)
- [ ] 题库系统
- [ ] 知识点图谱
- [ ] 个性化推荐
- [ ] 学习路径规划

### v3.0 (规划中)
- [ ] 更多年级支持
- [ ] 教师版本
- [ ] 社交功能
- [ ] 第三方集成

## 🤝 贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Claude](https://claude.ai) - AI 开发助手
- [智谱 AI](https://www.zhipuai.com) - GLM 模型支持

---

<p align="center">
  让每个孩子都能拥有一个懂他们、会引导的 AI 小老师
</p>
