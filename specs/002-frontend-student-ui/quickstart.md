# Frontend Quickstart Guide: 小芽家教前端学生界面

**Feature**: 002-frontend-student-ui
**Target Audience**: 前端开发者
**Prerequisites**: Node.js 18+, npm 或 yarn

---

## 概述

本指南帮助您快速搭建小芽家教前端开发环境，了解项目结构，并开始开发。

**技术栈**:
- React 18 + TypeScript
- Vite (构建工具)
- Tailwind CSS (样式)
- Zustand (状态管理)
- Axios (HTTP 客户端)
- Jest + Testing Library (测试)

---

## 1. 环境搭建

### 1.1 安装依赖

```bash
cd frontend
npm install
```

**预期输出**:
```
added 1423 packages, and audited 1424 packages in 45s
...
found 0 vulnerabilities
```

### 1.2 环境变量配置

创建 `.env.development` 文件：

```bash
# 后端 API 地址（开发环境使用代理）
VITE_API_BASE_URL=/api

# 开发服务器端口
VITE_PORT=5173
```

### 1.3 Vite 代理配置

确保 `vite.config.ts` 配置了代理到后端：

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

---

## 2. 本地开发

### 2.1 启动开发服务器

```bash
npm run dev
```

**预期输出**:
```
  VITE v5.0.8  ready in 250 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

浏览器自动打开 `http://localhost:5173/`。

### 2.2 验证后端连接

打开浏览器控制台，应看到：

```
[API] POST /api/v1/conversations/create
{ session_id: "sess_...", student_id: "student_...", ... }
```

### 2.3 热重载测试

修改 `src/App.tsx`，保存文件，浏览器应自动刷新。

---

## 3. 开发工作流

### 3.1 创建新组件

```bash
# 创建组件文件
touch src/components/NewComponent.tsx

# 创建测试文件
touch src/components/__tests__/NewComponent.test.tsx
```

**组件模板** (`NewComponent.tsx`):

```tsx
/**
 * 新组件说明
 */
import React from 'react'

interface NewComponentProps {
  // 定义 Props
  title: string
  onAction?: () => void
}

export default function NewComponent({ title, onAction }: NewComponentProps) {
  return (
    <div className="card-sprout">
      <h2 className="text-sprout-lg">{title}</h2>
      {onAction && (
        <button onClick={onAction} className="btn-sprout">
          点击
        </button>
      )}
    </div>
  )
}
```

**测试模板** (`NewComponent.test.tsx`):

```tsx
import { render, screen } from '@testing-library/react'
import NewComponent from '../NewComponent'

describe('NewComponent', () => {
  it('renders title correctly', () => {
    render(<NewComponent title="测试标题" />)
    expect(screen.getByText('测试标题')).toBeInTheDocument()
  })

  it('calls onAction when button is clicked', () => {
    const mockFn = jest.fn()
    render(<NewComponent title="测试" onAction={mockFn} />)

    const button = screen.getByRole('button')
    button.click()

    expect(mockFn).toHaveBeenCalled()
  })
})
```

### 3.2 添加新页面

```tsx
// src/pages/NewPage.tsx
export default function NewPage() {
  return (
    <div className="min-h-screen p-4">
      <h1>新页面</h1>
    </div>
  )
}
```

添加路由 (`src/App.tsx`):

```tsx
import NewPage from './pages/NewPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<StudentHome />} />
      <Route path="/new-page" element={<NewPage />} />
    </Routes>
  )
}
```

### 3.3 对接新 API

**步骤 1**: 添加类型定义 (`src/types/index.ts`)

```typescript
export interface NewAPIRequest {
  param1: string
  param2: number
}

export interface NewAPIResponse {
  result: string
  timestamp: string
}
```

**步骤 2**: 添加 API 方法 (`src/services/api.ts`)

```typescript
class ApiClient {
  // ... 其他方法

  async newAPI(request: NewAPIRequest): Promise<NewAPIResponse> {
    const response = await this.client.post<NewAPIResponse>(
      '/v1/new-endpoint',
      request
    )
    return response.data
  }
}
```

**步骤 3**: 在组件中使用

```tsx
import { apiClient } from '../services/api'

const MyComponent = () => {
  const [data, setData] = useState<NewAPIResponse | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await apiClient.newAPI({ param1: 'test', param2: 123 })
        setData(result)
      } catch (error) {
        console.error('API 调用失败:', error)
      }
    }
    fetchData()
  }, [])

  return <div>{data?.result}</div>
}
```

---

## 4. 测试

### 4.1 运行单元测试

```bash
# 运行所有测试
npm test

# 监听模式
npm run test:watch

# 生成覆盖率报告
npm run test:coverage
```

**预期输出**:

```
Test Suites: 12 passed, 12 total
Tests:       35 passed, 35 total
Snapshots:   0 total
Time:        5.234 s
Coverage:    82.45%
```

### 4.2 测试覆盖率要求

- **单元测试覆盖率**: ≥ 80%
- **关键组件**: 100% (VoiceInteraction, PhotoInteraction, API 服务)

### 4.3 手动测试清单

- [ ] 语音录制和识别
- [ ] 文字输入和发送
- [ ] 拍照上传和 OCR
- [ ] 错误处理和用户提示
- [ ] 页面刷新后恢复会话
- [ ] 离线缓存和同步

---

## 5. 代码规范

### 5.1 TypeScript

```typescript
// ✅ 正确: 使用接口定义 Props
interface MyComponentProps {
  title: string
  count?: number  // 可选属性
}

// ❌ 错误: 使用 any
function MyComponent(props: any) { ... }
```

### 5.2 命名规范

| 类型 | 命名规则 | 示例 |
|------|---------|------|
| 组件 | PascalCase | `VoiceInteraction.tsx` |
| 函数 | camelCase | `useVoiceRecognition` |
| 常量 | UPPER_SNAKE_CASE | `MAX_MESSAGES` |
| 类型 | PascalCase | `Message`, `SessionState` |
| 接口 | PascalCase + I 前缀 (可选) | `MessageProps` |

### 5.3 样式规范

```tsx
// ✅ 推荐: 使用 Tailwind 类名
<div className="btn-sprout btn-sprout-primary">
  点击
</div>

// ❌ 避免: 内联样式
<div style={{ padding: '1rem', color: 'red' }}>
  点击
</div>
```

### 5.4 错误处理

```tsx
// ✅ 正确: 捕获并处理错误
const fetchData = async () => {
  try {
    const data = await apiClient.createSession({ ... })
    setData(data)
  } catch (error) {
    console.error('创建会话失败:', error)
    setError('哎呀，小芽遇到了一点问题，请刷新页面试试')
  }
}

// ❌ 错误: 忽略错误
const fetchData = async () => {
  const data = await apiClient.createSession({ ... })  // 可能抛出异常
  setData(data)
}
```

---

## 6. 调试

### 6.1 Chrome DevTools

打开浏览器控制台（F12），查看：

- **Console**: 日志输出
- **Network**: API 请求和响应
- **Application**: localStorage 数据

### 6.2 React Developer Tools

安装扩展：[React Developer Tools](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi)

查看组件树和 Zustand store 状态。

### 6.3 Vite 日志

```bash
# 查看详细构建日志
npm run dev -- --debug
```

---

## 7. 构建与部署

### 7.1 构建生产版本

```bash
npm run build
```

**输出目录**: `frontend/dist/`

**预期输出**:

```
vite v5.0.8 building for production...
✓ 1234 modules transformed.
dist/index.html                  1.23 kB
dist/assets/index-abc123.css     45.67 kB
dist/assets/index-def456.js      234.56 kB
```

### 7.2 预览构建结果

```bash
npm run preview
```

访问 `http://localhost:4173/` 查看生产版本。

### 7.3 性能优化检查

```bash
# 分析构建包大小
npm run build -- --mode analyze
```

**目标**:
- 首屏加载时间: ≤ 2 秒
- 总包大小: ≤ 500KB (gzipped)

---

## 8. 常见问题

### Q1: Vite 代理不工作？

**A**: 检查 `vite.config.ts` 的 proxy 配置，确保 `changeOrigin: true`。

### Q2: TypeScript 类型错误？

**A**: 运行 `npm run build` 查看完整错误信息，或安装 VSCode 插件 "TypeScript Importer"。

### Q3: Jest 测试失败？

**A**: 确保 `jest.config.cjs` 配置正确，清除缓存 `npm test -- --clearCache`。

### Q4: Tailwind 样式不生效？

**A**: 检查 `tailwind.config.js` 的 content 配置是否包含所有文件路径。

---

## 9. 下一步

- 📖 阅读 [data-model.md](./data-model.md) 了解数据模型
- 🔌 查看 [contracts/](./contracts/) 了解 API 契约
- 🚀 开始实现 [tasks.md](./tasks.md) 中的任务

---

**Happy Coding! 🌱**
