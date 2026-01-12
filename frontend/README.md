# 小芽家教前端

## 概述

这是小芽家教项目的 React 前端应用，为一年级学生提供简洁友好的 AI 学习界面。

## 技术栈

- **框架**: React 18 + TypeScript
- **构建工具**: Vite 5
- **样式**: Tailwind CSS 3.4
- **状态管理**: Zustand
- **路由**: React Router 6
- **HTTP 客户端**: Axios
- **语音识别**: Web Speech API

## 功能特性

### 核心功能
- ✅ 语音对话交互（使用 Web Speech API）
- ✅ 拍照上传作业
- ✅ 引导式教学响应显示
- ✅ 会话管理
- ✅ 对话历史记录

### 设计特点
- 🎨 小芽绿色主题 (#8BC34A)
- 👶 适合一年级学生的大按钮设计
- 📱 响应式布局（支持平板和手机）
- ♿ 容错性设计（误操作可恢复）
- ⚡ 快速响应（交互反馈及时）

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 配置环境变量

```bash
cp .env.example .env.local
```

开发环境使用 Vite 代理，通常不需要修改 `.env.local`。

### 3. 启动开发服务器

```bash
npm run dev
```

前端将运行在 `http://localhost:3000`

### 4. 启动后端服务

确保后端服务运行在 `http://localhost:8000`

```bash
# 在另一个终端窗口
cd ../backend
uvicorn app.main:app --reload
```

## 项目结构

```
frontend/
├── public/              # 静态资源
├── src/
│   ├── components/      # React 组件
│   │   ├── VoiceInteraction.tsx    # 语音交互
│   │   ├── PhotoInteraction.tsx    # 拍照交互
│   │   └── GuidedResponse.tsx      # 引导响应
│   ├── pages/           # 页面组件
│   │   └── StudentHome.tsx         # 学生主页
│   ├── services/        # API 服务
│   │   └── api.ts                 # API 客户端
│   ├── store/           # 状态管理
│   │   └── sessionStore.ts         # 会话状态
│   ├── types/           # TypeScript 类型
│   │   └── index.ts               # 类型定义
│   ├── hooks/           # 自定义 Hooks
│   ├── context/         # React Context
│   ├── utils/           # 工具函数
│   ├── App.tsx          # 根组件
│   ├── main.tsx         # 入口文件
│   └── index.css        # 全局样式
├── index.html           # HTML 模板
├── package.json         # 依赖配置
├── tsconfig.json        # TypeScript 配置
├── vite.config.ts       # Vite 配置
├── tailwind.config.js   # Tailwind 配置
└── README.md            # 本文档
```

## 可用脚本

```bash
# 开发
npm run dev              # 启动开发服务器

# 构建
npm run build            # 构建生产版本
npm run preview          # 预览生产构建

# 测试
npm run test             # 运行测试
npm run test:watch       # 监听模式
npm run test:coverage    # 测试覆盖率

# 代码质量
npm run lint             # ESLint 检查
```

## 核心组件说明

### 1. StudentHome（学生主页）

主界面，包含：
- 会话管理
- 语音和拍照交互入口
- 对话历史展示
- 欢迎信息

### 2. VoiceInteraction（语音交互）

**功能**：
- Web Speech API 集成
- 实时语音识别
- 语音转文字发送

**状态**：
- `isListening`: 是否正在录音
- `transcript`: 识别的文字

### 3. PhotoInteraction（拍照交互）

**功能**：
- 拍照或上传图片
- 图片预览
- 发送到后端 OCR

**验证**：
- 文件类型检查（仅图片）
- 文件大小限制（最大 10MB）

### 4. GuidedResponse（引导响应）

**功能**：
- 突出显示 AI 引导问题
- 语音播报（可选）
- 教学理念标签展示

**设计**：
- 大字体，适合阅读
- 引导式教学标签
- 鼓励和思考提示

## API 集成

### 后端端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/conversations/create` | POST | 创建会话 |
| `/api/v1/conversations/voice` | POST | 语音输入 |
| `/api/v1/conversations/message` | POST | 文字输入 |
| `/api/v1/conversations/{id}/history` | GET | 获取历史 |
| `/api/v1/conversations/{id}/stats` | GET | 会话统计 |

### API 客户端

```typescript
import { apiClient } from '@/services/api'

// 创建会话
const session = await apiClient.createSession({
  student_id: 'student_123',
  subject: '数学',
  student_age: 6,
})

// 发送语音
const response = await apiClient.sendVoiceInput({
  session_id: sessionId,
  transcript: '1 + 1 等于几？',
})
```

## 状态管理

使用 Zustand 管理会话状态：

```typescript
import { useSessionStore } from '@/store/sessionStore'

function MyComponent() {
  const { sessionId, messages, addMessage } = useSessionStore()

  return (
    <div>
      <div>会话 ID: {sessionId}</div>
      <div>消息数: {messages.length}</div>
    </div>
  )
}
```

## 样式指南

### 小芽主题色

- **主色**: #8BC34A (sprout-500)
- **浅色**: #f6fdf6 (sprout-50)
- **深色**: #29562a (sprout-800)

### 组件样式类

```tsx
// 大按钮（适合一年级学生）
<button className="btn-sprout btn-sprout-primary">
  点击我
</button>

// 卡片
<div className="card-sprout">
  内容
</div>

// 引导文字
<p className="text-guided">
  引导问题内容
</p>
```

## 浏览器兼容性

| 功能 | Chrome | Safari | Firefox | Edge |
|------|--------|--------|---------|------|
| 语音识别 | ✅ | ✅ | ❌ | ✅ |
| 语音播报 | ✅ | ✅ | ✅ | ✅ |
| 拍照上传 | ✅ | ✅ | ✅ | ✅ |

**注意**: Web Speech API 在 Firefox 中不支持语音识别，但支持语音播报。

## 开发规范

### 组件开发
1. 使用 TypeScript 定义 Props 类型
2. 使用函数组件 + Hooks
3. 遵循单一职责原则
4. 添加清晰的注释

### 提交规范
```bash
git commit -m "[LWP-X] feat: 添加语音识别功能
- 实现 Web Speech API 集成
- 添加实时识别显示
- 处理错误状态

Refs: LWP-X"
```

## 测试

```bash
# 运行所有测试
npm test

# 监听模式
npm run test:watch

# 覆盖率报告
npm run test:coverage
```

## 故障排查

### 问题：后端 API 调用失败

**检查**：
1. 后端是否运行在 `http://localhost:8000`
2. Vite 代理配置是否正确
3. 浏览器控制台是否有 CORS 错误

### 问题：语音识别不工作

**检查**：
1. 是否使用了支持的浏览器（Chrome/Safari/Edge）
2. 是否授予了麦克风权限
3. 是否在 HTTPS 环境（开发时 localhost 可以）

### 问题：样式不生效

**检查**：
1. Tailwind CSS 配置是否正确
2. `index.css` 是否导入
3. PostCSS 配置是否正确

## 未来改进

- [ ] 添加单元测试（Jest + React Testing Library）
- [ ] 添加 E2E 测试（Playwright）
- [ ] 实现离线缓存（Service Worker）
- [ ] 添加家长端管理界面
- [ ] 实现学习进度可视化
- [ ] 添加更多交互动画

## 相关文档

- [项目主文档](../README.md)
- [后端文档](../backend/README.md)
- [项目宪章](../.specify/memory/constitution.md)

## 许可证

MIT
