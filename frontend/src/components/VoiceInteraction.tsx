/**
 * 语音交互组件（增强版）
 *
 * 功能特性：
 * - 集成 useVoiceRecognition Hook
 * - 友好的儿童错误提示
 * - 自动重试机制
 * - 可选的 SilenceDetector（3秒静音自动停止）
 * - 语音动画效果
 * - 实时音量显示
 */

import { useState, useCallback, useRef, useEffect } from 'react'
import type { VoiceInteractionProps } from '../types'
import { apiClient } from '../services/api'
import { useSessionStore } from '../store/sessionStore'
import useVoiceRecognition from '../hooks/useVoiceRecognition'
import { SilenceDetector, type VolumeLevel } from '../utils/audio'

interface VoiceInteractionState {
  /** 是否正在发送消息 */
  isSending: boolean
  /** 重试次数 */
  retryCount: number
  /** 是否显示重试按钮 */
  showRetry: boolean
  /** 待重试的消息 */
  pendingMessage: string
  /** 错误类型 */
  errorType: 'network' | 'recognition' | 'permission' | 'unknown' | null
}

const MAX_RETRIES = 3
const RETRY_DELAY = 2000 // 2秒后自动重试

export default function VoiceInteraction({
  sessionId,
  onMessageSent,
  isLoading,
}: VoiceInteractionProps) {
  const {
    isListening,
    transcript,
    interimTranscript,
    isSupported,
    error: recognitionError,
    startListening,
    stopListening,
    resetTranscript,
  } = useVoiceRecognition('zh-CN')

  const [state, setState] = useState<VoiceInteractionState>({
    isSending: false,
    retryCount: 0,
    showRetry: false,
    pendingMessage: '',
    errorType: null,
  })

  const [volumeLevel, setVolumeLevel] = useState<VolumeLevel | null>(null)
  const [useSilenceDetection, setUseSilenceDetection] = useState(false)

  const silenceDetectorRef = useRef<SilenceDetector | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const retryTimerRef = useRef<NodeJS.Timeout | null>(null)
  const { addMessage, setError } = useSessionStore()

  /**
   * 清理定时器
   */
  useEffect(() => {
    return () => {
      if (retryTimerRef.current) {
        clearTimeout(retryTimerRef.current)
      }
    }
  }, [])

  /**
   * 更新状态辅助函数
   */
  const updateState = useCallback((updates: Partial<VoiceInteractionState>) => {
    setState(prev => ({ ...prev, ...updates }))
  }, [])

  /**
   * 处理语音识别错误
   */
  useEffect(() => {
    if (recognitionError) {
      // 错误类型分类
      let errorType: VoiceInteractionState['errorType'] = 'unknown'

      if (recognitionError.includes('permission') || recognitionError.includes('权限')) {
        errorType = 'permission'
      } else if (recognitionError.includes('网络')) {
        errorType = 'network'
      } else if (recognitionError.includes('语音') || recognitionError.includes('识别')) {
        errorType = 'recognition'
      }

      updateState({ errorType, showRetry: errorType === 'network' || errorType === 'recognition' })

      // 设置全局错误（用于显示 Toast 或 Alert）
      setError(recognitionError)
    }
  }, [recognitionError, updateState, setError])

  /**
   * 开始语音识别
   */
  const handleStartListening = useCallback(async () => {
    if (!isSupported) {
      setError('你的浏览器不支持语音识别')
      return
    }

    // 清空之前的状态
    resetTranscript()
    updateState({
      isSending: false,
      showRetry: false,
      errorType: null,
      pendingMessage: '',
    })

    // 启动语音识别
    const started = startListening()

    if (!started) {
      setError('无法启动语音识别')
      return
    }

    // 如果启用了静音检测，启动 SilenceDetector
    if (useSilenceDetection) {
      try {
        // 获取麦克风流
        if (!streamRef.current) {
          streamRef.current = await navigator.mediaDevices.getUserMedia({ audio: true })
        }

        // 创建并启动静音检测器
        silenceDetectorRef.current = new SilenceDetector({
          threshold: 0.02,
          silenceDuration: 3000, // 3秒
          onSilenceDetected: () => {
            // 检测到静音，自动停止
            if (isListening) {
              handleStopListening()
            }
          },
          onVolumeChange: (level) => {
            setVolumeLevel(level)
          },
        })

        await silenceDetectorRef.current.start(streamRef.current)
      } catch (error) {
        console.error('Failed to start silence detection:', error)
        // 静音检测失败不影响语音识别
        setUseSilenceDetection(false)
      }
    }
  }, [
    isSupported,
    startListening,
    resetTranscript,
    updateState,
    useSilenceDetection,
    isListening,
    setError,
  ])

  /**
   * 停止语音识别并发送消息
   */
  const handleStopListening = useCallback(async () => {
    if (!isListening) return

    // 停止语音识别
    stopListening()

    // 停止静音检测
    if (silenceDetectorRef.current) {
      silenceDetectorRef.current.stop()
      silenceDetectorRef.current = null
    }

    // 等待最终识别结果
    setTimeout(async () => {
      const message = transcript.trim()

      if (message) {
        await sendMessage(message)
      } else {
        // 没有识别到文本
        setError('没有听到声音，请再试一次')
      }
    }, 500)
  }, [isListening, stopListening, transcript, setError])

  /**
   * 发送消息到后端
   */
  const sendMessage = useCallback(async (message: string) => {
    updateState({ isSending: true, pendingMessage: message })

    try {
      // 添加用户消息到会话
      addMessage('user', message)

      // 发送到后端 API
      const response = await apiClient.sendVoiceInput({
        session_id: sessionId,
        transcript: message,
      })

      // 添加助手响应
      addMessage('assistant', response.response)

      // 通知父组件
      onMessageSent(message)

      // 清空输入
      resetTranscript()
      updateState({
        isSending: false,
        retryCount: 0,
        showRetry: false,
        pendingMessage: '',
        errorType: null,
      })
    } catch (err) {
      console.error('发送语音失败:', err)

      const isRetryable = state.retryCount < MAX_RETRIES

      updateState({
        isSending: false,
        showRetry: isRetryable,
        errorType: 'network',
      })

      setError('发送消息失败，请重试')

      // 自动重试（仅在可重试时）
      if (isRetryable) {
        updateState({ retryCount: state.retryCount + 1 })

        retryTimerRef.current = setTimeout(() => {
          handleRetry()
        }, RETRY_DELAY)
      }
    }
  }, [
    sessionId,
    addMessage,
    onMessageSent,
    resetTranscript,
    updateState,
    state.retryCount,
    setError,
  ])

  /**
   * 重试发送消息
   */
  const handleRetry = useCallback(async () => {
    if (!state.pendingMessage) return

    // 清除定时器
    if (retryTimerRef.current) {
      clearTimeout(retryTimerRef.current)
      retryTimerRef.current = null
    }

    await sendMessage(state.pendingMessage)
  }, [state.pendingMessage, sendMessage])

  /**
   * 取消重试
   */
  const handleCancelRetry = useCallback(() => {
    if (retryTimerRef.current) {
      clearTimeout(retryTimerRef.current)
      retryTimerRef.current = null
    }

    updateState({
      showRetry: false,
      pendingMessage: '',
      errorType: null,
    })
  }, [updateState])

  /**
   * 获取儿童友好的错误消息
   */
  const getFriendlyErrorMessage = (): string => {
    if (!recognitionError && !state.errorType) return ''

    if (state.errorType === 'permission') {
      return '😅 需要麦克风权限才能说话哦'
    }

    if (state.errorType === 'network') {
      return `📡 网络有点问题... ${state.showRetry ? '要不要再试一次？' : ''}`
    }

    if (state.errorType === 'recognition') {
      return '👂 没听清楚，能再说一次吗？'
    }

    return recognitionError || '出了一点小问题'
  }

  const errorMessage = getFriendlyErrorMessage()
  const disabled = isLoading || state.isSending

  return (
    <div className="card-sprout">
      {/* 标题 */}
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-sprout-800 mb-2">
          🎤 语音对话
        </h2>
        <p className="text-lg text-sprout-600">
          点击麦克风，对小芽说话
        </p>
      </div>

      {/* 错误提示 */}
      {errorMessage && (
        <div className="mb-6 p-4 bg-red-50 rounded-2xl border-2 border-red-200">
          <div className="flex items-start gap-3">
            <div className="text-3xl">⚠️</div>
            <div className="flex-1">
              <div className="text-lg font-semibold text-red-800 mb-2">
                {errorMessage}
              </div>
              {state.showRetry && (
                <div className="flex gap-2">
                  <button
                    onClick={handleRetry}
                    disabled={state.isSending}
                    className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white font-bold rounded-xl transition-colors disabled:opacity-50"
                  >
                    {state.isSending ? '重试中...' : '重试'}
                  </button>
                  <button
                    onClick={handleCancelRetry}
                    disabled={state.isSending}
                    className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold rounded-xl transition-colors disabled:opacity-50"
                  >
                    取消
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 实时识别结果显示 */}
      {(transcript || interimTranscript) && (
        <div className="mb-6 p-4 bg-sprout-50 rounded-2xl border-2 border-sprout-200">
          <div className="text-sm text-sprout-500 mb-2">你说：</div>
          <div className="text-xl font-semibold text-sprout-800">
            {transcript}
            <span className="text-sprout-400">{interimTranscript}</span>
          </div>

          {/* 音量指示器 */}
          {volumeLevel && isListening && (
            <div className="mt-3">
              <div className="flex items-center gap-2">
                <div className="text-xs text-sprout-500">音量：</div>
                <div className="flex-1 h-2 bg-sprout-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-sprout-500 transition-all duration-100"
                    style={{ width: `${volumeLevel.level * 100}%` }}
                  />
                </div>
                <div className="text-xs text-sprout-600">
                  {Math.round(volumeLevel.level * 100)}%
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 麦克风按钮 */}
      <div className="flex justify-center">
        {!isListening ? (
          <button
            onClick={handleStartListening}
            disabled={disabled}
            className={`
              w-32 h-32 rounded-full shadow-2xl
              bg-gradient-to-br from-sprout-400 to-sprout-600
              hover:from-sprout-500 hover:to-sprout-700
              active:scale-95 transition-all duration-200
              flex items-center justify-center
              disabled:opacity-50 disabled:cursor-not-allowed
              ${isListening ? 'animate-pulse-glow' : 'hover:scale-105'}
            `}
          >
            <svg
              className="w-16 h-16 text-white"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
              <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
            </svg>
          </button>
        ) : (
          <button
            onClick={handleStopListening}
            className="
              w-32 h-32 rounded-full shadow-2xl
              bg-gradient-to-br from-red-400 to-red-600
              hover:from-red-500 hover:to-red-700
              active:scale-95 transition-all duration-200
              flex items-center justify-center
              animate-pulse-glow hover:scale-105
            "
          >
            <svg
              className="w-16 h-16 text-white"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M6 6h12v12H6z" />
            </svg>
          </button>
        )}
      </div>

      {/* 提示文字 */}
      <div className="mt-6 text-center">
        {state.isSending ? (
          <div className="text-lg text-sprout-700 font-semibold animate-pulse">
            📤 发送中...
          </div>
        ) : isListening ? (
          <div className="text-lg text-sprout-700 font-semibold animate-pulse">
            🔴 正在听你说话...
          </div>
        ) : (
          <div className="text-lg text-sprout-600">
            点击开始说话
          </div>
        )}
      </div>

      {/* 静音检测开关（开发/测试用） */}
      {process.env.NODE_ENV === 'development' && (
        <div className="mt-4 text-center">
          <label className="inline-flex items-center gap-2 text-sm text-sprout-600">
            <input
              type="checkbox"
              checked={useSilenceDetection}
              onChange={(e) => setUseSilenceDetection(e.target.checked)}
              className="rounded"
            />
            启用静音检测（3秒自动停止）
          </label>
        </div>
      )}
    </div>
  )
}
