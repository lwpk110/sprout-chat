# Ralph Loop 使用指南 - 小芽家教项目

## 快速开始

### 1. 启动 Ralph Loop

```bash
# 在 Claude Code 中执行
/ralph-loop "继续 Phase 2.2 学习管理系统开发"
```

### 2. 停止 Ralph Loop

```bash
/cancel-ralph
```

## 当前迭代任务

**Phase 2.2: 学习管理系统开发**

详细提示词请查看 `PROMPT.md`

### 核心目标
1. ✅ 学习记录 API
2. ✅ 苏格拉底式引导教学
3. ✅ 错题本功能
4. ✅ 知识点图谱

### 完成标准
- 所有功能实现并测试通过
- 测试覆盖率 > 80%
- 与现有认证系统集成验证
- API 响应时间 < 2 秒（p95）

## Ralph Loop 最佳实践

### 每次迭代做什么

1. **阅读提示词** - 查看 PROMPT.md 了解任务
2. **检查现状** - 查看现有代码和测试
3. **选择一个功能点** - 专注单一任务
4. **实现功能** - 编写代码，遵循规范
5. **编写测试** - 确保测试覆盖
6. **运行测试** - 验证功能正常
7. **更新文档** - 记录重要变更

### 完成信号

当所有目标达成时，输出：
```
<promise>Phase 2.2 学习管理系统核心功能完成：学习记录API、苏格拉底引导教学、错题本功能、知识点图谱均已实现并通过测试，所有API端点响应正常，测试覆盖率>80%，与现有认证系统集成验证通过。</promise>
```

Ralph Loop 会检测到这个信号并自动停止。

## 项目状态

### 已完成
- ✅ Phase 0: 项目基础设施
- ✅ Phase 1: MVP 核心功能
- ✅ Phase 2.1: 用户系统和数据库集成

### 进行中
- 🔄 Phase 2.2: 学习管理系统

### 待开始
- ⏳ Phase 2.3: 家长模式
- ⏳ Phase 2.4: 内容管理

## 常用命令

```bash
# 查看任务列表
tm list

# 查看具体任务详情
tm get <task-id>

# 设置任务状态
tm set-status --id=<task-id> --status=in-progress

# 测试服务
curl http://localhost:8000/health

# 运行测试
pytest

# 查看日志
tail -f /tmp/fastapi_restart.log
```

## 注意事项

1. **一次只做一件事** - Ralph Loop 的优势是专注和迭代
2. **保持测试通过** - 每次修改都要确保测试通过
3. **小步快跑** - 小改动、频繁提交、快速验证
4. **及时沟通** - 遇到阻塞问题立即提出

## 技术文档

- 数据库设计: `docs/database_schema.md`
- 项目计划: `tasks.md`
- API 文档: http://localhost:8000/docs
- 完成报告: `PHASE2_1_COMPLETION_REPORT.md`
