# 前端开发指南

## 快速开始

### 方法一：使用启动脚本（推荐）

```bash
# 在项目根目录
./start-all.sh
```

这将自动启动前后端服务。

### 方法二：手动启动

```bash
# 终端 1：启动后端
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# 终端 2：启动前端
cd frontend
npm run dev
```

## 开发工作流

### 1. 创建新组件

```bash
# 在 src/components/ 创建新组件
touch src/components/MyComponent.tsx
```

组件模板：

```tsx
import { useState } from 'react'

interface MyComponentProps {
  title: string
  onClick?: () => void
}

export default function MyComponent({ title, onClick }: MyComponentProps) {
  const [isActive, setIsActive] = useState(false)

  return (
    <div className="card-sprout">
      <h2>{title}</h2>
      <button onClick={() => setIsActive(!isActive)}>
        {isActive ? '激活' : '未激活'}
      </button>
    </div>
  )
}
```

### 2. 添加 API 端点

在 `src/services/api.ts` 中添加新方法：

```typescript
async myNewMethod(param: string) {
  const response = await this.client.get(`/v1/endpoint/${param}`)
  return response.data
}
```

### 3. 更新状态管理

在 `src/store/sessionStore.ts` 中添加新状态：

```typescript
interface SessionState {
  // ... 现有状态
  myNewState: string
  setMyNewState: (value: string) => void
}

export const useSessionStore = create<SessionState>((set) => ({
  // ... 现有实现
  myNewState: '',
  setMyNewState: (value) => set({ myNewState: value }),
}))
```

## 调试技巧

### 查看网络请求

打开浏览器开发者工具 → Network 标签页，查看所有 API 请求。

### 查看状态变化

在组件中添加 console.log：

```tsx
const { sessionId, messages } = useSessionStore()
useEffect(() => {
  console.log('状态更新:', { sessionId, messages })
}, [sessionId, messages])
```

### React DevTools

安装 [React DevTools](https://react.dev/learn/react-developer-tools) 浏览器扩展，查看组件树和 props。

## 常见问题

### Q: 样式不生效？

A: 检查：
1. Tailwind 类名是否正确
2. 是否在 `tailwind.config.js` 中配置了内容路径
3. 浏览器缓存（强制刷新：Ctrl+Shift+R）

### Q: API 调用失败？

A: 检查：
1. 后端是否运行在 `http://localhost:8000`
2. 浏览器控制台的错误信息
3. `vite.config.ts` 中的代理配置

### Q: 语音识别不工作？

A: 检查：
1. 浏览器是否支持 Web Speech API（Chrome/Safari/Edge）
2. 是否授予了麦克风权限
3. 是否在 HTTPS 环境（localhost 可以）

## 性能优化

### 1. 代码分割

使用 `React.lazy()` 懒加载组件：

```tsx
const HeavyComponent = React.lazy(() => import('./HeavyComponent'))

function App() {
  return (
    <Suspense fallback={<div>加载中...</div>}>
      <HeavyComponent />
    </Suspense>
  )
}
```

### 2. 图片优化

使用适当的图片格式和尺寸：

```tsx
// 使用 WebP 格式
<img src="/image.webp" alt="描述" />

// 添加 loading 属性
<img src="/image.jpg" loading="lazy" alt="描述" />
```

### 3. 防抖和节流

对于频繁触发的事件（如输入），使用防抖：

```tsx
import { debounce } from 'lodash'

const handleChange = debounce((value: string) => {
  // API 调用
}, 300)
```

## 测试

### 单元测试

```tsx
// MyComponent.test.tsx
import { render, screen } from '@testing-library/react'
import MyComponent from './MyComponent'

test('renders title', () => {
  render(<MyComponent title="测试" />)
  expect(screen.getByText('测试')).toBeInTheDocument()
})
```

### 运行测试

```bash
npm test                 # 运行所有测试
npm run test:watch       # 监听模式
npm run test:coverage    # 覆盖率报告
```

## 部署

### 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录。

### 预览生产构建

```bash
npm run preview
```

### 环境变量

生产环境需要设置 `VITE_API_BASE_URL`：

```bash
# .env.production
VITE_API_BASE_URL=https://api.sprout-chat.com
```

## 代码规范

### TypeScript

- 始终使用类型定义
- 避免使用 `any` 类型
- 使用接口定义 Props

### React

- 使用函数组件 + Hooks
- 遵循单一职责原则
- 添加清晰的注释

### 命名规范

- 组件: PascalCase（如 `MyComponent`）
- 函数/变量: camelCase（如 `handleSubmit`）
- 常量: UPPER_SNAKE_CASE（如 `API_BASE_URL`）
- 文件名: PascalCase（如 `MyComponent.tsx`）

## 相关资源

- [React 文档](https://react.dev/)
- [TypeScript 文档](https://www.typescriptlang.org/docs/)
- [Tailwind CSS 文档](https://tailwindcss.com/docs)
- [Vite 文档](https://vitejs.dev/)
- [Zustand 文档](https://zustand-demo.pmnd.rs/)
