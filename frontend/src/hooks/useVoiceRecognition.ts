/**
 * useVoiceRecognition Hook
 * 封装 Web Speech API，提供语音识别功能
 *
 * 功能特性：
 * - 支持中文语音识别
 * - 自动处理临时结果和最终结果
 * - 友好的错误提示（适合儿童）
 * - 自动停止检测
 * - 组件卸载时自动清理
 */

import { useState, useCallback, useEffect, useRef } from 'react';

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface UseVoiceRecognitionReturn {
  /** 是否正在监听语音 */
  isListening: boolean;
  /** 最终识别文本 */
  transcript: string;
  /** 临时识别文本 */
  interimTranscript: string;
  /** 浏览器是否支持语音识别 */
  isSupported: boolean;
  /** 错误信息（中文） */
  error: string | null;
  /** 开始监听 */
  startListening: () => boolean;
  /** 停止监听 */
  stopListening: () => void;
  /** 重置识别文本 */
  resetTranscript: () => void;
}

interface SpeechRecognition extends EventTarget {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  maxAlternatives: number;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onstart: ((event: Event) => void) | null;
  onend: ((event: Event) => void) | null;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
}

declare global {
  interface Window {
    SpeechRecognition: {
      new (): SpeechRecognition;
    };
    webkitSpeechRecognition: {
      new (): SpeechRecognition;
    };
  }
}

/**
 * 友好的错误消息映射
 */
const ERROR_MESSAGES: Record<string, string> = {
  'no-speech': '没有检测到语音，请再试一次',
  'audio-capture': '无法访问麦克风',
  'not-allowed': '需要麦克风权限才能使用语音功能',
  'network': '网络连接有问题，请检查网络',
  'aborted': '语音识别已停止',
  'default': '语音识别遇到问题，请再试一次',
};

function useVoiceRecognition(
  lang: string = 'zh-CN'
): UseVoiceRecognitionReturn {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  // 检查浏览器支持
  const isSupported = typeof window !== 'undefined' &&
    // @ts-ignore - webkitSpeechRecognition may not exist in all browsers
    !!(window.SpeechRecognition || window.webkitSpeechRecognition);

  /**
   * 初始化 SpeechRecognition 实例
   */
  useEffect(() => {
    if (!isSupported) return;

    // @ts-ignore
    const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognitionAPI();

    recognition.lang = lang;
    recognition.continuous = false; // 不持续监听，自动停止
    recognition.interimResults = true; // 返回临时结果
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.onresult = (event: any) => {
      let finalTranscript = '';
      let interimTranscriptText = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const transcript = result[0].transcript;

        if (result.isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscriptText += transcript;
        }
      }

      if (finalTranscript) {
        setTranscript(finalTranscript);
        setInterimTranscript('');
      } else {
        setInterimTranscript(interimTranscriptText);
      }
    };

    recognition.onerror = (event: any) => {
      const errorMessage = ERROR_MESSAGES[event.error] || ERROR_MESSAGES.default;
      setError(errorMessage);
      setIsListening(false);

      console.error('Speech recognition error:', event.error, event.message);
    };

    recognitionRef.current = recognition;

    return () => {
      recognition.abort();
    };
  }, [isSupported, lang]);

  /**
   * 开始监听语音
   */
  const startListening = useCallback(() => {
    if (!isSupported) {
      setError('语音识别不支持');
      return false;
    }

    if (isListening || !recognitionRef.current) {
      return false;
    }

    try {
      setIsListening(true);
      setError(null);
      recognitionRef.current.start();
      return true;
    } catch (err) {
      console.error('Failed to start speech recognition:', err);
      setError('无法启动语音识别');
      setIsListening(false);
      return false;
    }
  }, [isSupported, isListening]);

  /**
   * 停止监听语音
   */
  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  }, [isListening]);

  /**
   * 重置识别文本
   */
  const resetTranscript = useCallback(() => {
    setTranscript('');
    setInterimTranscript('');
    setError(null);
  }, []);

  return {
    isListening,
    transcript,
    interimTranscript,
    isSupported,
    error,
    startListening,
    stopListening,
    resetTranscript,
  };
}

export default useVoiceRecognition;
