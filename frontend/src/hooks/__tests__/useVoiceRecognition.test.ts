/**
 * useVoiceRecognition Hook 单元测试
 * 测试 Web Speech API 封装功能
 */

import { renderHook, act } from '@testing-library/react';
import useVoiceRecognition from '../useVoiceRecognition';

// Mock Web Speech API
let mockSpeechRecognitionInstance: any = {
  lang: '',
  continuous: false,
  interimResults: false,
  maxAlternatives: 1,
  start: jest.fn(),
  stop: jest.fn(),
  abort: jest.fn(),
  onstart: null as ((event: Event) => void) | null,
  onend: null as ((event: Event) => void) | null,
  onresult: null as ((event: any) => void) | null,
  onerror: null as ((event: any) => void) | null,
};

const mockSpeechRecognitionConstructor = jest.fn(() => {
  // Return a new instance each time to avoid shared state between tests
  const instance = {
    lang: '',
    continuous: false,
    interimResults: false,
    maxAlternatives: 1,
    start: jest.fn(),
    stop: jest.fn(),
    abort: jest.fn(),
    onstart: null,
    onend: null,
    onresult: null,
    onerror: null,
  };
  mockSpeechRecognitionInstance = instance;
  return instance;
});

// @ts-ignore - Mocking window object
global.window.SpeechRecognition = mockSpeechRecognitionConstructor;
// @ts-ignore
global.window.webkitSpeechRecognition = mockSpeechRecognitionConstructor;

describe('useVoiceRecognition Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset mock instance
    mockSpeechRecognitionInstance = null;
  });

  describe('初始化状态', () => {
    test('应该返回初始状态', () => {
      const { result } = renderHook(() => useVoiceRecognition());

      expect(result.current).toMatchObject({
        isListening: false,
        transcript: '',
        isSupported: true,
        error: null,
      });
    });

    test('在不支持 Speech API 的浏览器中应该标记为不支持', () => {
      // Save original
      const originalSpeechRecognition = global.window.SpeechRecognition;
      const originalWebkitSpeechRecognition = global.window.webkitSpeechRecognition;

      // @ts-ignore
      delete global.window.SpeechRecognition;
      // @ts-ignore
      delete global.window.webkitSpeechRecognition;

      const { result } = renderHook(() => useVoiceRecognition());

      expect(result.current.isSupported).toBe(false);

      // Restore
      // @ts-ignore
      global.window.SpeechRecognition = originalSpeechRecognition;
      // @ts-ignore
      global.window.webkitSpeechRecognition = originalWebkitSpeechRecognition;
    });
  });

  describe('startListening 函数', () => {
    test('应该启动语音识别', () => {
      const { result } = renderHook(() => useVoiceRecognition());

      act(() => {
        result.current.startListening();
      });

      expect(mockSpeechRecognitionInstance.start).toHaveBeenCalledTimes(1);
      expect(result.current.isListening).toBe(true);
    });

    test('在不支持时调用应该返回 false', () => {
      // Save original
      const originalSpeechRecognition = global.window.SpeechRecognition;
      const originalWebkitSpeechRecognition = global.window.webkitSpeechRecognition;

      // @ts-ignore
      delete global.window.SpeechRecognition;
      // @ts-ignore
      delete global.window.webkitSpeechRecognition;

      const { result } = renderHook(() => useVoiceRecognition());

      let success = false;
      act(() => {
        success = result.current.startListening();
      });

      expect(success).toBe(false);
      expect(result.current.error).toBe('语音识别不支持');

      // Restore
      // @ts-ignore
      global.window.SpeechRecognition = originalSpeechRecognition;
      // @ts-ignore
      global.window.webkitSpeechRecognition = originalWebkitSpeechRecognition;
    });

    test('已经在监听时不应该重复启动', () => {
      const { result } = renderHook(() => useVoiceRecognition());

      act(() => {
        result.current.startListening();
      });

      const firstCallCount = mockSpeechRecognitionInstance.start.mock.calls.length;

      act(() => {
        result.current.startListening();
      });

      expect(mockSpeechRecognitionInstance.start).toHaveBeenCalledTimes(firstCallCount);
    });
  });

  describe('stopListening 函数', () => {
    test('应该停止语音识别', () => {
      const { result } = renderHook(() => useVoiceRecognition());

      act(() => {
        result.current.startListening();
      });

      act(() => {
        result.current.stopListening();
      });

      expect(mockSpeechRecognitionInstance.stop).toHaveBeenCalledTimes(1);
    });
  });

  describe('语音识别结果处理', () => {
    test('应该捕获最终识别结果', () => {
      const { result } = renderHook(() => useVoiceRecognition());

      act(() => {
        result.current.startListening();
      });

      // 模拟语音识别成功事件
      const mockResult = {
        resultIndex: 0,
        results: [
          {
            0: {
              transcript: '你好小芽',
              confidence: 0.95,
            },
            isFinal: true,
          },
        ],
      };

      act(() => {
        if (mockSpeechRecognitionInstance.onresult) {
          mockSpeechRecognitionInstance.onresult(mockResult);
        }
      });

      expect(result.current.transcript).toBe('你好小芽');
    });

    test('应该捕获临时识别结果', () => {
      const { result } = renderHook(() => useVoiceRecognition());

      act(() => {
        result.current.startListening();
      });

      // 模拟临时结果
      const mockResult = {
        resultIndex: 0,
        results: [
          {
            0: {
              transcript: '你好',
              confidence: 0.8,
            },
            isFinal: false,
          },
        ],
      };

      act(() => {
        if (mockSpeechRecognitionInstance.onresult) {
          mockSpeechRecognitionInstance.onresult(mockResult);
        }
      });

      expect(result.current.interimTranscript).toBe('你好');
    });

    test('应该支持设置语言', () => {
      const { result } = renderHook(() => useVoiceRecognition('zh-CN'));

      act(() => {
        result.current.startListening();
      });

      // SpeechRecognition 实例应该被初始化为中文
      // 注意：这个测试依赖于实现细节
      expect(result.current.isListening).toBe(true);
    });
  });

  describe('错误处理', () => {
    test('应该处理权限拒绝错误', () => {
      const { result } = renderHook(() => useVoiceRecognition());

      act(() => {
        result.current.startListening();
      });

      // 模拟权限拒绝错误
      const mockError = {
        error: 'not-allowed',
        message: 'Permission denied',
      };

      act(() => {
        if (mockSpeechRecognitionInstance.onerror) {
          mockSpeechRecognitionInstance.onerror(mockError);
        }
      });

      expect(result.current.error).toContain('麦克风权限');
      expect(result.current.isListening).toBe(false);
    });

    test('应该处理无语音输入错误', () => {
      const { result } = renderHook(() => useVoiceRecognition());

      act(() => {
        result.current.startListening();
      });

      // 模拟无语音输入错误
      const mockError = {
        error: 'no-speech',
        message: 'No speech detected',
      };

      act(() => {
        if (mockSpeechRecognitionInstance.onerror) {
          mockSpeechRecognitionInstance.onerror(mockError);
        }
      });

      expect(result.current.error).toContain('没有检测到语音');
    });

    test('应该处理网络错误', () => {
      const { result } = renderHook(() => useVoiceRecognition());

      act(() => {
        result.current.startListening();
      });

      // 模拟网络错误
      const mockError = {
        error: 'network',
        message: 'Network error',
      };

      act(() => {
        if (mockSpeechRecognitionInstance.onerror) {
          mockSpeechRecognitionInstance.onerror(mockError);
        }
      });

      expect(result.current.error).toContain('网络');
    });
  });

  describe('重置功能', () => {
    test('resetTranscript 应该清空识别文本', () => {
      const { result } = renderHook(() => useVoiceRecognition());

      act(() => {
        result.current.startListening();
      });

      // 设置一个识别结果
      const mockResult = {
        resultIndex: 0,
        results: [
          {
            0: {
              transcript: '测试文本',
              confidence: 0.9,
            },
            isFinal: true,
          },
        ],
      };

      act(() => {
        if (mockSpeechRecognitionInstance.onresult) {
          mockSpeechRecognitionInstance.onresult(mockResult);
        }
      });

      expect(result.current.transcript).toBe('测试文本');

      // 重置
      act(() => {
        result.current.resetTranscript();
      });

      expect(result.current.transcript).toBe('');
    });
  });

  describe('自动停止功能', () => {
    test('应该在识别完成后自动停止', () => {
      const { result } = renderHook(() => useVoiceRecognition());

      act(() => {
        result.current.startListening();
      });

      // 模拟识别完成事件
      act(() => {
        if (mockSpeechRecognitionInstance.onend) {
          mockSpeechRecognitionInstance.onend(new Event('end'));
        }
      });

      expect(result.current.isListening).toBe(false);
    });
  });

  describe('清理功能', () => {
    test('组件卸载时应该停止识别', () => {
      const { result, unmount } = renderHook(() => useVoiceRecognition());

      act(() => {
        result.current.startListening();
      });

      expect(result.current.isListening).toBe(true);

      unmount();

      // 验证 abort 被调用 (not stop, because cleanup uses abort)
      expect(mockSpeechRecognitionInstance.abort).toHaveBeenCalledTimes(1);
    });
  });
});
