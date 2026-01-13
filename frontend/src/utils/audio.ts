/**
 * Audio Utility Functions
 * 提供音频处理相关工具函数，包括音量检测、静音检测等
 *
 * 主要功能：
 * - 检测音频流的音量级别
 * - 检测静音（用于自动停止录音）
 * - 计算音频的 RMS (Root Mean Square) 值
 */

/**
 * 音量检测结果
 */
export interface VolumeLevel {
  /** 音量级别 (0.0 - 1.0) */
  level: number;
  /** 是否为静音 */
  isSilent: boolean;
  /** 分贝值 (approximate) */
  decibels: number;
}

/**
 * 静音检测器配置
 */
export interface SilenceDetectorOptions {
  /** 静音阈值 (0.0 - 1.0)，默认 0.02 */
  threshold?: number;
  /** 静音持续时间（毫秒），默认 3000ms */
  silenceDuration?: number;
  /** 检测间隔（毫秒），默认 100ms */
  checkInterval?: number;
  /** 检测到静音时的回调 */
  onSilenceDetected?: () => void;
  /** 音量变化时的回调 */
  onVolumeChange?: (level: VolumeLevel) => void;
}

/**
 * 静音检测器类
 *
 * 使用示例：
 * ```ts
 * const detector = new SilenceDetector({
 *   threshold: 0.02,
 *   silenceDuration: 3000,
 *   onSilenceDetected: () => console.log('检测到静音'),
 *   onVolumeChange: (level) => console.log('音量:', level.level)
 * });
 *
 * // 开始检测
 * await detector.start(stream);
 *
 * // 停止检测
 * detector.stop();
 * ```
 */
export class SilenceDetector {
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private microphone: MediaStreamAudioSourceNode | null = null;
  private dataArray: Float32Array | null = null;
  private animationFrameId: number | null = null;
  private silenceStartTime: number | null = null;
  private isRunning: boolean = false;

  private readonly threshold: number;
  private readonly silenceDuration: number;
  private readonly checkInterval: number;
  private readonly onSilenceDetected?: () => void;
  private readonly onVolumeChange?: (level: VolumeLevel) => void;
  private lastCheckTime: number = 0;

  constructor(options: SilenceDetectorOptions = {}) {
    this.threshold = options.threshold ?? 0.02;
    this.silenceDuration = options.silenceDuration ?? 3000;
    this.checkInterval = options.checkInterval ?? 100;
    this.onSilenceDetected = options.onSilenceDetected;
    this.onVolumeChange = options.onVolumeChange;
  }

  /**
   * 开始检测静音
   * @param stream 音频流（通常是来自麦克风的 MediaStream）
   */
  async start(stream: MediaStream): Promise<void> {
    if (this.isRunning) {
      console.warn('SilenceDetector is already running');
      return;
    }

    try {
      // 创建 AudioContext
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
      this.audioContext = new AudioContextClass();

      // 创建分析器
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;
      this.analyser.smoothingTimeConstant = 0.8;

      // 连接麦克风
      this.microphone = this.audioContext.createMediaStreamSource(stream);
      this.microphone.connect(this.analyser);

      // 准备数据数组
      const bufferLength = this.analyser.frequencyBinCount;
      this.dataArray = new Float32Array(bufferLength);

      this.isRunning = true;
      this.silenceStartTime = null;
      this.lastCheckTime = Date.now();

      // 开始检测循环
      this.detect();

    } catch (error) {
      console.error('Failed to start SilenceDetector:', error);
      this.stop();
      throw error;
    }
  }

  /**
   * 停止检测
   */
  stop(): void {
    this.isRunning = false;

    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }

    if (this.microphone) {
      this.microphone.disconnect();
      this.microphone = null;
    }

    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
      this.audioContext = null;
    }

    this.analyser = null;
    this.dataArray = null;
    this.silenceStartTime = null;
  }

  /**
   * 检测循环
   */
  private detect = (): void => {
    if (!this.isRunning || !this.analyser || !this.dataArray) {
      return;
    }

    const now = Date.now();

    // 限制检测频率
    if (now - this.lastCheckTime < this.checkInterval) {
      this.animationFrameId = requestAnimationFrame(this.detect);
      return;
    }

    this.lastCheckTime = now;

    // 获取音频数据
    this.analyser.getFloatTimeDomainData(this.dataArray);

    // 计算 RMS (Root Mean Square) 音量
    const rms = this.calculateRMS(this.dataArray);
    const level = Math.min(rms * 10, 1.0); // 放大并限制在 0-1 之间
    const isSilent = level < this.threshold;

    // 计算分贝值 (近似)
    const decibels = rms > 0 ? 20 * Math.log10(rms) : -Infinity;

    const volumeLevel: VolumeLevel = {
      level,
      isSilent,
      decibels,
    };

    // 触发音量变化回调
    if (this.onVolumeChange) {
      this.onVolumeChange(volumeLevel);
    }

    // 检测静音
    if (isSilent) {
      if (this.silenceStartTime === null) {
        // 开始静音计时
        this.silenceStartTime = now;
      } else {
        // 检查静音持续时间
        const silenceDuration = now - this.silenceStartTime;
        if (silenceDuration >= this.silenceDuration) {
          // 触发静音检测回调
          if (this.onSilenceDetected) {
            this.onSilenceDetected();
          }
          this.silenceStartTime = null; // 重置，避免重复触发
        }
      }
    } else {
      // 有声音，重置静音计时
      this.silenceStartTime = null;
    }

    // 继续下一帧
    this.animationFrameId = requestAnimationFrame(this.detect);
  }

  /**
   * 计算 RMS (Root Mean Square) 音量
   * @param data 音频数据数组
   * @returns RMS 值
   */
  private calculateRMS(data: Float32Array): number {
    let sum = 0;
    for (let i = 0; i < data.length; i++) {
      sum += data[i] * data[i];
    }
    return Math.sqrt(sum / data.length);
  }

  /**
   * 重置静音计时器
   */
  resetSilenceTimer(): void {
    this.silenceStartTime = null;
  }

  /**
   * 获取当前状态
   */
  getStatus(): { isRunning: boolean; silenceTime: number | null } {
    let silenceTime: number | null = null;
    if (this.silenceStartTime !== null) {
      silenceTime = Date.now() - this.silenceStartTime;
    }

    return {
      isRunning: this.isRunning,
      silenceTime,
    };
  }
}

/**
 * 检测音频流的音量级别（一次性检测）
 * @param stream 音频流
 * @param duration 检测持续时间（毫秒），默认 100ms
 * @returns Promise<VolumeLevel> 音量级别
 */
export async function detectVolumeLevel(
  stream: MediaStream,
  duration: number = 100
): Promise<VolumeLevel> {
  return new Promise((resolve, reject) => {
    try {
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
      const audioContext = new AudioContextClass();

      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      analyser.smoothingTimeConstant = 0.8;

      const microphone = audioContext.createMediaStreamSource(stream);
      microphone.connect(analyser);

      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Float32Array(bufferLength);

      let startTime: number | null = null;

      const detect = () => {
        if (startTime === null) {
          startTime = Date.now();
        }

        analyser.getFloatTimeDomainData(dataArray);

        // 计算 RMS
        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i] * dataArray[i];
        }
        const rms = Math.sqrt(sum / dataArray.length);
        const level = Math.min(rms * 10, 1.0);
        const isSilent = level < 0.02;
        const decibels = rms > 0 ? 20 * Math.log10(rms) : -Infinity;

        const elapsed = Date.now() - startTime;

        if (elapsed >= duration) {
          // 清理
          microphone.disconnect();
          audioContext.close();

          resolve({
            level,
            isSilent,
            decibels,
          });
        } else {
          requestAnimationFrame(detect);
        }
      };

      detect();

    } catch (error) {
      reject(error);
    }
  });
}

/**
 * 检查浏览器是否支持 AudioContext
 * @returns boolean 是否支持
 */
export function isAudioContextSupported(): boolean {
  return typeof window !== 'undefined' &&
    (window.AudioContext || (window as any).webkitAudioContext);
}

/**
 * 请求麦克风权限并获取音频流
 * @param constraints 媒体约束，默认要求音频
 * @returns Promise<MediaStream> 音频流
 */
export async function getMicrophoneStream(
  constraints: MediaStreamConstraints = { audio: true }
): Promise<MediaStream> {
  try {
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    return stream;
  } catch (error) {
    console.error('Failed to get microphone stream:', error);
    throw new Error('无法访问麦克风，请检查权限设置');
  }
}
