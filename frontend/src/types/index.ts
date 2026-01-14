/**
 * 前端类型定义
 * 与后端 Schema 保持一致
 */

// ========== 请求类型 ==========

export interface CreateSessionRequest {
  student_id: string;
  subject?: string;
  student_age?: number;
  topic?: string;
}

export interface VoiceInputRequest {
  session_id: string;
  transcript: string;
  confidence?: number;
}

export interface TextInputRequest {
  session_id: string;
  content: string;
}

// ========== 响应类型 ==========

export interface SessionResponse {
  session_id: string;
  student_id: string;
  subject: string;
  student_age: number;
  created_at: string;
  is_valid: boolean;
}

export interface MessageResponse {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

export interface ConversationResponse {
  session_id: string;
  response: string;
  timestamp: string;
}

export interface HistoryResponse {
  session_id: string;
  messages: MessageResponse[];
  total_count: number;
}

export interface SessionStatsResponse {
  session_id: string;
  student_id: string;
  subject: string;
  message_count: number;
  duration_seconds: number;
  created_at: string;
  last_activity: string;
  is_valid: boolean;
}

export interface ErrorResponse {
  error: string;
  detail?: string;
  timestamp: string;
}

// ========== 组件 Props 类型 ==========

export interface VoiceInteractionProps {
  sessionId: string;
  onMessageSent: (message: string) => void;
  isLoading: boolean;
}

export interface PhotoInteractionProps {
  sessionId: string;
  onImageUploaded: (result: string) => void;
  isLoading: boolean;
}

export interface GuidedResponseProps {
  response: string;
  timestamp: string;
}

// ========== 学习进度类型 ==========

/**
 * 学习进度统计
 * 记录学生的学习进度和掌握情况
 */
export interface LearningProgress {
  // 实体标识
  student_id: string;
  subject: string;

  // 掌握情况
  total_knowledge_points: number;
  mastered_knowledge_points: number;
  mastery_rate: number;  // 掌握率 (0-1)

  // 学习统计
  total_sessions: number;
  total_questions: number;
  correct_questions: number;
  accuracy_rate: number;  // 正确率 (0-1)

  // 时间统计
  total_study_time: number;  // 总学习时长（秒）
  average_session_time: number;
  current_streak: number;  // 当前连续学习天数
  longest_streak: number;  // 最长连续学习天数

  // 最近活动
  last_session_date: string;
  last_session_id: string;

  // 元数据
  updated_at: string;
}

/**
 * 成就徽章
 * 表示学生解锁的成就
 */
export interface Achievement {
  // 实体标识
  id: string;
  name: string;
  description: string;
  icon: string;  // Emoji 或 URL

  // 解锁条件
  unlock_condition: {
    type: 'correct_streak' | 'total_sessions' | 'mastery_rate' | 'custom';
    target: number;
  };

  // 状态
  unlocked_at?: string;
  is_unlocked: boolean;

  // 显示
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  category: 'learning' | 'streak' | 'mastery' | 'special';
}

/**
 * 错题记录
 * 记录学生的错误题目和订正状态
 */
export interface Mistake {
  // 实体标识
  id: string;
  session_id: string;
  timestamp: string;

  // 题目信息
  question_type: 'voice' | 'image' | 'text';
  question_content: string;
  image_url?: string;

  // 错误分析
  wrong_answer: string;
  correct_answer: string;
  error_reason: string;
  hint: string;

  // 订正状态
  is_corrected: boolean;
  corrected_at?: string;
  correction_attempts: number;

  // 知识点
  knowledge_point: string;
  difficulty: 'easy' | 'medium' | 'hard';

  // 元数据
  reviewed: boolean;
}

/**
 * 离线队列项
 * 离线时保存的请求，网络恢复后重试
 */
export interface OfflineQueueItem {
  id: string;
  type: 'voice' | 'text' | 'image';
  data: any;
  timestamp: string;
  retry_count: number;
}
