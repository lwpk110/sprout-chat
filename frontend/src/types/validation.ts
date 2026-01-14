/**
 * Zod Validation Schemas
 * 使用 Zod 进行运行时类型验证
 */

import { z } from 'zod';

/**
 * Message Schema - 对话消息验证
 */
export const MessageSchema = z.object({
  id: z.string().uuid(),
  timestamp: z.string().datetime(),
  role: z.enum(['user', 'assistant', 'system']),
  content: z.string().min(1).max(2000),
  input_type: z.enum(['voice', 'text', 'image']).optional(),
  image_url: z.string().url().optional(),
  response_type: z.enum(['guidance', 'encouragement', 'error', 'question']).optional(),
  is_correct: z.boolean().optional(),
  is_loading: z.boolean().optional(),
  confidence: z.number().min(0).max(1).optional(),
  error: z.string().optional(),
});

/**
 * Achievement Schema - 成就徽章验证
 */
export const AchievementSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1).max(50),
  description: z.string().min(1).max(200),
  icon: z.string(),
  unlock_condition: z.object({
    type: z.enum(['correct_streak', 'total_sessions', 'mastery_rate', 'custom']),
    target: z.number().positive(),
  }),
  unlocked_at: z.string().datetime().optional(),
  is_unlocked: z.boolean(),
  rarity: z.enum(['common', 'rare', 'epic', 'legendary']),
  category: z.enum(['learning', 'streak', 'mastery', 'special']),
});

/**
 * Mistake Schema - 错题记录验证
 */
export const MistakeSchema = z.object({
  id: z.string().min(1),
  session_id: z.string().min(1),
  timestamp: z.string().datetime(),
  question_type: z.enum(['voice', 'image', 'text']),
  question_content: z.string().min(1).max(1000),
  image_url: z.string().url().optional(),
  wrong_answer: z.string().max(500),
  correct_answer: z.string().max(500),
  error_reason: z.string().max(200),
  hint: z.string().max(500),
  is_corrected: z.boolean(),
  corrected_at: z.string().datetime().optional(),
  correction_attempts: z.number().int().min(0),
  knowledge_point: z.string().min(1),
  difficulty: z.enum(['easy', 'medium', 'hard']),
  reviewed: z.boolean(),
});

/**
 * OfflineQueueItem Schema - 离线队列项验证
 */
export const OfflineQueueItemSchema = z.object({
  id: z.string().uuid(),
  type: z.enum(['voice', 'text', 'image']),
  data: z.any(),  // 可以是任意请求数据
  timestamp: z.string().datetime(),
  retry_count: z.number().int().min(0).max(5),
});

/**
 * 类型导出
 */
export type Message = z.infer<typeof MessageSchema>;
export type Achievement = z.infer<typeof AchievementSchema>;
export type Mistake = z.infer<typeof MistakeSchema>;
export type OfflineQueueItem = z.infer<typeof OfflineQueueItemSchema>;
