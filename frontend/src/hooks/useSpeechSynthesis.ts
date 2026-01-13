/**
 * useSpeechSynthesis Hook
 * 提供文本转语音 (TTS) 功能，用于语音播报 AI 助手的回复
 *
 * 功能特性：
 * - 支持中文语音播报
 * - 儿童友好的语音配置（语速、音调）
 * - 播放控制（播放、暂停、恢复、取消）
 * - 语音列表获取
 * - 播放状态管理
 * - 错误处理
 */

import { useState, useCallback, useEffect, useRef } from 'react';

interface SpeechSynthesisOptions {
  /** 语速 (0.1 - 10)，默认 0.9（稍慢，适合儿童） */
  rate?: number;
  /** 音调 (0 - 2)，默认 1.0（正常） */
  pitch?: number;
  /** 音量 (0 - 1)，默认 1.0（最大） */
  volume?: number;
  /** 语音语言，默认 'zh-CN' */
  lang?: string;
  /** 播放结束时的回调 */
  onEnd?: () => void;
  /** 播放出错时的回调 */
  onError?: (error: string) => void;
}

interface UseSpeechSynthesisReturn {
  /** 是否正在播放 */
  isSpeaking: boolean;
  /** 是否已暂停 */
  isPaused: boolean;
  /** 是否支持 TTS */
  isSupported: boolean;
  /** 当前播放的文本 */
  currentText: string;
  /** 可用语音列表 */
  voices: SpeechSynthesisVoice[];
  /** 播放文本 */
  speak: (text: string, options?: SpeechSynthesisOptions) => boolean;
  /** 暂停播放 */
  pause: () => void;
  /** 恢复播放 */
  resume: () => void;
  /** 取消播放 */
  cancel: () => void;
  /** 获取中文语音 */
  getChineseVoice: () => SpeechSynthesisVoice | null;
}

/**
 * useSpeechSynthesis Hook
 *
 * 使用示例：
 * ```tsx
 * const { isSpeaking, speak, cancel } = useSpeechSynthesis({
 *   rate: 0.9,
 *   pitch: 1.0,
 *   onEnd: () => console.log('播放结束'),
 * });
 *
 * // 播放语音
 * speak('你好，我是小芽老师！');
 *
 * // 停止播放
 * cancel();
 * ```
 */
function useSpeechSynthesis(
  defaultOptions: SpeechSynthesisOptions = {}
): UseSpeechSynthesisReturn {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [currentText, setCurrentText] = useState('');
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  // 默认选项
  const {
    rate = 0.9,          // 语速稍慢，适合儿童
    pitch = 1.0,         // 正常音调
    volume = 1.0,        // 最大音量
    lang = 'zh-CN',      // 中文
    onEnd,
    onError,
  } = defaultOptions;

  // 检查浏览器支持
  const isSupported = typeof window !== 'undefined' &&
    'speechSynthesis' in window &&
    'SpeechSynthesisUtterance' in window;

  /**
   * 加载可用语音列表
   */
  useEffect(() => {
    if (!isSupported) return;

    const loadVoices = () => {
      const availableVoices = window.speechSynthesis.getVoices();
      setVoices(availableVoices);
    };

    // 立即加载一次
    loadVoices();

    // 某些浏览器语音列表是异步加载的
    window.speechSynthesis.onvoiceschanged = loadVoices;

    return () => {
      window.speechSynthesis.onvoiceschanged = null;
    };
  }, [isSupported]);

  /**
   * 获取中文语音
   */
  const getChineseVoice = useCallback((): SpeechSynthesisVoice | null => {
    // 优先选择中文语音
    const chineseVoice = voices.find(voice =>
      voice.lang.startsWith('zh') || voice.lang.includes('CN')
    );

    // 如果没有中文语音，使用默认语音
    return chineseVoice || voices[0] || null;
  }, [voices]);

  /**
   * 播放文本
   */
  const speak = useCallback((text: string, options: SpeechSynthesisOptions = {}): boolean => {
    if (!isSupported) {
      console.error('Speech synthesis is not supported');
      return false;
    }

    if (!text || text.trim() === '') {
      console.warn('Cannot speak empty text');
      return false;
    }

    // 取消当前播放
    window.speechSynthesis.cancel();

    // 创建新的语音实例
    const utterance = new SpeechSynthesisUtterance(text);

    // 配置语音参数
    utterance.rate = options.rate ?? rate;
    utterance.pitch = options.pitch ?? pitch;
    utterance.volume = options.volume ?? volume;
    utterance.lang = options.lang ?? lang;

    // 设置中文语音
    const chineseVoice = getChineseVoice();
    if (chineseVoice) {
      utterance.voice = chineseVoice;
    }

    // 事件处理
    utterance.onstart = () => {
      setIsSpeaking(true);
      setIsPaused(false);
      setCurrentText(text);
    };

    utterance.onend = () => {
      setIsSpeaking(false);
      setIsPaused(false);
      setCurrentText('');
      utteranceRef.current = null;

      if (onEnd) {
        onEnd();
      }
    };

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event.error);

      setIsSpeaking(false);
      setIsPaused(false);
      setCurrentText('');
      utteranceRef.current = null;

      const errorMessage = getErrorMessage(event.error);
      if (onError) {
        onError(errorMessage);
      }
    };

    utterance.onpause = () => {
      setIsPaused(true);
    };

    utterance.onresume = () => {
      setIsPaused(false);
    };

    // 保存引用
    utteranceRef.current = utterance;

    // 开始播放
    window.speechSynthesis.speak(utterance);

    return true;
  }, [isSupported, rate, pitch, volume, lang, getChineseVoice, onEnd, onError]);

  /**
   * 暂停播放
   */
  const pause = useCallback(() => {
    if (isSpeaking && !isPaused) {
      window.speechSynthesis.pause();
    }
  }, [isSpeaking, isPaused]);

  /**
   * 恢复播放
   */
  const resume = useCallback(() => {
    if (isPaused) {
      window.speechSynthesis.resume();
    }
  }, [isPaused]);

  /**
   * 取消播放
   */
  const cancel = useCallback(() => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
    setIsPaused(false);
    setCurrentText('');
    utteranceRef.current = null;
  }, []);

  /**
   * 组件卸载时取消播放
   */
  useEffect(() => {
    return () => {
      cancel();
    };
  }, [cancel]);

  return {
    isSpeaking,
    isPaused,
    isSupported,
    currentText,
    voices,
    speak,
    pause,
    resume,
    cancel,
    getChineseVoice,
  };
}

/**
 * 获取友好的错误消息
 */
function getErrorMessage(error: string): string {
  const errorMessages: Record<string, string> = {
    'canceled': '语音播放已取消',
    'interrupted': '语音播放被打断',
    'audio-busy': '音频设备忙碌',
    'audio-hardware': '音频设备不可用',
    'network': '网络连接问题',
    'synthesis-unavailable': '语音合成不可用',
    'synthesis-failed': '语音合成失败',
    'language-unavailable': '该语言不支持',
    'voice-unavailable': '该语音不可用',
    'text-too-long': '文本太长',
  };

  return errorMessages[error] || `语音播放出现问题: ${error}`;
}

export default useSpeechSynthesis;
