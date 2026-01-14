/**
 * 会话状态管理（增强版）
 * 使用 Zustand 管理会话、消息、学习进度和成就状态
 *
 * 功能特性：
 * - 会话和消息管理
 * - 连续答对计数（streak）
 * - 成就解锁系统
 * - 学习统计追踪
 * - 持久化存储
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  SessionResponse,
  MessageResponse,
} from '../types';

/**
 * 成就类型定义
 */
export interface Achievement {
  /** 成就ID */
  id: string;
  /** 成就名称 */
  name: string;
  /** 成就描述 */
  description: string;
  /** 成就图标 */
  icon: string;
  /** 解锁时间 */
  unlockedAt: string;
  /** 是否已显示 */
  shown: boolean;
}

/**
 * 学习统计定义
 */
export interface LearningStats {
  /** 总答题数 */
  totalQuestions: number;
  /** 正确数 */
  correctAnswers: number;
  /** 错误数 */
  incorrectAnswers: number;
  /** 正确率 (0-100) */
  accuracy: number;
  /** 当前连续答对 */
  currentStreak: number;
  /** 最长连续答对 */
  longestStreak: number;
  /** 今日学习时长（秒） */
  todayStudyTime: number;
  /** 最后学习时间 */
  lastStudyTime: string | null;
}

/**
 * 会话状态定义
 */
interface SessionState {
  // ========== 会话信息 ==========
  sessionId: string | null;
  studentId: string;
  subject: string;
  studentAge: number;
  isValid: boolean;

  // ========== 消息历史 ==========
  messages: MessageResponse[];

  // ========== UI 状态 ==========
  isLoading: boolean;
  error: string | null;

  // ========== 学习统计 ==========
  stats: LearningStats;

  // ========== 成就系统 ==========
  achievements: Achievement[];
  unlockedAchievements: string[];

  // ========== 会话 Actions ==========
  setSession: (session: SessionResponse) => void;
  clearSession: () => void;

  // ========== 消息 Actions ==========
  addMessage: (role: 'user' | 'assistant', content: string) => void;
  setMessages: (messages: MessageResponse[]) => void;

  // ========== UI Actions ==========
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // ========== 学习统计 Actions ==========
  recordAnswer: (isCorrect: boolean) => void;
  resetStreak: () => void;
  incrementStudyTime: (seconds: number) => void;
  updateStats: (stats: Partial<LearningStats>) => void;

  // ========== 成就系统 Actions ==========
  unlockAchievement: (achievementId: string) => void;
  markAchievementShown: (achievementId: string) => void;
  hasAchievement: (achievementId: string) => boolean;
  resetAchievements: () => void;
}

/**
 * 成就定义配置
 */
const ACHIEVEMENT_DEFINITIONS: Record<string, Omit<Achievement, 'unlockedAt' | 'shown'>> = {
  'first-correct': {
    id: 'first-correct',
    name: '第一次答对！',
    description: '成功回答了第一个问题',
    icon: '🎉',
  },
  'streak-3': {
    id: 'streak-3',
    name: '三连胜！',
    description: '连续答对 3 道题',
    icon: '🔥',
  },
  'streak-5': {
    id: 'streak-5',
    name: '五连胜！',
    description: '连续答对 5 道题',
    icon: '⭐',
  },
  'streak-10': {
    id: 'streak-10',
    name: '十连胜王者！',
    description: '连续答对 10 道题',
    icon: '👑',
  },
  'accuracy-80': {
    id: 'accuracy-80',
    name: '优秀学员',
    description: '正确率达到 80%',
    icon: '💯',
  },
  'accuracy-90': {
    id: 'accuracy-90',
    name: '学霸模式',
    description: '正确率达到 90%',
    icon: '🏆',
  },
  'questions-10': {
    id: 'questions-10',
    name: '勤奋学习',
    description: '完成了 10 道题',
    icon: '📚',
  },
  'questions-50': {
    id: 'questions-50',
    name: '学习达人',
    description: '完成了 50 道题',
    icon: '🎓',
  },
};

/**
 * 创建会话 Store（带持久化）
 */
export const useSessionStore = create<SessionState>()(
  persist(
    (set, get) => ({
      // ========== 初始状态 ==========
      sessionId: null,
      studentId: '',
      subject: '数学',
      studentAge: 6,
      isValid: false,
      messages: [],
      isLoading: false,
      error: null,

      // 学习统计初始状态
      stats: {
        totalQuestions: 0,
        correctAnswers: 0,
        incorrectAnswers: 0,
        accuracy: 0,
        currentStreak: 0,
        longestStreak: 0,
        todayStudyTime: 0,
        lastStudyTime: null,
      },

      // 成就系统初始状态
      achievements: [],
      unlockedAchievements: [],

      // ========== 会话 Actions ==========

      /**
       * 设置会话信息
       */
      setSession: (session) =>
        set({
          sessionId: session.session_id,
          studentId: session.student_id,
          subject: session.subject,
          studentAge: session.student_age,
          isValid: session.is_valid,
        }),

      /**
       * 清除会话（保留学习统计和成就）
       */
      clearSession: () =>
        set({
          sessionId: null,
          studentId: '',
          subject: '数学',
          studentAge: 6,
          isValid: false,
          messages: [],
          isLoading: false,
          error: null,
          // 注意：不重置 stats 和 achievements
        }),

      // ========== 消息 Actions ==========

      /**
       * 添加消息
       */
      addMessage: (role, content) =>
        set((state) => ({
          messages: [
            ...state.messages,
            {
              role,
              content,
              timestamp: new Date().toISOString(),
            },
          ],
        })),

      /**
       * 设置消息列表
       */
      setMessages: (messages) => set({ messages }),

      // ========== UI Actions ==========

      /**
       * 设置加载状态
       */
      setLoading: (loading) => set({ isLoading: loading }),

      /**
       * 设置错误
       */
      setError: (error) => set({ error }),

      // ========== 学习统计 Actions ==========

      /**
       * 记录答题结果
       */
      recordAnswer: (isCorrect) =>
        set((state) => {
          const newTotal = state.stats.totalQuestions + 1;
          const newCorrect = isCorrect ? state.stats.correctAnswers + 1 : state.stats.correctAnswers;
          const newIncorrect = isCorrect ? state.stats.incorrectAnswers : state.stats.incorrectAnswers + 1;
          const newAccuracy = (newCorrect / newTotal) * 100;

          // 更新连续答对
          let newCurrentStreak = isCorrect ? state.stats.currentStreak + 1 : 0;
          let newLongestStreak = Math.max(state.stats.longestStreak, newCurrentStreak);

          const newStats: LearningStats = {
            totalQuestions: newTotal,
            correctAnswers: newCorrect,
            incorrectAnswers: newIncorrect,
            accuracy: newAccuracy,
            currentStreak: newCurrentStreak,
            longestStreak: newLongestStreak,
            todayStudyTime: state.stats.todayStudyTime,
            lastStudyTime: new Date().toISOString(),
          };

          // 检查成就解锁
          const newAchievements = checkAchievements(newStats, state.unlockedAchievements);

          return {
            stats: newStats,
            achievements: [...state.achievements, ...newAchievements],
            unlockedAchievements: [
              ...state.unlockedAchievements,
              ...newAchievements.map(a => a.id),
            ],
          };
        }),

      /**
       * 重置连续答对（答错时调用）
       */
      resetStreak: () =>
        set((state) => ({
          stats: {
            ...state.stats,
            currentStreak: 0,
          },
        })),

      /**
       * 增加学习时长
       */
      incrementStudyTime: (seconds) =>
        set((state) => ({
          stats: {
            ...state.stats,
            todayStudyTime: state.stats.todayStudyTime + seconds,
          },
        })),

      /**
       * 更新学习统计
       */
      updateStats: (updates) =>
        set((state) => ({
          stats: {
            ...state.stats,
            ...updates,
          },
        })),

      // ========== 成就系统 Actions ==========

      /**
       * 解锁成就
       */
      unlockAchievement: (achievementId) =>
        set((state) => {
          if (state.unlockedAchievements.includes(achievementId)) {
            return state;
          }

          const definition = ACHIEVEMENT_DEFINITIONS[achievementId];
          if (!definition) {
            console.warn(`Achievement ${achievementId} not defined`);
            return state;
          }

          const newAchievement: Achievement = {
            ...definition,
            unlockedAt: new Date().toISOString(),
            shown: false,
          };

          return {
            achievements: [...state.achievements, newAchievement],
            unlockedAchievements: [...state.unlockedAchievements, achievementId],
          };
        }),

      /**
       * 标记成就为已显示
       */
      markAchievementShown: (achievementId) =>
        set((state) => ({
          achievements: state.achievements.map((a) =>
            a.id === achievementId ? { ...a, shown: true } : a
          ),
        })),

      /**
       * 检查是否已解锁成就
       */
      hasAchievement: (achievementId) => {
        return get().unlockedAchievements.includes(achievementId);
      },

      /**
       * 重置成就（用于测试）
       */
      resetAchievements: () =>
        set({
          achievements: [],
          unlockedAchievements: [],
        }),
    }),
    {
      name: 'sprout-session-storage',
      // 只持久化学习统计和成就，不持久化会话和消息
      partialize: (state) => ({
        stats: state.stats,
        achievements: state.achievements,
        unlockedAchievements: state.unlockedAchievements,
      }),
    }
  )
);

/**
 * 检查成就解锁条件
 */
function checkAchievements(
  stats: LearningStats,
  unlocked: string[]
): Achievement[] {
  const newAchievements: Achievement[] = [];

  // 首次答对
  if (stats.correctAnswers >= 1 && !unlocked.includes('first-correct')) {
    newAchievements.push({
      ...ACHIEVEMENT_DEFINITIONS['first-correct'],
      unlockedAt: new Date().toISOString(),
      shown: false,
    });
  }

  // 连续答对成就
  if (stats.currentStreak >= 3 && !unlocked.includes('streak-3')) {
    newAchievements.push({
      ...ACHIEVEMENT_DEFINITIONS['streak-3'],
      unlockedAt: new Date().toISOString(),
      shown: false,
    });
  }

  if (stats.currentStreak >= 5 && !unlocked.includes('streak-5')) {
    newAchievements.push({
      ...ACHIEVEMENT_DEFINITIONS['streak-5'],
      unlockedAt: new Date().toISOString(),
      shown: false,
    });
  }

  if (stats.currentStreak >= 10 && !unlocked.includes('streak-10')) {
    newAchievements.push({
      ...ACHIEVEMENT_DEFINITIONS['streak-10'],
      unlockedAt: new Date().toISOString(),
      shown: false,
    });
  }

  // 正确率成就
  if (stats.accuracy >= 80 && stats.totalQuestions >= 5 && !unlocked.includes('accuracy-80')) {
    newAchievements.push({
      ...ACHIEVEMENT_DEFINITIONS['accuracy-80'],
      unlockedAt: new Date().toISOString(),
      shown: false,
    });
  }

  if (stats.accuracy >= 90 && stats.totalQuestions >= 10 && !unlocked.includes('accuracy-90')) {
    newAchievements.push({
      ...ACHIEVEMENT_DEFINITIONS['accuracy-90'],
      unlockedAt: new Date().toISOString(),
      shown: false,
    });
  }

  // 答题数量成就
  if (stats.totalQuestions >= 10 && !unlocked.includes('questions-10')) {
    newAchievements.push({
      ...ACHIEVEMENT_DEFINITIONS['questions-10'],
      unlockedAt: new Date().toISOString(),
      shown: false,
    });
  }

  if (stats.totalQuestions >= 50 && !unlocked.includes('questions-50')) {
    newAchievements.push({
      ...ACHIEVEMENT_DEFINITIONS['questions-50'],
      unlockedAt: new Date().toISOString(),
      shown: false,
    });
  }

  return newAchievements;
}

/**
 * Hook: 获取未显示的成就
 */
export function useUnshownAchievements() {
  const achievements = useSessionStore((state) => state.achievements);
  const markShown = useSessionStore((state) => state.markAchievementShown);

  const unshown = achievements.filter((a) => !a.shown);

  const markAllAsShown = () => {
    unshown.forEach((a) => markShown(a.id));
  };

  return { unshown, markAllAsShown };
}
