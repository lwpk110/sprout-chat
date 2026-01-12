/**
 * 引导响应组件
 * 突出显示小芽的引导式教学回复
 * 强调"不直接给答案"的教学理念
 */

import { useState } from 'react'
import type { GuidedResponseProps } from '../types'

export default function GuidedResponse({ response, timestamp }: GuidedResponseProps) {
  const [isSpeaking, setIsSpeaking] = useState(false)

  // 语音播报（可选功能）
  const handleSpeak = () => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(response)
      utterance.lang = 'zh-CN'
      utterance.rate = 0.9  // 稍慢的语速适合学生
      utterance.pitch = 1.2  # 稍高的音调更友好

      utterance.onstart = () => setIsSpeaking(true)
      utterance.onend = () => setIsSpeaking(false)
      utterance.onerror = () => setIsSpeaking(false)

      window.speechSynthesis.speak(utterance)
    }
  }

  // 格式化时间
  const formatTime = (isoString: string) => {
    const date = new Date(isoString)
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="card-sprout border-l-8 border-l-sprout-500 bg-gradient-to-r from-sprout-50 to-white">
      {/* 顶部栏 */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="text-4xl animate-bounce-soft">🌱</div>
          <div>
            <div className="text-2xl font-bold text-sprout-800">
              小芽老师
            </div>
            <div className="text-sm text-sprout-500">
              {formatTime(timestamp)}
            </div>
          </div>
        </div>

        {/* 语音播报按钮 */}
        <button
          onClick={handleSpeak}
          disabled={isSpeaking}
          className="
            px-4 py-2 rounded-full
            bg-sprout-200 hover:bg-sprout-300
            text-sprout-700 font-semibold
            transition-all duration-200
            disabled:opacity-50
            flex items-center gap-2
          "
        >
          {isSpeaking ? (
            <>
              <div className="w-4 h-4 rounded-full bg-sprout-500 animate-ping"></div>
              播放中...
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z" />
              </svg>
              读给我听
            </>
          )}
        </button>
      </div>

      {/* 引导问题内容 */}
      <div className="space-y-4">
        {/* 教学理念标签 */}
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-100 rounded-full border-2 border-yellow-300">
          <span className="text-2xl">💡</span>
          <span className="text-lg font-semibold text-yellow-800">
            引导式教学 - 不直接给答案
          </span>
        </div>

        {/* 引导问题文本 */}
        <div className="p-6 bg-white rounded-2xl border-4 border-sprout-200">
          <p className="text-guided leading-relaxed whitespace-pre-wrap">
            {response}
          </p>
        </div>

        {/* 鼓励标签 */}
        <div className="flex gap-2 flex-wrap">
          {response.includes('很棒') && (
            <span className="px-4 py-2 bg-green-100 text-green-700 rounded-full font-semibold">
              🎉 做得好！
            </span>
          )}
          {response.includes('？') && (
            <span className="px-4 py-2 bg-blue-100 text-blue-700 rounded-full font-semibold">
              🤔 一起思考
            </span>
          )}
          {response.includes('试试') && (
            <span className="px-4 py-2 bg-purple-100 text-purple-700 rounded-full font-semibold">
              💪 你可以试试
            </span>
          )}
        </div>
      </div>

      {/* 教学提示 */}
      <div className="mt-4 p-4 bg-sprout-50 rounded-xl border-2 border-sprout-200">
        <div className="flex items-start gap-2">
          <span className="text-xl">✨</span>
          <div className="text-sm text-sprout-700">
            <div className="font-semibold mb-1">学习小贴士</div>
            <p>小芽会通过提问引导你思考，而不是直接告诉你答案。这样你能学得更牢固哦！</p>
          </div>
        </div>
      </div>
    </div>
  )
}
