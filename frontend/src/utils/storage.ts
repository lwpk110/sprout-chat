/**
 * localStorage 持久化工具
 * 提供类型安全的 localStorage 操作
 */

import type { SessionState, Message, Achievement, Mistake } from '../types';

const STORAGE_KEYS = {
  SESSION_STATE: 'sprout_session_state',
  MESSAGES: 'sprout_messages',
  ACHIEVEMENTS: 'sprout_achievements',
  MISTAKES: 'sprout_mistakes',
  OFFLINE_QUEUE: 'sprout_offline_queue',
  STUDENT_ID: 'sprout_student_id',
} as const;

/**
 * 通用存储函数
 */
function setItem<T>(key: string, value: T): boolean {
  try {
    const serialized = JSON.stringify(value);
    localStorage.setItem(key, serialized);
    return true;
  } catch (error) {
    console.error(`Failed to save ${key} to localStorage:`, error);
    return false;
  }
}

/**
 * 通用读取函数
 */
function getItem<T>(key: string, defaultValue: T): T {
  try {
    const item = localStorage.getItem(key);
    if (item === null) {
      return defaultValue;
    }
    return JSON.parse(item) as T;
  } catch (error) {
    console.error(`Failed to read ${key} from localStorage:`, error);
    return defaultValue;
  }
}

/**
 * 保存会话状态
 */
export function saveSessionState(state: SessionState): boolean {
  return setItem(STORAGE_KEYS.SESSION_STATE, state);
}

/**
 * 读取会话状态
 */
export function loadSessionState(): SessionState | null {
  return getItem<SessionState | null>(STORAGE_KEYS.SESSION_STATE, null);
}

/**
 * 清除会话状态
 */
export function clearSessionState(): void {
  localStorage.removeItem(STORAGE_KEYS.SESSION_STATE);
}

/**
 * 保存消息历史
 */
export function saveMessages(messages: Message[]): boolean {
  return setItem(STORAGE_KEYS.MESSAGES, messages);
}

/**
 * 读取消息历史
 */
export function loadMessages(): Message[] {
  return getItem<Message[]>(STORAGE_KEYS.MESSAGES, []);
}

/**
 * 添加单条消息
 */
export function addMessage(message: Message): boolean {
  const messages = loadMessages();
  messages.push(message);
  return saveMessages(messages);
}

/**
 * 清除消息历史
 */
export function clearMessages(): void {
  localStorage.removeItem(STORAGE_KEYS.MESSAGES);
}

/**
 * 保存成就列表
 */
export function saveAchievements(achievements: Achievement[]): boolean {
  return setItem(STORAGE_KEYS.ACHIEVEMENTS, achievements);
}

/**
 * 读取成就列表
 */
export function loadAchievements(): Achievement[] {
  return getItem<Achievement[]>(STORAGE_KEYS.ACHIEVEMENTS, []);
}

/**
 * 保存错题本
 */
export function saveMistakes(mistakes: Mistake[]): boolean {
  return setItem(STORAGE_KEYS.MISTAKES, mistakes);
}

/**
 * 读取错题本
 */
export function loadMistakes(): Mistake[] {
  return getItem<Mistake[]>(STORAGE_KEYS.MISTAKES, []);
}

/**
 * 保存学生ID
 */
export function saveStudentId(studentId: string): boolean {
  return setItem(STORAGE_KEYS.STUDENT_ID, studentId);
}

/**
 * 读取学生ID
 */
export function loadStudentId(): string | null {
  return getItem<string | null>(STORAGE_KEYS.STUDENT_ID, null);
}

/**
 * 清除所有数据
 * 用于"清除所有数据"功能
 */
export function clearAllData(): void {
  Object.values(STORAGE_KEYS).forEach(key => {
    localStorage.removeItem(key);
  });
}

/**
 * 获取存储使用情况
 * @returns 已用空间（字节）
 */
export function getStorageUsage(): number {
  let total = 0;
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key) {
      const value = localStorage.getItem(key);
      if (value) {
        total += key.length + value.length;
      }
    }
  }
  return total;
}

/**
 * 检查存储空间是否充足
 * @returns 是否有足够空间（假设5MB限制）
 */
export function hasEnoughSpace(estimatedSize: number): boolean {
  const usage = getStorageUsage();
  const LIMIT = 5 * 1024 * 1024; // 5MB
  return usage + estimatedSize < LIMIT;
}
