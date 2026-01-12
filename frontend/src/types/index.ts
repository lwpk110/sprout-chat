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
