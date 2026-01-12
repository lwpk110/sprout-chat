/**
 * 会话状态管理
 * 使用 Zustand 管理会话和消息状态
 */

import { create } from 'zustand';
import type {
  SessionResponse,
  MessageResponse,
  ConversationResponse,
} from '../types';

interface SessionState {
  // 会话信息
  sessionId: string | null;
  studentId: string;
  subject: string;
  studentAge: number;
  isValid: boolean;

  // 消息历史
  messages: MessageResponse[];

  // UI 状态
  isLoading: boolean;
  error: string | null;

  // Actions
  setSession: (session: SessionResponse) => void;
  addMessage: (role: 'user' | 'assistant', content: string) => void;
  setMessages: (messages: MessageResponse[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearSession: () => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  // 初始状态
  sessionId: null,
  studentId: '',
  subject: '数学',
  studentAge: 6,
  isValid: false,
  messages: [],
  isLoading: false,
  error: null,

  // 设置会话
  setSession: (session) =>
    set({
      sessionId: session.session_id,
      studentId: session.student_id,
      subject: session.subject,
      studentAge: session.student_age,
      isValid: session.is_valid,
    }),

  // 添加消息
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

  // 设置消息列表
  setMessages: (messages) => set({ messages }),

  // 设置加载状态
  setLoading: (loading) => set({ isLoading: loading }),

  // 设置错误
  setError: (error) => set({ error }),

  // 清除会话
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
    }),
}));
