# 示例：任务领取流程

完整的任务领取和实施流程示例。

## 场景

Backend Dev Agent 需要实施学习记录功能。

## 步骤

### 1. 查询可领取任务

```bash
@backend-dev-1:

/task-manager list --status=pending --unclaimed --tag=learning-management
```

**输出**：
```
📋 可领取任务列表（8 个）：

1. LWP-2.2-T001 [P0] 配置 Claude API 集成环境
   - 依赖：无
   - 预估时间：30 分钟

2. LWP-2.2-T002 [P0] 安装 Python 依赖包
   - 依赖：LWP-2.2-T001
   - 预估时间：15 分钟
   - ⚠️ 等待依赖任务完成

3. LWP-2.2-T004 [P1] 创建学习记录扩展模型
   - 依赖：LWP-2.2-T003
   - 预估时间：2 小时
   - 优先级：high

4. LWP-2.2-T006 [P1] 创建知识点模型
   - 依赖：无
   - 预估时间：1.5 小时
   - 优先级：high

...
```

### 2. 领取任务

```bash
@backend-dev-1:

/task-manager claim LWP-2.2-T004 --agent=backend-dev-1 --tag=learning-management
```

**输出**：
```
✅ 任务 LWP-2.2-T004 已被 backend-dev-1 领取
   - 状态更新为 in-progress
   - 领取时间: 2025-01-15 10:30:00 UTC
   - 超时时间: 2025-01-15 11:30:00 UTC（1 小时后）
```

### 3. 阅读实施细节

```bash
@backend-dev-1:

cat specs/001-learning-management/tasks.md | grep -A 25 "T004"
```

**输出**：
```markdown
- [ ] T004 [P] 创建学习记录扩展模型（LearningRecord）
  - **文件位置**: `backend/app/models/learning.py`
  - **技术实现**:
    ```python
    class LearningRecord(Base):
        __tablename__ = 'learning_records'

        id = Column(Integer, primary_key=True)
        student_id = Column(Integer, ForeignKey('students.id'))
        question_content = Column(Text, nullable=False)
        student_answer = Column(String(500))
        is_correct = Column(Boolean, default=False)
        time_spent = Column(Integer)  # 秒
        created_at = Column(DateTime, default=datetime.utcnow)
    ```
  - **索引**: idx_student_id, idx_is_correct, idx_created_at
  - **提交格式**: `[LWP-2.2-T004] feat: 扩展学习记录模型`
```

### 4. 遵循 TDD 循环实施

```bash
@backend-dev-1:

# Red 阶段：编写测试
/tdd-cycle red

# 编写测试代码...
# 提交测试
/git-commit [LWP-2.2-T004] test: 添加学习记录模型测试 (Red)

# Green 阶段：实现功能
/tdd-cycle green

# 实施功能代码...
# 提交功能
/git-commit [LWP-2.2-T004] feat: 实现学习记录模型 (Green)

# Refactor 阶段：重构（可选）
/tdd-cycle refactor

# 重构代码...
# 提交重构
/git-commit [LWP-2.2-T004] refactor: 优化学习记录模型代码 (Refactor)
```

### 5. 更新任务状态

```bash
@backend-dev-1:

/task-manager status LWP-2.2-T004 --status=done --tag=learning-management
```

**输出**：
```
✅ 任务 LWP-2.2-T004 状态已更新为 done
   - 完成时间: 2025-01-15 12:30:00 UTC
   - 用时: 2 小时
   - 任务锁已自动释放

📊 进度更新：
   - learning-management: 20/30 完成 (66.7%)
```

### 6. 验证完成

```bash
@backend-dev-1:

# 查看我的任务
/task-manager list --agent=backend-dev-1

# 查看所有完成任务
/task-manager list --status=done
```

## 多 Agent 并行示例

同时有 3 个 Agent 工作时：

```bash
# 时间线: 10:30

@backend-dev-1:
/task-manager claim LWP-2.2-T004 --agent=backend-dev-1
✅ 领取成功

@backend-dev-2:
/task-manager claim LWP-2.2-T005 --agent=backend-dev-2
✅ 领取成功

@backend-dev-3:
/task-manager claim LWP-2.2-T004 --agent=backend-dev-3
❌ 失败：任务已被 backend-dev-1 领取

@backend-dev-3:
/task-manager claim LWP-2.2-T006 --agent=backend-dev-3
✅ 领取成功
```

## 错误处理

### 任务已被领取

```bash
@backend-dev-2:

/task-manager claim LWP-2.2-T004 --agent=backend-dev-2
```

**输出**：
```
❌ 任务 LWP-2.2-T004 已被 backend-dev-1 领取
   - 领取时间: 2025-01-15 10:30:00 UTC
   - 心跳时间: 2025-01-15 10:35:00 UTC

💡 建议：
   - 等待任务完成或释放
   - 或选择其他可领取任务
```

### 任务不存在

```bash
@backend-dev-1:

/task-manager claim LWP-2.2-T999 --agent=backend-dev-1
```

**输出**：
```
❌ 任务 LWP-2.2-T999 不存在
   - Tag: learning-management
   - Project: /home/luwei/workspace/github/sprout-chat

💡 建议：
   - 使用 /task-manager list 查看所有任务
   - 检查任务 ID 是否正确
```

---

**场景**: Backend Dev 完整工作流
**预计用时**: 2-3 小时
**相关技能**: tdd-cycle, git-commit
