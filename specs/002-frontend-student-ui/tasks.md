# Implementation Tasks: 小芽家教前端学生界面

**Feature Branch**: `002-frontend-student-ui`
**Generated**: 2025-01-13
**Status**: Ready for Implementation

## 概述

本文档定义前端实施的完整任务清单，任务按用户故事组织，确保每个用户故事可以独立实现和测试。

**实施策略**: MVP 优先，增量交付
- **MVP 范围**: User Story 1 (P1) - 语音对话学习
- **增量功能**: User Story 2 (P2), User Story 3 (P3)

**技术栈**: React 18 + TypeScript 5.2 + Vite + Zustand + Tailwind CSS

---

## Phase 1: Setup 项目初始化

**目标**: 确保项目依赖和配置完整，为后续开发做好准备。

- [X] T001 [P] 安装图片压缩依赖 browser-image-compression 在 frontend/
- [X] T002 [P] 检查并验证 .env.development 环境变量配置在 frontend/
- [X] T003 [P] 验证 Vite proxy 配置指向后端 API 在 frontend/vite.config.ts
- [X] T004 [P] 确认 Tailwind CSS 适龄设计类名配置在 frontend/tailwind.config.js

**完成标准**:
- 所有依赖安装完成
- 开发服务器可正常启动
- 代理配置正确，API 请求可达后端

---

## Phase 2: Foundational 基础设施

**目标**: 实现所有用户故事依赖的基础工具和类型定义。

**独立测试标准**: 这些工具函数和类型定义应通过独立的单元测试验证。

### 2.1 类型定义扩展

- [X] T005 [P] 添加 LearningProgress 类型定义在 frontend/src/types/index.ts
- [X] T006 [P] 添加 Achievement 类型定义在 frontend/src/types/index.ts
- [X] T007 [P] 添加 Mistake 类型定义在 frontend/src/types/index.ts
- [X] T008 [P] 添加 OfflineQueueItem 类型定义在 frontend/src/types/index.ts
- [X] T009 [P] 创建 Zod 验证 Schema 在 frontend/src/types/validation.ts

### 2.2 工具函数

- [X] T010 [P] 实现时间格式化工具 (相对时间) 在 frontend/src/utils/format.ts
- [X] T011 [P] 实现 localStorage 持久化工具 在 frontend/src/utils/storage.ts
- [X] T012 [P] 实现图片压缩工具 (基于 browser-image-compression) 在 frontend/src/utils/image.ts
- [X] T013 [P] 实现错误处理和友好提示转换 在 frontend/src/utils/errorHandler.ts

### 2.3 基础 Hooks

- [X] T014 [P] 实现 useLocalStorage Hook 在 frontend/src/hooks/useLocalStorage.ts
- [X] T015 实现全局错误边界组件 ErrorBoundary 在 frontend/src/components/ErrorBoundary.tsx

**完成标准**:
- 所有工具函数通过单元测试
- TypeScript 类型检查无错误
- localStorage 持久化测试通过

---

## Phase 3: User Story 1 - 语音对话学习 (P1)

**用户故事**: 一年级学生通过语音与 AI 小芽老师对话，提问数学问题，获得引导式回答而非直接答案，培养思考能力。

**优先级**: P1 (核心功能)

**独立测试标准**:
- 学生可以独立完成语音提问并获得 AI 响应
- 语音识别失败时有友好重试提示
- 连续答对 3 题时显示动画奖励
- 任务完成率 ≥ 90%

### 3.1 Web Speech API Hook

- [X] T016 [US1] 实现 useVoiceRecognition Hook (Web Speech API 封装) 在 frontend/src/hooks/useVoiceRecognition.ts
- [X] T017 [US1] 实现 AudioContext 音量检测 (静音检测) 在 frontend/src/utils/audio.ts
- [X] T018 [P] [US1] 编写 useVoiceRecognition 单元测试 在 frontend/src/hooks/__tests__/useVoiceRecognition.test.ts

### 3.2 VoiceInteraction 组件增强

- [X] T019 [US1] 增强 VoiceInteraction 组件 (错误处理、重试机制) 在 frontend/src/components/VoiceInteraction.tsx
- [ ] T020 [P] [US1] 编写 VoiceInteraction 组件单元测试 在 frontend/src/components/__tests__/VoiceInteraction.test.tsx

### 3.3 语音播报功能 (TTS)

- [ ] T021 [US1] 实现 useSpeechSynthesis Hook (TTS 语音播报) 在 frontend/src/hooks/useSpeechSynthesis.ts
- [ ] T022 [US1] 集成 TTS 到 GuidedResponse 组件 在 frontend/src/components/GuidedResponse.tsx

### 3.4 TextInteraction 组件增强

- [ ] T023 [P] [US1] 增强 TextInteraction 组件 (fallback 方案) 在 frontend/src/components/TextInteraction.tsx
- [ ] T024 [P] [US1] 编写 TextInteraction 组件单元测试 在 frontend/src/components/__tests__/TextInteraction.test.tsx

### 3.5 Zustand Store 扩展

- [ ] T025 [US1] 扩展 sessionStore 添加连续答对计数 在 frontend/src/store/sessionStore.ts
- [ ] T026 [US1] 实现 achievement 解锁逻辑 在 frontend/src/store/sessionStore.ts

### 3.6 集成测试

- [ ] T027 [US1] 编写语音对话端到端集成测试 在 frontend/tests/integration/voice-conversation.test.tsx

**完成标准**:
- 语音录制延迟 ≤ 500ms
- 语音识别失败时有友好提示
- 连续答对 3 题显示成就动画
- 集成测试覆盖关键用户流程

---

## Phase 4: User Story 2 - 拍照上传作业 (P2)

**用户故事**: 学生通过拍照上传手写作业或练习题，AI 识别题目内容并提供个性化辅导。

**优先级**: P2 (扩展功能)

**依赖**: User Story 1 的基础组件

**独立测试标准**:
- 学生可以独立拍照上传并获得识别结果
- 图片模糊时有重拍提示
- 图片上传在 5 秒内完成

### 4.1 摄像头访问 Hook

- [ ] T028 [P] [US2] 实现 useCamera Hook (摄像头访问) 在 frontend/src/hooks/useCamera.ts
- [ ] T029 [P] [US2] 编写 useCamera 单元测试 在 frontend/src/hooks/__tests__/useCamera.test.ts

### 4.2 PhotoInteraction 组件增强

- [ ] T030 [US2] 增强 PhotoInteraction 组件 (模糊检测、进度显示) 在 frontend/src/components/PhotoInteraction.tsx
- [ ] T031 [P] [US2] 编写 PhotoInteraction 组件单元测试 在 frontend/src/components/__tests__/PhotoInteraction.test.tsx

### 4.3 图片预览与确认

- [ ] T032 [US2] 实现 ImagePreview 组件 (本地预览、质量检查) 在 frontend/src/components/ImagePreview.tsx
- [ ] T033 [P] [US2] 编写 ImagePreview 组件单元测试 在 frontend/src/components/__tests__/ImagePreview.test.tsx

### 4.4 API 集成

- [ ] T034 [US2] 在 api.ts 中添加 uploadImageForGuidance 方法 在 frontend/src/services/api.ts
- [ ] T035 [US2] 处理图片上传错误 (模糊检测、格式不支持) 在 frontend/src/utils/errorHandler.ts

### 4.5 集成测试

- [ ] T036 [US2] 编写拍照上传端到端集成测试 在 frontend/tests/integration/photo-upload.test.tsx

**完成标准**:
- 摄像头调用成功，实时预览流畅
- 图片压缩至 < 1MB，耗时 < 2 秒
- 图片上传在 5 秒内完成
- 模糊检测准确率 ≥ 80%

---

## Phase 5: User Story 3 - 学习进度可视化 (P3)

**用户故事**: 学生和父母可以查看学习进度，包括已掌握知识点、错题本、学习时长等，激励持续学习。

**优先级**: P3 (增强功能)

**依赖**: User Story 1 和 User Story 2

**独立测试标准**:
- 学生可以查看进度图表和成就徽章
- 家长可以查看学习报告
- 错题本功能完整

### 5.1 进度页面

- [ ] T037 [P] [US3] 创建 ProgressPage 页面组件 在 frontend/src/pages/ProgressPage.tsx
- [ ] T038 [P] [US3] 在 App.tsx 中添加进度页面路由 在 frontend/src/App.tsx

### 5.2 进度组件

- [ ] T039 [P] [US3] 实现 ProgressBar 组件 (学习进度条) 在 frontend/src/components/ProgressBar.tsx
- [ ] T040 [P] [US3] 实现 AchievementBadge 组件 (成就徽章) 在 frontend/src/components/AchievementBadge.tsx
- [ ] T041 [P] [US3] 实现 MistakeCard 组件 (错题卡片) 在 frontend/src/components/MistakeCard.tsx
- [ ] T042 [P] [US3] 编写进度组件单元测试 在 frontend/src/components/__tests__/progress.test.tsx

### 5.3 API 集成

- [ ] T043 [US3] 在 api.ts 中添加 getLearningProgress 方法 在 frontend/src/services/api.ts
- [ ] T044 [US3] 在 api.ts 中添加 getMistakes 方法 在 frontend/src/services/api.ts
- [ ] T045 [US3] 在 api.ts 中添加 getAchievements 方法 在 frontend/src/services/api.ts

### 5.4 数据可视化

- [ ] T046 [US3] 实现简单的统计图表 (使用 CSS 或轻量级库) 在 frontend/src/components/StatsChart.tsx
- [ ] T047 [P] [US3] 编写统计图表单元测试 在 frontend/src/components/__tests__/StatsChart.test.tsx

### 5.5 设置页面

- [ ] T048 [P] [US3] 创建 SettingsPage 页面组件 (数据清除、隐私设置) 在 frontend/src/pages/SettingsPage.tsx
- [ ] T049 [P] [US3] 实现"清除所有数据"功能 在 frontend/src/utils/storage.ts

### 5.6 集成测试

- [ ] T050 [US3] 编写进度页面端到端集成测试 在 frontend/tests/integration/progress-page.test.tsx

**完成标准**:
- 进度页面正确显示学习统计
- 成就徽章动画流畅
- 错题本可以按类型筛选
- "清除所有数据"功能正常工作

---

## Phase 6: Polish 优化与跨功能关注点

**目标**: 提升用户体验、性能、安全性和可访问性。

### 6.1 离线缓存机制

- [ ] T051 [P] 实现 useOfflineSync Hook 在 frontend/src/hooks/useOfflineSync.ts
- [ ] T052 [P] 实现离线队列管理 在 frontend/src/utils/offlineQueue.ts
- [ ] T053 [P] 编写离线同步单元测试 在 frontend/src/hooks/__tests__/useOfflineSync.test.ts

### 6.2 性能优化

- [ ] T054 [P] 实现代码分割和懒加载 在 frontend/src/App.tsx
- [ ] T055 [P] 优化图片加载 (懒加载、占位符) 在 frontend/src/components/ImagePreview.tsx
- [ ] T056 [P] 实现消息历史虚拟化 (或分页) 在 frontend/src/components/MessageList.tsx

### 6.3 适龄设计验证

- [ ] T057 [P] 验证所有按钮 ≥ 48x48px (适龄设计) 在 frontend/src/components/
- [ ] T058 [P] 验证所有正文字体 ≥ 18px (适龄设计) 在 frontend/src/
- [ ] T059 [P] 验证色彩对比度 ≥ 7:1 (WCAG AAA) 在 frontend/tailwind.config.js

### 6.4 安全审计

- [ ] T060 [P] 实现麦克风/摄像头权限检查和友好提示 在 frontend/src/utils/permissions.ts
- [ ] T061 [P] 验证 localStorage 数据不包含敏感信息 在 frontend/src/utils/storage.ts
- [ ] T062 [P] 实现 CSRF 防护 (API 请求) 在 frontend/src/services/api.ts

### 6.5 可访问性 (A11y)

- [ ] T063 [P] 添加 ARIA 标签到所有交互元素 在 frontend/src/components/
- [ ] T064 [P] 实现键盘导航支持 在 frontend/src/pages/StudentHome.tsx
- [ ] T065 [P] 添加屏幕阅读器支持 在 frontend/src/components/VoiceInteraction.tsx

### 6.6 错误监控

- [ ] T066 [P] 实现全局错误日志上报 在 frontend/src/utils/logger.ts
- [ ] T067 [P] 添加用户行为分析 (可选) 在 frontend/src/utils/analytics.ts

**完成标准**:
- 首屏加载时间 ≤ 2 秒
- 所有适龄设计检查通过
- 安全审计无高危问题
- 可访问性测试通过

---

## Phase 7: Testing 全面测试

**目标**: 确保代码质量，测试覆盖率 ≥ 80%。

### 7.1 单元测试

- [ ] T068 [P] 补充所有组件单元测试 (覆盖率 ≥ 80%) 在 frontend/src/components/__tests__/
- [ ] T069 [P] 补充所有 Hooks 单元测试 在 frontend/src/hooks/__tests__/
- [ ] T070 [P] 补充所有工具函数单元测试 在 frontend/src/utils/__tests__/

### 7.2 集成测试

- [ ] T071 [P] 编写完整用户流程集成测试 在 frontend/tests/integration/
- [ ] T072 [P] 编写 API 契约测试 在 frontend/tests/contract/api-contract.test.ts

### 7.3 端到端测试

- [ ] T073 编写语音对话 E2E 测试 (关键流程) 在 frontend/tests/e2e/voice-flow.spec.ts
- [ ] T074 编写拍照上传 E2E 测试 (关键流程) 在 frontend/tests/e2e/photo-flow.spec.ts
- [ ] T075 编写进度查看 E2E 测试 (关键流程) 在 frontend/tests/e2e/progress-flow.spec.ts

### 7.4 性能测试

- [ ] T076 [P] 运行 Lighthouse 性能测试 (目标: ≥ 90 分) 在 frontend/
- [ ] T077 [P] 测试首屏加载时间 (目标: ≤ 2 秒) 在 frontend/
- [ ] T078 [P] 测试语音录制启动延迟 (目标: ≤ 500ms) 在 frontend/

### 7.5 用户测试

- [ ] T079 组织一年级学生用户测试 (任务完成率 ≥ 90%) 在 frontend/
- [ ] T080 组织家长满意度调查 (满意度 ≥ 80%) 在 frontend/

**完成标准**:
- 测试覆盖率 ≥ 80%
- 所有关键流程测试通过
- 性能指标全部达标
- 用户测试通过

---

## 任务依赖关系

```
Phase 1: Setup
   ↓
Phase 2: Foundational
   ↓
   ├─→ Phase 3: User Story 1 (P1) ← MVP 范围
   │       ↓
   └─→ Phase 4: User Story 2 (P2)
           ↓
           └─→ Phase 5: User Story 3 (P3)
                   ↓
Phase 6: Polish
   ↓
Phase 7: Testing
```

**依赖说明**:
- Phase 2 必须在所有用户故事之前完成
- User Story 1 (P1) 是 MVP，无其他用户故事依赖
- User Story 2 (P2) 可以与 User Story 1 并行开发（部分依赖）
- User Story 3 (P3) 依赖 User Story 1 和 User Story 2 的数据

---

## 并行执行机会

### Phase 1 完全并行 (T001-T004)
所有 Setup 任务可以并行执行。

### Phase 2 部分并行
- **并行组 1**: T005-T009 (类型定义)
- **并行组 2**: T010-T013 (工具函数)
- **串行**: T014 (依赖 T011), T015 (依赖所有工具)

### Phase 3 部分并行
- **并行组 1**: T016-T017 (useVoiceRecognition 实现)
- **并行组 2**: T018 (useVoiceRecognition 测试)
- **并行组 3**: T021-T022 (TTS 功能)
- **并行组 4**: T023-T024 (TextInteraction)

### Phase 4 完全并行
- T028-T029 (useCamera)
- T032-T033 (ImagePreview)
- 可以与 Phase 3 后期任务并行

### Phase 5 高度并行
- T037-T042 (页面和组件) 完全并行
- T043-T045 (API 方法) 并行
- T048-T049 (设置页面) 并行

### Phase 6 完全并行 (T051-T067)
所有 Polish 任务可以并行执行。

### Phase 7 部分并行
- T068-T072 (单元测试和集成测试) 并行
- T073-T075 (E2E 测试) 串行（需要完整环境）
- T076-T078 (性能测试) 并行

---

## MVP 范围建议

**推荐 MVP**: Phase 1 + Phase 2 + Phase 3

**包含任务**: T001-T027

**交付成果**:
- 学生可以通过语音与 AI 对话学习
- 错误处理和重试机制完善
- 基础成就系统（连续答对奖励）
- 完整的测试覆盖

**预计工作量**: 20-25 个任务

**增量 1**: Phase 4 (拍照上传) - 9 个任务
**增量 2**: Phase 5 (进度可视化) - 14 个任务
**增量 3**: Phase 6 + Phase 7 (优化与测试) - 27 个任务

---

## 实施建议

### 开发顺序

1. **Week 1**: Phase 1 + Phase 2 (基础设施)
2. **Week 2-3**: Phase 3 (MVP - 语音对话)
3. **Week 4**: Phase 4 (拍照上传) + MVP 测试
4. **Week 5**: Phase 5 (进度可视化)
5. **Week 6**: Phase 6 (优化) + Phase 7 (全面测试)

### TDD 要求

根据项目宪章 P2 原则，所有功能开发必须遵循 TDD 循环：

```
Red (红灯) → Green (绿灯) → Refactor (重构)
   ↓            ↓              ↓
Commit       Commit         Commit
  测试         功能           重构
```

**提交格式**:
- Red: `[LWP-XX] test: 添加 XXX 测试 (Red)`
- Green: `[LWP-XX] feat: 实现 XXX 功能 (Green)`
- Refactor: `[LWP-XX] refactor: 优化 XXX 代码 (Refactor)`

### 测试覆盖率要求

- **单元测试覆盖率**: ≥ 80%
- **关键组件**: 100% (VoiceInteraction, PhotoInteraction, API 服务)
- **集成测试**: 覆盖所有关键用户流程

---

## 总任务统计

| Phase | 任务数 | 并行机会 | 预计时间 (天) |
|-------|--------|---------|---------------|
| Phase 1: Setup | 4 | 100% | 0.5 |
| Phase 2: Foundational | 11 | 80% | 2 |
| Phase 3: US1 (P1) | 12 | 60% | 5 |
| Phase 4: US2 (P2) | 9 | 70% | 3 |
| Phase 5: US3 (P3) | 14 | 70% | 4 |
| Phase 6: Polish | 17 | 100% | 3 |
| Phase 7: Testing | 13 | 60% | 4 |
| **总计** | **80** | **平均 75%** | **21.5** |

---

## 下一步行动

1. ✅ 确认 MVP 范围 (Phase 1-3)
2. ✅ 创建 Taskmaster 任务并分配
3. ✅ 启动 Ralph Loop 实施 (`/ralph-loop`)
4. ✅ 遵循 TDD 循环开发
5. ✅ 每个 Phase 完成后运行测试验证

---

**任务清单生成完成** ✅

**准备就绪，可以开始实施！** 🚀
