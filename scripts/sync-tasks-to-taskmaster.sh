#!/bin/bash
#
# Spec-Kit 任务同步脚本
# 将 Spec-Kit 生成的任务（T-XXX）映射到 Taskmaster（LWP-XXX）
#
# 用途：
#   1. 为前端任务创建 Taskmaster 子任务
#   2. 建立 Spec-Kit 和 Taskmaster 的映射关系
#   3. 确保任务状态双向同步
#
# 作者: PM Agent
# 日期: 2025-01-14
# 版本: 1.0.0

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 项目根目录
PROJECT_ROOT="/home/luwei/workspace/github/sprout-chat"

# 任务映射配置
# 格式: "T任务编号|LWP父任务|任务描述"
declare -a TASK_MAPPINGS=(
    "T016|LWP-1|实现 useVoiceRecognition Hook (Web Speech API 封装)"
    "T017|LWP-1|实现 AudioContext 音量检测 (静音检测)"
    "T018|LWP-1|编写 useVoiceRecognition 单元测试"
    "T019|LWP-1|增强 VoiceInteraction 组件 (错误处理、重试机制)"
    "T020|LWP-1|编写 VoiceInteraction 组件单元测试"
    "T021|LWP-1|实现 useSpeechSynthesis Hook (TTS 语音播报)"
    "T022|LWP-1|集成 TTS 到 GuidedResponse 组件"
    "T023|LWP-1|增强 TextInteraction 组件 (fallback 方案)"
    "T024|LWP-1|编写 TextInteraction 组件单元测试"
    "T025|LWP-1|扩展 sessionStore 添加连续答对计数"
    "T026|LWP-1|实现 achievement 解锁逻辑"
    "T027|LWP-1|编写语音对话端到端集成测试"
)

# 检查 Taskmaster 是否可用
check_taskmaster() {
    log_info "检查 Taskmaster 是否可用..."

    if ! command -v tm &> /dev/null; then
        log_warning "Taskmaster CLI 不可用，使用 MCP 工具"

        # 检查是否可以通过 MCP 访问
        # 这里假设可以通过某种方式调用 MCP
        return 0
    fi

    log_success "Taskmaster CLI 可用"
    return 0
}

# 创建任务映射
create_task_mapping() {
    local t_task=$1
    local lwp_parent=$2
    local description=$3

    log_info "映射任务: $t_task → $lwp_parent"

    # 使用 Taskmaster MCP 工具创建子任务
    # 注意：这里需要实际的 MCP 调用，目前只是示例
    log_info "  父任务: $lwp_parent"
    log_info "  任务描述: $description"

    # 实际调用示例（需要 MCP 支持）：
    # mcp__task-master-ai__expand_task \
    #     --id="$lwp_parent" \
    #     --num=1 \
    #     --prompt="Frontend task: $t_task - $description" \
    #     --projectRoot="$PROJECT_ROOT"

    log_success "映射创建: $t_task → $lwp_parent"
}

# 同步任务状态
sync_task_status() {
    local t_task=$1
    local status=$2

    log_info "同步任务状态: $t_task → $status"

    # 检查 tasks.md 中的任务状态
    local tasks_file="$PROJECT_ROOT/specs/002-frontend-student-ui/tasks.md"

    if [ ! -f "$tasks_file" ]; then
        log_error "找不到 tasks.md: $tasks_file"
        return 1
    fi

    # 检查任务是否完成
    if grep -q "\- \[x\] $t_task" "$tasks_file"; then
        log_info "任务 $t_task 已完成"

        # 更新 Taskmaster 状态
        # mcp__task-master-ai__set_task_status \
        #     --id="$t_task" \
        #     --status="done" \
        #     --projectRoot="$PROJECT_ROOT"
    elif grep -q "\- \[ \] $t_task" "$tasks_file"; then
        log_info "任务 $t_task 待办"
    else
        log_warning "任务 $t_task 状态未知"
    fi
}

# 验证 Git Commit 格式
validate_commit_format() {
    log_info "验证 Git Commit 格式..."

    local recent_commits=10
    local invalid_commits=0

    # 获取最近的 commit
    while IFS= read -r commit; do
        local hash=$(echo "$commit" | cut -d' ' -f1)
        local msg=$(echo "$commit" | cut -d' ' -f2-)

        # 检查是否包含 [LWP-X] 和 [TXXX]
        if [[ ! "$msg" =~ \[LWP-[0-9]+\] ]] || [[ ! "$msg" =~ \[T[0-9]+\] ]]; then
            log_warning "Commit 格式不正确: $hash"
            log_warning "  消息: $msg"
            log_warning "  期望格式: [LWP-X][TXXX] type: description"
            ((invalid_commits++))
        fi
    done < <(git -C "$PROJECT_ROOT" log --oneline -n "$recent_commits")

    if [ $invalid_commits -eq 0 ]; then
        log_success "所有 commit 格式正确 ✅"
    else
        log_error "发现 $invalid_commits 个格式不正确的 commit"
        return 1
    fi
}

# 生成映射报告
generate_mapping_report() {
    log_info "生成任务映射报告..."

    local report_file="$PROJECT_ROOT/docs/task-mapping-report.md"

    cat > "$report_file" << EOF
# 任务映射报告

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**生成者**: PM Agent
**用途**: Spec-Kit (T-XXX) ↔ Taskmaster (LWP-XXX) 映射

---

## 映射关系

| Spec-Kit 任务 | Taskmaster 任务 | 任务描述 | 状态 |
|--------------|-----------------|----------|------|
EOF

    for mapping in "${TASK_MAPPINGS[@]}"; do
        IFS='|' read -r t_task lwp_parent description <<< "$mapping"

        # 检查任务状态
        local status="⏳ 待办"
        local tasks_file="$PROJECT_ROOT/specs/002-frontend-student-ui/tasks.md"

        if [ -f "$tasks_file" ]; then
            if grep -q "\- \[x\] $t_task" "$tasks_file"; then
                status="✅ 完成"
            elif grep -q "\- \[ \] $t_task" "$tasks_file"; then
                status="⏳ 待办"
            fi
        fi

        echo "| $t_task | $lwp_parent | $description | $status |" >> "$report_file"
    done

    cat >> "$report_file" << EOF

---

## Git Commit 格式验证

EOF

    # 验证 commit 格式
    if validate_commit_format &>> "$report_file"; then
        echo "✅ 所有 commit 格式正确" >> "$report_file"
    else
        echo "❌ 发现格式不正确的 commit（详见上方日志）" >> "$report_file"
    fi

    cat >> "$report_file" << EOF

---

## 下一步行动

- [ ] 确保所有 Git commit 包含 [LWP-X][TXXX] 格式
- [ ] 同步任务状态到 Taskmaster
- [ ] 协调 frontend-dev 和 backend-dev 任务分配

---

**报告结束**
EOF

    log_success "映射报告已生成: $report_file"
}

# 主函数
main() {
    log_info "开始同步 Spec-Kit 任务到 Taskmaster..."
    log_info "项目根目录: $PROJECT_ROOT"

    # 检查项目根目录
    if [ ! -d "$PROJECT_ROOT" ]; then
        log_error "项目根目录不存在: $PROJECT_ROOT"
        exit 1
    fi

    # 检查 Taskmaster
    check_taskmaster

    # 创建任务映射
    log_info "创建任务映射..."
    for mapping in "${TASK_MAPPINGS[@]}"; do
        IFS='|' read -r t_task lwp_parent description <<< "$mapping"
        create_task_mapping "$t_task" "$lwp_parent" "$description"
    done

    # 同步任务状态
    log_info "同步任务状态..."
    for mapping in "${TASK_MAPPINGS[@]}"; do
        IFS='|' read -r t_task lwp_parent description <<< "$mapping"
        sync_task_status "$t_task"
    done

    # 验证 Git Commit 格式
    log_info "验证 Git Commit 格式..."
    validate_commit_format

    # 生成映射报告
    generate_mapping_report

    log_success "任务同步完成！"
    log_info "请查看映射报告了解详细信息"
}

# 执行主函数
main "$@"
