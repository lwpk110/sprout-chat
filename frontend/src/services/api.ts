/**
 * API 服务层
 * 封装所有后端 API 调用
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  CreateSessionRequest,
  SessionResponse,
  VoiceInputRequest,
  TextInputRequest,
  ConversationResponse,
  HistoryResponse,
  SessionStatsResponse,
  ErrorResponse,
} from '../types';

// API 基础 URL（开发环境使用代理）
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.client.interceptors.response.use(
      (response) => {
        return response;
      },
      (error: AxiosError<ErrorResponse>) => {
        console.error('[API Error]', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  /**
   * 创建新的对话会话
   */
  async createSession(request: CreateSessionRequest): Promise<SessionResponse> {
    const response = await this.client.post<SessionResponse>(
      '/v1/conversations/create',
      request
    );
    return response.data;
  }

  /**
   * 处理语音输入
   */
  async sendVoiceInput(request: VoiceInputRequest): Promise<ConversationResponse> {
    const response = await this.client.post<ConversationResponse>(
      '/v1/conversations/voice',
      request
    );
    return response.data;
  }

  /**
   * 处理文字输入
   */
  async sendTextInput(request: TextInputRequest): Promise<ConversationResponse> {
    const response = await this.client.post<ConversationResponse>(
      '/v1/conversations/message',
      request
    );
    return response.data;
  }

  /**
   * 获取对话历史
   */
  async getHistory(sessionId: string, limit: number = 10): Promise<HistoryResponse> {
    const response = await this.client.get<HistoryResponse>(
      `/v1/conversations/${sessionId}/history`,
      { params: { limit } }
    );
    return response.data;
  }

  /**
   * 获取会话统计
   */
  async getSessionStats(sessionId: string): Promise<SessionStatsResponse> {
    const response = await this.client.get<SessionStatsResponse>(
      `/v1/conversations/${sessionId}/stats`
    );
    return response.data;
  }

  /**
   * 删除会话
   */
  async deleteSession(sessionId: string): Promise<{ message: string }> {
    const response = await this.client.delete<{ message: string }>(
      `/v1/conversations/${sessionId}`
    );
    return response.data;
  }
}

// 导出单例
export const apiClient = new ApiClient();
