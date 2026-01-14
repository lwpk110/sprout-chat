# Data Model: 小芽家教前端学生界面

**Feature**: 002-frontend-student-ui
**Date**: 2025-01-13
**Phase**: Phase 1.1 - Data Model Design

## 概述

本文档定义前端应用的数据模型，包括 Zustand 状态管理、localStorage 持久化、以及与后端 API 的对接实体。

**设计原则**:
- 单一数据源 (Single Source of Truth)
- 不可变更新 (Immutable Updates)
- 类型安全 (TypeScript)
- 性能优化 (按需渲染)

---

## 核心实体定义

### 1. Message (对话消息)

表示学生与 AI 之间的单次交互。

```typescript
interface Message {
  // 实体标识
  id: string                    // 唯一 ID (UUID)
  timestamp: string             // ISO 8601 时间戳

  // 内容
  role: 'user' | 'assistant' | 'system'
  content: string               // 消息文本内容

  // 交互类型
  input_type?: 'voice' | 'text' | 'image'  // 用户输入类型
  image_url?: string            // 如果是图片输入，存储图片 URL

  // AI 响应分类 (仅 assistant)
  response_type?: 'guidance' | 'encouragement' | 'error' | 'question'

  // 状态
  is_correct?: boolean          // 学生是否回答正确
  is_loading?: boolean          // 是否正在加载

  // 元数据
  confidence?: number           // 语音识别置信度 (0-1)
  error?: string                // 错误信息
}
```

**验证规则**:
- `id`: 必填，格式 UUID v4
- `timestamp`: 必填，有效 ISO 8601 格式
- `content`: 必填，非空字符串，长度 ≤ 2000 字符
- `role`: 必填，枚举值
- `input_type`: 可选，role='user' 时必填
- `response_type`: 可选，role='assistant' 时必填

**状态转换**:
```
pending (用户输入中)
   ↓
sending (发送中)
   ↓
processing (AI 处理中)
   ↓
completed (完成) 或 failed (失败)
```

---

### 2. SessionState (会话状态)

Zustand store 的状态定义，管理当前学习会话。

```typescript
interface SessionState {
  // === 状态 ===
  sessionId: string | null              // 当前会话 ID
  studentId: string                     // 学生 ID
  subject: string                       // 科目 (数学、语文等)
  studentAge: number                    // 学生年龄
  messages: Message[]                   // 对话历史
  isLoading: boolean                    // 全局加载状态
  error: string | null                  // 全局错误信息

  // === 学习进度 ===
  correctCount: number                  // 连续答对次数
  totalTurns: number                    // 总对话轮次
  sessionDuration: number               // 会话时长 (秒)
  lastActivity: string                  // 最后活动时间

  // === 成就系统 ===
  unlockedAchievements: Achievement[]   // 已解锁成就
  currentStreak: number                 // 当前连续学习天数

  // === Actions ===
  // 会话管理
  setSession: (session: SessionResponse) => void
  clearSession: () => void

  // 消息管理
  addMessage: (message: Message) => void
  updateMessage: (id: string, updates: Partial<Message>) => void
  clearMessages: () => void

  // 加载与错误
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void

  // 学习进度
  incrementCorrectCount: () => void
  resetCorrectCount: () => void
  incrementTotalTurns: () => void
  updateDuration: () => void

  // 成就系统
  unlockAchievement: (achievement: Achievement) => void
  hasAchievement: (achievementId: string) => boolean
}
```

**持久化策略**:
- `sessionId`, `studentId`, `messages`: 持久化到 localStorage
- `isLoading`, `error`: 仅内存，不持久化
- `unlockedAchievements`: 持久化到 localStorage

**更新策略** (遵循 Zustand 最佳实践):
```typescript
// ✅ 正确: 不可变更新
addMessage: (message) => {
  set((state) => ({
    messages: [...state.messages, message]
  }))
}

// ❌ 错误: 可变更新
addMessage: (message) => {
  get().messages.push(message)  // 禁止！
}
```

---

### 3. LearningProgress (学习进度)

表示学生的学习进度和掌握情况。

```typescript
interface LearningProgress {
  // 实体标识
  student_id: string
  subject: string

  // 掌握情况
  total_knowledge_points: number       // 总知识点数量
  mastered_knowledge_points: number    // 已掌握知识点数量
  mastery_rate: number                 // 掌握率 (0-1)

  // 学习统计
  total_sessions: number               // 总学习会话数
  total_questions: number              // 总问题数
  correct_questions: number            // 正确问题数
  accuracy_rate: number                // 正确率 (0-1)

  // 时间统计
  total_study_time: number             // 总学习时长 (秒)
  average_session_time: number         // 平均会话时长 (秒)
  current_streak: number               // 当前连续学习天数
  longest_streak: number               // 最长连续学习天数

  // 最近活动
  last_session_date: string            // 最后学习日期
  last_session_id: string              // 最后会话 ID

  // 元数据
  updated_at: string                   // 更新时间
}
```

**计算字段**:
- `mastery_rate = mastered_knowledge_points / total_knowledge_points`
- `accuracy_rate = correct_questions / total_questions`
- `average_session_time = total_study_time / total_sessions`

**验证规则**:
- 所有 `rate` 字段: 0 ≤ value ≤ 1
- 所有 `count` 字段: value ≥ 0
- `current_streak` ≤ `longest_streak`

---

### 4. Achievement (成就徽章)

表示学生解锁的成就。

```typescript
interface Achievement {
  // 实体标识
  id: string                   // 成就 ID (唯一)
  name: string                 // 成就名称
  description: string          // 成就描述
  icon: string                 // 图标 (Emoji 或 URL)

  // 解锁条件
  unlock_condition: {
    type: 'correct_streak' | 'total_sessions' | 'mastery_rate' | 'custom'
    target: number             // 目标值
  }

  // 状态
  unlocked_at?: string         // 解锁时间 (未解锁为 undefined)
  is_unlocked: boolean         // 是否已解锁

  // 显示
  rarity: 'common' | 'rare' | 'epic' | 'legendary'
  category: 'learning' | 'streak' | 'mastery' | 'special'
}
```

**预定义成就**:

| ID | 名称 | 描述 | 解锁条件 | 稀有度 |
|----|------|------|---------|--------|
| first_step | 初出茅庐 | 完成第一个问题 | 正确回答 1 题 | Common |
| streak_3 | 连胜3题 | 连续答对 3 题 | correct_streak = 3 | Common |
| streak_5 | 连胜5题 | 连续答对 5 题 | correct_streak = 5 | Rare |
| streak_10 | 连胜10题 | 连续答对 10 题 | correct_streak = 10 | Epic |
| scholar | 学者 | 完成 50 个问题 | total_questions = 50 | Rare |
| master | 大师 | 掌握率 90% | mastery_rate = 0.9 | Epic |
| legend | 传奇 | 连续学习 7 天 | current_streak = 7 | Legendary |

**验证规则**:
- `id`: 必填，唯一标识
- `rarity`: 必填，枚举值
- `unlock_condition.target`: 必填，> 0
- `unlocked_at`: 已解锁时必填

---

### 5. Mistake (错题记录)

记录学生的错误题目和订正状态。

```typescript
interface Mistake {
  // 实体标识
  id: string                   // 错题 ID
  session_id: string           // 所属会话
  timestamp: string            // 错误时间

  // 题目信息
  question_type: 'voice' | 'image' | 'text'
  question_content: string     // 题目内容
  image_url?: string           // 题目图片 (如果是图片题)

  // 错误分析
  wrong_answer: string         // 学生的错误答案
  correct_answer: string       // 正确答案
  error_reason: string         // 错误原因 (AI 分析)
  hint: string                 // 引导提示

  // 订正状态
  is_corrected: boolean        // 是否已订正
  corrected_at?: string        // 订正时间
  correction_attempts: number  // 订正尝试次数

  // 知识点
  knowledge_point: string      // 所属知识点
  difficulty: 'easy' | 'medium' | 'hard'

  // 元数据
  reviewed: boolean            // 是否已复习
}
```

**状态转换**:
```
wrong (错误)
   ↓
reviewing (复习中)
   ↓
corrected (已订正) 或 mastered (已掌握)
```

**验证规则**:
- `correction_attempts`: ≥ 0
- `is_corrected = true` 时，`corrected_at` 必填
- `difficulty`: 必填，枚举值

---

## 数据流架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端应用                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────────┐      ┌──────────────┐      ┌──────────┐  │
│   │  React UI   │ ◀──▶ │ Zustand Store│ ◀──▶ │  API     │  │
│   │ Components  │      │  (State)     │      │ Service  │  │
│   └─────────────┘      └──────────────┘      └──────────┘  │
│         │                     │                     │        │
│         │                     ▼                     │        │
│         │              ┌──────────────┐            │        │
│         │              │ localStorage │            │        │
│         │              │  (Persist)   │            │        │
│         │              └──────────────┘            │        │
│         │                                          │        │
│         ▼                                          ▼        │
│   ┌─────────────────────────────────────────────────────┐  │
│   │                    浏览器存储                        │  │
│   │  - localStorage: 会话、消息、成就                    │  │
│   │  - IndexedDB (可选): 大文件缓存                     │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       后端 API                               │
│  - /api/v1/conversations/* (对话)                            │
│  - /api/v1/images/* (OCR)                                    │
│  - /api/v1/learning/* (学习记录)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 数据同步策略

### 在线同步

```typescript
// 同步策略: 写穿 (Write-Through)
const sendMessage = async (content: string) => {
  // 1. 立即更新本地状态 (乐观更新)
  const optimisticMessage: Message = {
    id: generateUUID(),
    timestamp: new Date().toISOString(),
    role: 'user',
    content,
    is_loading: true,
  }

  addMessage(optimisticMessage)

  // 2. 发送到后端
  try {
    const response = await apiClient.sendTextInput({
      session_id: sessionId,
      content,
    })

    // 3. 更新本地状态为真实数据
    updateMessage(optimisticMessage.id, {
      is_loading: false,
      ...response,
    })

    // 4. 持久化到 localStorage
    persistMessages()
  } catch (error) {
    // 5. 错误处理
    updateMessage(optimisticMessage.id, {
      is_loading: false,
      error: error.message,
    })
  }
}
```

### 离线队列

```typescript
interface OfflineQueueItem {
  id: string
  type: 'voice' | 'text' | 'image'
  data: any
  timestamp: string
  retry_count: number
}

// 离线时将请求加入队列
const enqueueOfflineRequest = (item: OfflineQueueItem) => {
  const queue = loadOfflineQueue()
  queue.push(item)
  localStorage.setItem(STORAGE_KEYS.OFFLINE_QUEUE, JSON.stringify(queue))
}

// 网络恢复时重试
window.addEventListener('online', () => {
  const queue = loadOfflineQueue()
  queue.forEach(async (item) => {
    try {
      await retryRequest(item)
      // 成功后从队列移除
      removeOfflineRequest(item.id)
    } catch {
      item.retry_count++
    }
  })
})
```

---

## 数据验证与类型安全

### Zod Schema 定义

```typescript
import { z } from 'zod'

// Message Schema
export const MessageSchema = z.object({
  id: z.string().uuid(),
  timestamp: z.string().datetime(),
  role: z.enum(['user', 'assistant', 'system']),
  content: z.string().min(1).max(2000),
  input_type: z.enum(['voice', 'text', 'image']).optional(),
  image_url: z.string().url().optional(),
  response_type: z.enum(['guidance', 'encouragement', 'error', 'question']).optional(),
  is_correct: z.boolean().optional(),
  is_loading: z.boolean().optional(),
  confidence: z.number().min(0).max(1).optional(),
  error: z.string().optional(),
})

// Achievement Schema
export const AchievementSchema = z.object({
  id: z.string(),
  name: z.string().min(1).max(50),
  description: z.string().min(1).max(200),
  icon: z.string(),
  unlock_condition: z.object({
    type: z.enum(['correct_streak', 'total_sessions', 'mastery_rate', 'custom']),
    target: z.number().positive(),
  }),
  unlocked_at: z.string().datetime().optional(),
  is_unlocked: z.boolean(),
  rarity: z.enum(['common', 'rare', 'epic', 'legendary']),
  category: z.enum(['learning', 'streak', 'mastery', 'special']),
})
```

---

## 性能优化

### 1. 消息历史分页

```typescript
// 仅保留最近 50 条消息在内存中
const MAX_MESSAGES_IN_MEMORY = 50

const addMessage = (message: Message) => {
  set((state) => {
    const messages = [...state.messages, message]
    const trimmed = messages.slice(-MAX_MESSAGES_IN_MEMORY)
    return { messages: trimmed }
  })
}
```

### 2. 选择性渲染

```typescript
// 使用 Zustand selector 避免不必要的重渲染
const messages = useSessionStore((state) => state.messages)  // ❌ 整个 store 变化都会重渲染
const messages = useSessionStore((state) => state.messages)  // ✅ 仅 messages 变化才重渲染
```

### 3. localStorage 批量写入

```typescript
// 防抖，避免频繁写入
const debouncedPersist = debounce(() => {
  const state = useSessionStore.getState()
  localStorage.setItem(STORAGE_KEYS.MESSAGES_CACHE, JSON.stringify(state.messages))
}, 1000)
```

---

## 安全与隐私

### 数据加密 (可选)

敏感数据（如学生 ID）在存储前加密：

```typescript
const encryptData = (data: string, key: string): string => {
  // 使用 Web Crypto API
  // 参考: https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API
}

const decryptData = (encryptedData: string, key: string): string => {
  // 解密逻辑
}
```

### 数据最小化

- 仅存储必要的数据
- 不存储语音录音（仅存储识别文本）
- 图片缓存仅保留缩略图（< 100KB）
- 提供"清除所有数据"功能

---

## 总结

### 实体关系图

```
SessionState (1) ── (1) (*) Message
                        │
                        ├── (0..1) Image
                        └── (0..1) Voice

SessionState (1) ── (*) Achievement

SessionState (*) ── (*) Mistake

LearningProgress (1) ── (*) SessionState
```

### 下一步

- [x] 定义核心实体
- [x] 设计 Zustand store
- [x] 定义数据流架构
- [ ] 实现 useVoiceRecognition Hook
- [ ] 实现 useCamera Hook
- [ ] 实现 useOfflineSync Hook

---

**Phase 1.1 完成** ✅
