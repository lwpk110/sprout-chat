/**
 * 语音交互组件
 * 使用 Web Speech API 进行语音识别
 */

import { useState, useRef, useEffect } from 'react'
import type { VoiceInteractionProps } from '../types'
import { apiClient } from '../services/api'
import { useSessionStore } from '../store/sessionStore'

export default function VoiceInteraction({
  sessionId,
  onMessageSent,
  isLoading,
}: VoiceInteractionProps) {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [interimTranscript, setInterimTranscript] = useState('')

  const recognitionRef = useRef<any>(null)
  const { addMessage, setError } = useSessionStore()

  // 初始化语音识别
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
      recognitionRef.current = new SpeechRecognition()

      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = true
      recognitionRef.current.lang = 'zh-CN'

      recognitionRef.current.onresult = (event: any) => {
        let finalTranscript = ''
        let interimTranscript = ''

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            finalTranscript += transcript
          } else {
            interimTranscript += transcript
          }
        }

        if (finalTranscript) {
          setTranscript(finalTranscript)
        }
        setInterimTranscript(interimTranscript)
      }

      recognitionRef.current.onerror = (event: any) => {
        console.error('语音识别错误:', event.error)
        setIsListening(false)

        if (event.error === 'no-speech') {
          setError('没有听到声音，请再试一次')
        } else if (event.error === 'not-allowed') {
          setError('请允许麦克风权限')
        } else {
          setError('语音识别出现问题，请重试')
        }
      }

      recognitionRef.current.onend = () => {
        setIsListening(false)
      }
    } else {
      setError('你的浏览器不支持语音识别')
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
    }
  }, [])

  const handleStartListening = () => {
    if (!recognitionRef.current) {
      setError('语音识别不可用')
      return
    }

    setTranscript('')
    setInterimTranscript('')
    setIsListening(true)
    recognitionRef.current.start()
  }

  const handleStopListening = async () => {
    if (!recognitionRef.current) return

    setIsListening(false)
    recognitionRef.current.stop()

    // 等待最终识别结果
    setTimeout(async () => {
      if (transcript.trim()) {
        try {
          addMessage('user', transcript)

          const response = await apiClient.sendVoiceInput({
            session_id: sessionId,
            transcript: transcript.trim(),
          })

          addMessage('assistant', response.response)
          onMessageSent(transcript)

          // 清空输入
          setTranscript('')
          setInterimTranscript('')
        } catch (err) {
          console.error('发送语音失败:', err)
          setError('发送消息失败，请重试')
        }
      }
    }, 500)
  }

  return (
    <div className="card-sprout">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-sprout-800 mb-2">
          🎤 语音对话
        </h2>
        <p className="text-lg text-sprout-600">
          点击麦克风，对小芽说话
        </p>
      </div>

      {/* 实时识别结果显示 */}
      {(transcript || interimTranscript) && (
        <div className="mb-6 p-4 bg-sprout-50 rounded-2xl border-2 border-sprout-200">
          <div className="text-sm text-sprout-500 mb-2">你说：</div>
          <div className="text-xl font-semibold text-sprout-800">
            {transcript}
            <span className="text-sprout-400">{interimTranscript}</span>
          </div>
        </div>
      )}

      {/* 麦克风按钮 */}
      <div className="flex justify-center">
        {!isListening ? (
          <button
            onClick={handleStartListening}
            disabled={isLoading}
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
        {isListening ? (
          <div className="text-lg text-sprout-700 font-semibold animate-pulse">
            🔴 正在听你说话...
          </div>
        ) : (
          <div className="text-lg text-sprout-600">
            点击开始说话
          </div>
        )}
      </div>
    </div>
  )
}
