/**
 * sessionStore 测试
 * 测试学习统计、连续答对计数、成就解锁等功能
 */

import { renderHook, act } from '@testing-library/react'
import { useSessionStore } from '../sessionStore'

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  clear: jest.fn(),
  removeItem: jest.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

describe('sessionStore', () => {
  beforeEach(() => {
    // 重置 store 状态到初始值
    act(() => {
      const store = useSessionStore.getState()

      // 重置会话状态
      store.setSession({
        session_id: '',
        student_id: '',
        subject: '数学',
        student_age: 6,
        is_valid: false,
      })

      // 清除消息
      store.setMessages([])

      // 重置学习统计
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

      // 重置成就
      store.resetAchievements()

      // 重置 UI 状态
      store.setLoading(false)
      store.setError(null)
    })

    // 清除 localStorage mock
    localStorageMock.clear.mockClear()
    localStorageMock.getItem.mockClear()
    localStorageMock.setItem.mockClear()
  })

  describe('学习统计', () => {
    it('应该初始化为零状态', () => {
      const { result } = renderHook(() => useSessionStore())

      expect(result.current.stats.totalQuestions).toBe(0)
      expect(result.current.stats.correctAnswers).toBe(0)
      expect(result.current.stats.incorrectAnswers).toBe(0)
      expect(result.current.stats.accuracy).toBe(0)
      expect(result.current.stats.currentStreak).toBe(0)
      expect(result.current.stats.longestStreak).toBe(0)
    })

    it('应该正确记录答对', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.recordAnswer(true)
      })

      expect(result.current.stats.totalQuestions).toBe(1)
      expect(result.current.stats.correctAnswers).toBe(1)
      expect(result.current.stats.incorrectAnswers).toBe(0)
      expect(result.current.stats.accuracy).toBe(100)
    })

    it('应该正确记录答错', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.recordAnswer(false)
      })

      expect(result.current.stats.totalQuestions).toBe(1)
      expect(result.current.stats.correctAnswers).toBe(0)
      expect(result.current.stats.incorrectAnswers).toBe(1)
      expect(result.current.stats.accuracy).toBe(0)
    })

    it('应该正确计算正确率', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
        result.current.recordAnswer(false)
      })

      expect(result.current.stats.totalQuestions).toBe(3)
      expect(result.current.stats.correctAnswers).toBe(2)
      expect(result.current.stats.accuracy).toBeCloseTo(66.67, 1)
    })
  })

  describe('连续答对计数 (T025)', () => {
    it('答对应该增加连续答对', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
      })

      expect(result.current.stats.currentStreak).toBe(3)
    })

    it('答错应该重置连续答对', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
        result.current.recordAnswer(false)
      })

      expect(result.current.stats.currentStreak).toBe(0)
    })

    it('应该更新最长连续答对', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
      })

      expect(result.current.stats.currentStreak).toBe(5)
      expect(result.current.stats.longestStreak).toBe(5)
    })

    it('最长连续答对应该保留历史最大值', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        // 先连续答对 5 题
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)

        // 答错一题，重置
        result.current.recordAnswer(false)

        // 再连续答对 3 题
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
      })

      expect(result.current.stats.currentStreak).toBe(3)
      expect(result.current.stats.longestStreak).toBe(5) // 保留历史最大值
    })

    it('应该支持手动重置连续答对', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
      })

      expect(result.current.stats.currentStreak).toBe(3)

      act(() => {
        result.current.resetStreak()
      })

      expect(result.current.stats.currentStreak).toBe(0)
    })
  })

  describe('成就解锁 (T026)', () => {
    it('应该在首次答对时解锁成就', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.recordAnswer(true)
      })

      const achievements = result.current.achievements
      const firstCorrect = achievements.find(a => a.id === 'first-correct')

      expect(firstCorrect).toBeDefined()
      expect(firstCorrect?.name).toBe('第一次答对！')
    })

    it('应该在连续答对 3 题时解锁三连胜成就', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
      })

      const achievements = result.current.achievements
      const streak3 = achievements.find(a => a.id === 'streak-3')

      expect(streak3).toBeDefined()
      expect(streak3?.name).toBe('三连胜！')
    })

    it('应该在连续答对 5 题时解锁五连胜成就', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        for (let i = 0; i < 5; i++) {
          result.current.recordAnswer(true)
        }
      })

      const achievements = result.current.achievements
      const streak5 = achievements.find(a => a.id === 'streak-5')

      expect(streak5).toBeDefined()
      expect(streak5?.name).toBe('五连胜！')
    })

    it('应该在连续答对 10 题时解锁十连胜王者成就', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        for (let i = 0; i < 10; i++) {
          result.current.recordAnswer(true)
        }
      })

      const achievements = result.current.achievements
      const streak10 = achievements.find(a => a.id === 'streak-10')

      expect(streak10).toBeDefined()
      expect(streak10?.name).toBe('十连胜王者！')
    })

    it('应该在正确率达到 80% 时解锁优秀学员成就（至少5题）', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        // 5 题：4 对 1 错 = 80%
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
        result.current.recordAnswer(false)
      })

      const achievements = result.current.achievements
      const accuracy80 = achievements.find(a => a.id === 'accuracy-80')

      expect(accuracy80).toBeDefined()
      expect(accuracy80?.name).toBe('优秀学员')
    })

    it('应该在完成 10 题时解锁勤奋学习成就', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        for (let i = 0; i < 10; i++) {
          result.current.recordAnswer(true)
        }
      })

      const achievements = result.current.achievements
      const questions10 = achievements.find(a => a.id === 'questions-10')

      expect(questions10).toBeDefined()
      expect(questions10?.name).toBe('勤奋学习')
    })

    it('不应该重复解锁已解锁的成就', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        // 先连续答对 10 题，解锁所有连续成就
        for (let i = 0; i < 10; i++) {
          result.current.recordAnswer(true)
        }
      })

      const firstCount = result.current.achievements.length
      const firstIds = new Set(result.current.achievements.map(a => a.id))

      act(() => {
        // 再答 10 题，应该没有重复成就
        for (let i = 0; i < 10; i++) {
          result.current.recordAnswer(true)
        }
      })

      const secondCount = result.current.achievements.length
      const secondIds = result.current.achievements.map(a => a.id)

      // 验证：每个成就 ID 都是唯一的，没有重复
      const uniqueIds = new Set(secondIds)
      expect(uniqueIds.size).toBe(secondIds.length) // 所有 ID 都是唯一的
      expect(secondCount).toBe(firstCount) // 没有新成就（因为都已解锁）
    })

    it('答错应该清除连续答对，但保留已解锁的连续成就', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        // 连续答对 5 题
        for (let i = 0; i < 5; i++) {
          result.current.recordAnswer(true)
        }
      })

      const streak5Count = result.current.achievements.length

      act(() => {
        // 答错一题
        result.current.recordAnswer(false)
      })

      // 连续答对应该重置
      expect(result.current.stats.currentStreak).toBe(0)

      // 但成就数量不应该减少
      expect(result.current.achievements.length).toBeGreaterThanOrEqual(streak5Count)

      // 五连胜成就应该仍然存在
      const streak5 = result.current.achievements.find(a => a.id === 'streak-5')
      expect(streak5).toBeDefined()
    })
  })

  describe('成就状态管理', () => {
    it('应该正确标记成就为已显示', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.recordAnswer(true)
      })

      const achievement = result.current.achievements[0]
      expect(achievement.shown).toBe(false)

      act(() => {
        result.current.markAchievementShown(achievement.id)
      })

      const updated = result.current.achievements.find(a => a.id === achievement.id)
      expect(updated?.shown).toBe(true)
    })

    it('hasAchievement 应该正确检查成就状态', () => {
      const { result } = renderHook(() => useSessionStore())

      expect(result.current.hasAchievement('first-correct')).toBe(false)

      act(() => {
        result.current.recordAnswer(true)
      })

      expect(result.current.hasAchievement('first-correct')).toBe(true)
    })

    it('应该支持重置成就（测试用）', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
        result.current.recordAnswer(true)
      })

      expect(result.current.achievements.length).toBeGreaterThan(0)

      act(() => {
        result.current.resetAchievements()
      })

      expect(result.current.achievements).toHaveLength(0)
      expect(result.current.unlockedAchievements).toHaveLength(0)
    })
  })

  describe('学习时长统计', () => {
    it('应该正确增加学习时长', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.incrementStudyTime(60) // 1 分钟
      })

      expect(result.current.stats.todayStudyTime).toBe(60)
    })

    it('应该累加学习时长', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.incrementStudyTime(60)
        result.current.incrementStudyTime(120)
        result.current.incrementStudyTime(180)
      })

      expect(result.current.stats.todayStudyTime).toBe(360)
    })

    it('记录答题时应该更新最后学习时间', () => {
      const { result } = renderHook(() => useSessionStore())

      const beforeTime = result.current.stats.lastStudyTime

      act(() => {
        result.current.recordAnswer(true)
      })

      const afterTime = result.current.stats.lastStudyTime

      expect(afterTime).not.toBe(beforeTime)
      expect(afterTime).toBeTruthy()
    })
  })

  describe('会话管理', () => {
    it('应该正确设置会话信息', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.setSession({
          session_id: 'test-session',
          student_id: 'student-123',
          subject: '数学',
          student_age: 7,
          is_valid: true,
        })
      })

      expect(result.current.sessionId).toBe('test-session')
      expect(result.current.studentId).toBe('student-123')
      expect(result.current.isValid).toBe(true)
    })

    it('清除会话时应该保留学习统计和成就', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        // 先设置一些学习数据
        result.current.setSession({
          session_id: 'test-session',
          student_id: 'student-123',
          subject: '数学',
          student_age: 7,
          is_valid: true,
        })
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

  describe('消息管理', () => {
    it('应该正确添加用户消息', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.addMessage('user', '你好，小芽')
      })

      expect(result.current.messages).toHaveLength(1)
      expect(result.current.messages[0]).toMatchObject({
        role: 'user',
        content: '你好，小芽',
      })
      expect(result.current.messages[0].timestamp).toBeTruthy()
    })

    it('应该正确添加助手消息', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.addMessage('assistant', '你好！我是小芽')
      })

      expect(result.current.messages).toHaveLength(1)
      expect(result.current.messages[0]).toMatchObject({
        role: 'assistant',
        content: '你好！我是小芽',
      })
    })

    it('应该按时间顺序保留消息历史', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.addMessage('user', '第一句话')
        result.current.addMessage('assistant', '第二句话')
        result.current.addMessage('user', '第三句话')
      })

      expect(result.current.messages).toHaveLength(3)
      expect(result.current.messages[0].content).toBe('第一句话')
      expect(result.current.messages[1].content).toBe('第二句话')
      expect(result.current.messages[2].content).toBe('第三句话')
    })
  })

  describe('UI 状态管理', () => {
    it('应该正确设置加载状态', () => {
      const { result } = renderHook(() => useSessionStore())

      expect(result.current.isLoading).toBe(false)

      act(() => {
        result.current.setLoading(true)
      })

      expect(result.current.isLoading).toBe(true)
    })

    it('应该正确设置错误信息', () => {
      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.setError('网络错误')
      })

      expect(result.current.error).toBe('网络错误')

      act(() => {
        result.current.setError(null)
      })

      expect(result.current.error).toBeNull()
    })
  })
})
