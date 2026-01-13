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
// 支持测试环境注入
declare const __API_BASE_URL__: string | undefined;
const getApiBaseUrl = (): string => {
  // 测试环境：检查全局配置
  if (typeof __API_BASE_URL__ !== 'undefined') {
    return __API_BASE_URL__;
  }
  // 默认值
  return '/api';
};

class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL?: string) {
    this.client = axios.create({
      baseURL: baseURL || getApiBaseUrl(),
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

  /**
   * 上传图片并获得引导式教学响应
   */
  async uploadImageForGuidance(
    file: File,
    studentId: string,
    studentAge: number = 6,
    subject: string = '数学'
  ): Promise<{
    success: boolean;
    data: {
      student_id: string;
      subject: string;
      response: string;
      image_size: number;
    };
  }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('student_id', studentId);
    formData.append('student_age', studentAge.toString());
    formData.append('subject', subject);

    const response = await this.client.post(
      '/v1/images/guide',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }
}

// 导出单例
export const apiClient = new ApiClient();
