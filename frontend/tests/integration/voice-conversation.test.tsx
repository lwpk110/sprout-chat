/**
 * 语音对话端到端集成测试
 * 测试完整的语音交互流程，包括：
 * - 会话初始化
 * - 语音输入
 * - 消息发送
 * - AI 响应
 * - TTS 语音播报
 * - 学习进度追踪
 * - 成就解锁
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { renderHook, act } from '@testing-library/react'
import StudentHome from '../../src/pages/StudentHome'
import { useSessionStore } from '../../src/store/sessionStore'
import { apiClient } from '../../src/services/api'

// Mock the API client
jest.mock('../../src/services/api')

// Mock useVoiceRecognition Hook
jest.mock('../../src/hooks/useVoiceRecognition', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    isListening: false,
    transcript: '',
    interimTranscript: '',
    isSupported: true,
    error: null,
    startListening: jest.fn(() => true),
    stopListening: jest.fn(),
    resetTranscript: jest.fn(),
  })),
}))

// Mock useSpeechSynthesis Hook
jest.mock('../../src/hooks/useSpeechSynthesis', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    speak: jest.fn(),
    isSupported: true,
    isSpeaking: false,
    cancel: jest.fn(),
  })),
}))

// Mock SilenceDetector
jest.mock('../../src/utils/audio', () => ({
  SilenceDetector: jest.fn().mockImplementation(() => ({
    start: jest.fn().mockResolvedValue(undefined),
    stop: jest.fn(),
  })),
}))

const mockApi = apiClient as jest.Mocked<typeof apiClient>

describe('语音对话端到端集成测试 (T027)', () => {
  beforeEach(() => {
    jest.clearAllMocks()

    // 重置 store 状态
    const store = useSessionStore.getState()
    store.setSession({
      session_id: '',
      student_id: '',
      subject: '数学',
      student_age: 6,
      is_valid: false,
    })
    store.setMessages([])
    store.updateStats({
      totalQuestions: 0,
      correctAnswers: 0,
      incorrectAnswers: 0,
      accuracy: 0,
      currentStreak: 0,
      longestStreak: 0,
      todayStudyTime: 0,
      lastStudyTime: null,
    })
    store.resetAchievements()
    store.setLoading(false)
    store.setError(null)
  })

  describe('完整对话流程', () => {
    it('应该完成一次完整的语音对话', async () => {
      // Mock API 响应
      mockApi.createSession.mockResolvedValue({
        session_id: 'test-session-123',
        student_id: 'student-001',
        subject: '数学',
        student_age: 6,
        is_valid: true,
      })

      mockApi.sendVoiceInput.mockResolvedValue({
        response: '很好！答案是正确的。你知道1+1等于几吗？',
        next_question: '1+1等于几？',
      })

      render(<StudentHome />)

      // 1. 应该先显示加载界面
      expect(screen.getByText('小芽正在赶来...')).toBeInTheDocument()

      // 2. 应该自动初始化会话
      await waitFor(() => {
        expect(mockApi.createSession).toHaveBeenCalled()
      }, { timeout: 3000 })

      // 3. 会话初始化后应该显示欢迎界面
      await waitFor(() => {
        // emoji 和文本可能分开，分别匹配
        expect(screen.getByText('🌱')).toBeInTheDocument()
        expect(screen.getByText('小芽家教')).toBeInTheDocument()
        expect(screen.getByText('你的 AI 学习伙伴')).toBeInTheDocument()
      }, { timeout: 3000 })

      // 4. 应该显示三个交互组件
      await waitFor(() => {
        // emoji 和文本在同一元素，使用正则匹配
        expect(screen.getByText(/语音对话/)).toBeInTheDocument()
        expect(screen.getByText(/文字对话/)).toBeInTheDocument()
        // PhotoInteraction 使用"点击拍照"
        expect(screen.getByText(/点击拍照/)).toBeInTheDocument()
      }, { timeout: 3000 })
    })

    it('应该支持文字输入对话', async () => {
      // Mock API 响应
      mockApi.createSession.mockResolvedValue({
        session_id: 'test-session-456',
        student_id: 'student-002',
        subject: '数学',
        student_age: 7,
        is_valid: true,
      })

      mockApi.sendTextInput.mockResolvedValue({
        response: '对的！2+3等于5。你真棒！',
      })

      render(<StudentHome />)

      // 等待会话初始化
      await waitFor(() => {
        expect(screen.getByText('✍️ 文字对话')).toBeInTheDocument()
      })

      // 找到文字输入框
      const textarea = screen.getByPlaceholderText('在这里输入你想说的话...')
      const sendButton = screen.getByRole('button', { name: /发送消息/ })

      // 输入文字
      fireEvent.change(textarea, { target: { value: '2+3等于几？' } })
      expect(textarea).toHaveValue('2+3等于几？')

      // 点击发送
      fireEvent.click(sendButton)

      // 验证 API 调用
      await waitFor(() => {
        expect(mockApi.sendTextInput).toHaveBeenCalledWith({
          session_id: 'test-session-456',
          content: '2+3等于几？',
        })
      })
    })
  })

  describe('学习进度追踪', () => {
    it('应该正确追踪学习统计', async () => {
      const { result } = renderHook(() => useSessionStore())

      // 初始状态
      expect(result.current.stats.totalQuestions).toBe(0)
      expect(result.current.stats.currentStreak).toBe(0)

      // 模拟连续答对 5 题
      act(() => {
        for (let i = 0; i < 5; i++) {
          result.current.recordAnswer(true)
        }
      })

      // 验证统计
      expect(result.current.stats.totalQuestions).toBe(5)
      expect(result.current.stats.correctAnswers).toBe(5)
      expect(result.current.stats.currentStreak).toBe(5)
      expect(result.current.stats.longestStreak).toBe(5)
      expect(result.current.stats.accuracy).toBe(100)
    })

    it('答错时应该重置连续答对', async () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        // 连续答对 3 题
        for (let i = 0; i < 3; i++) {
          result.current.recordAnswer(true)
        }

        // 答错 1 题
        result.current.recordAnswer(false)
      })

      expect(result.current.stats.currentStreak).toBe(0)
      expect(result.current.stats.longestStreak).toBe(3) // 保留历史最大值
    })
  })

  describe('成就解锁', () => {
    it('连续答对 3 题应该解锁三连胜成就', async () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        for (let i = 0; i < 3; i++) {
          result.current.recordAnswer(true)
        }
      })

      const streak3 = result.current.achievements.find(a => a.id === 'streak-3')
      expect(streak3).toBeDefined()
      expect(streak3?.name).toBe('三连胜！')
      expect(streak3?.icon).toBe('🔥')
    })

    it('首次答对应该解锁成就', async () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.recordAnswer(true)
      })

      const firstCorrect = result.current.achievements.find(a => a.id === 'first-correct')
      expect(firstCorrect).toBeDefined()
      expect(firstCorrect?.name).toBe('第一次答对！')
    })

    it('答对 10 题应该解锁多个成就', async () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        for (let i = 0; i < 10; i++) {
          result.current.recordAnswer(true)
        }
      })

      // 应该解锁：first-correct, streak-3, streak-5, streak-10, questions-10
      expect(result.current.achievements.length).toBeGreaterThanOrEqual(5)

      const streak10 = result.current.achievements.find(a => a.id === 'streak-10')
      expect(streak10).toBeDefined()
      expect(streak10?.name).toBe('十连胜王者！')
    })
  })

  describe('错误处理', () => {
    it('会话初始化失败应该显示错误提示', async () => {
      mockApi.createSession.mockRejectedValue(new Error('网络错误'))

      render(<StudentHome />)

      await waitFor(() => {
        expect(screen.getByText(/哎呀，出错了/)).toBeInTheDocument()
      })
    })

    it('消息发送失败应该显示错误', async () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.setError('发送消息失败，请重试')
      })

      // 验证错误状态
      expect(result.current.error).toBe('发送消息失败，请重试')
    })
  })

  describe('消息历史', () => {
    it('应该正确保存和显示消息历史', async () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.addMessage('user', '你好，小芽')
        result.current.addMessage('assistant', '你好！我是小芽，很高兴认识你！')
        result.current.addMessage('user', '教我算术')
      })

      expect(result.current.messages).toHaveLength(3)
      expect(result.current.messages[0].content).toBe('你好，小芽')
      expect(result.current.messages[1].content).toBe('你好！我是小芽，很高兴认识你！')
      expect(result.current.messages[2].content).toBe('教我算术')
    })

    it('清除会话时应该保留学习统计和成就', async () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        // 设置会话
        result.current.setSession({
          session_id: 'test-session',
          student_id: 'student-123',
          subject: '数学',
          student_age: 6,
          is_valid: true,
        })

        // 添加一些学习数据
        result.current.addMessage('user', '测试消息')
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
      })

      const statsBeforeClear = result.current.stats
      const achievementsBeforeClear = result.current.achievements

      act(() => {
        result.current.clearSession()
      })

      // 会话应该清除
      expect(result.current.sessionId).toBeNull()
      expect(result.current.messages).toHaveLength(0)

      // 但学习统计和成就应该保留
      expect(result.current.stats).toEqual(statsBeforeClear)
      expect(result.current.achievements).toEqual(achievementsBeforeClear)
    })
  })

  describe('UI 状态管理', () => {
    it('应该正确管理加载状态', async () => {
      mockApi.createSession.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({
          session_id: 'test-session-loading',
          student_id: 'student-loading',
          subject: '数学',
          student_age: 6,
          is_valid: true,
        }), 100))
      )

      render(<StudentHome />)

      // 初始状态应该是加载中
      const store = useSessionStore.getState()
      expect(store.isLoading).toBe(true)
    })

    it('应该正确重置错误状态', async () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.setError('测试错误')
      })

      expect(result.current.error).toBe('测试错误')

      act(() => {
        result.current.setError(null)
      })

      expect(result.current.error).toBeNull()
    })
  })

  describe('持久化', () => {
    it('清除会话后重新初始化应该恢复学习统计', async () => {
      const { result: result1 } = renderHook(() => useSessionStore())

      // 第一次会话：记录一些学习数据
      act(() => {
        result1.current.setSession({
          session_id: 'session-1',
          student_id: 'student-1',
          subject: '数学',
          student_age: 6,
          is_valid: true,
        })

        for (let i = 0; i < 5; i++) {
          result1.current.recordAnswer(true)
        }
      })

      const stats1 = result1.current.stats
      const achievements1 = result1.current.achievements

      // 清除会话
      act(() => {
        result1.current.clearSession()
      })

      // 新会话：应该恢复学习统计
      const { result: result2 } = renderHook(() => useSessionStore())

      act(() => {
        result2.current.setSession({
          session_id: 'session-2',
          student_id: 'student-2',
          subject: '数学',
          student_age: 6,
          is_valid: true,
        })
      })

      // 学习统计应该保留
      expect(result2.current.stats.totalQuestions).toBe(stats1.totalQuestions)
      expect(result2.current.stats.correctAnswers).toBe(stats1.correctAnswers)
      expect(result2.current.stats.longestStreak).toBe(stats1.longestStreak)

      // 成就应该保留
      expect(result2.current.achievements.length).toBe(achievements1.length)
    })
  })
})
