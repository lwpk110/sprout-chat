/**
 * 引导响应组件（增强版 - 集成 TTS）
 * 突出显示小芽的引导式教学回复
 * 强调"不直接给答案"的教学理念
 * 支持语音播报（TTS）
 */

import { useState } from 'react'
import type { GuidedResponseProps } from '../types'
import useSpeechSynthesis from '../hooks/useSpeechSynthesis'

export default function GuidedResponse({ response, timestamp }: GuidedResponseProps) {
  // 使用 TTS Hook
  const { isSpeaking, isPaused, speak, pause, resume, cancel, isSupported } = useSpeechSynthesis({
    rate: 0.9,        // 稍慢的语速适合学生
    pitch: 1.0,       // 正常音调
    volume: 1.0,      // 最大音量
    lang: 'zh-CN',    // 中文
    onEnd: () => {
      // 播放结束，不需要额外处理
    },
    onError: (error) => {
      console.error('TTS 播放错误:', error)
    },
  })

  const [showTTSButton, setShowTTSButton] = useState(true)

  /**
   * 处理语音播报
   */
  const handleSpeak = () => {
    if (!isSupported) {
      alert('你的浏览器不支持语音播报功能')
      return
    }

    if (isSpeaking) {
      // 如果正在播放，暂停或恢复
      if (isPaused) {
        resume()
      } else {
        pause()
      }
    } else {
      // 开始播放
      const success = speak(response)
      if (!success) {
        alert('无法播放语音，请再试一次')
      }
    }
  }

  /**
   * 停止播放
   */
  const handleStop = () => {
    cancel()
  }

  /**
   * 格式化时间
   */
  const formatTime = (isoString: string) => {
    const date = new Date(isoString)
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  /**
   * 根据内容自动检测并显示鼓励标签
   */
  const detectEncouragementTags = () => {
    const tags: Array<{ text: string; emoji: string; bgColor: string; textColor: string }> = []

    if (response.includes('很棒') || response.includes('真好') || response.includes('不错')) {
      tags.push({ text: '做得好！', emoji: '🎉', bgColor: 'bg-green-100', textColor: 'text-green-700' })
    }

    if (response.includes('？') || response.includes('怎么') || response.includes('为什么')) {
      tags.push({ text: '一起思考', emoji: '🤔', bgColor: 'bg-blue-100', textColor: 'text-blue-700' })
    }

    if (response.includes('试试') || response.includes('可以') || response.includes('动手')) {
      tags.push({ text: '你可以试试', emoji: '💪', bgColor: 'bg-purple-100', textColor: 'text-purple-700' })
    }

    if (response.includes('加油') || response.includes('继续')) {
      tags.push({ text: '继续努力', emoji: '💫', bgColor: 'bg-orange-100', textColor: 'text-orange-700' })
    }

    return tags
  }

  const encouragementTags = detectEncouragementTags()

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

        {/* TTS 控制按钮 */}
        {showTTSButton && isSupported && (
          <div className="flex items-center gap-2">
            {/* 播放/暂停按钮 */}
            <button
              onClick={handleSpeak}
              className="
                px-4 py-2 rounded-full
                bg-sprout-200 hover:bg-sprout-300
                text-sprout-700 font-semibold
                transition-all duration-200
                disabled:opacity-50
                flex items-center gap-2
              "
              title={isSpeaking ? (isPaused ? '继续播放' : '暂停播放') : '读给我听'}
            >
              {isSpeaking ? (
                isPaused ? (
                  <>
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z" />
                    </svg>
                    继续
                  </>
                ) : (
                  <>
                    <div className="w-4 h-4 rounded-full bg-sprout-500 animate-ping"></div>
                    暂停
                  </>
                )
              ) : (
                <>
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z" />
                  </svg>
                  读给我听
                </>
              )}
            </button>

            {/* 停止按钮（仅在播放时显示） */}
            {isSpeaking && (
              <button
                onClick={handleStop}
                className="
                  px-3 py-2 rounded-full
                  bg-red-100 hover:bg-red-200
                  text-red-700 font-semibold
                  transition-all duration-200
                  flex items-center gap-1
                "
                title="停止播放"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M6 6h12v12H6z" />
                </svg>
                停止
              </button>
            )}
          </div>
        )}
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

        {/* 自动检测的鼓励标签 */}
        {encouragementTags.length > 0 && (
          <div className="flex gap-2 flex-wrap">
            {encouragementTags.map((tag, index) => (
              <span
                key={index}
                className={`px-4 py-2 ${tag.bgColor} ${tag.textColor} rounded-full font-semibold`}
              >
                {tag.emoji} {tag.text}
              </span>
            ))}
          </div>
        )}
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

      {/* TTS 播放状态提示（仅在播放时显示） */}
      {isSpeaking && (
        <div className="mt-3 p-3 bg-sprout-100 rounded-xl border border-sprout-300 animate-pulse">
          <div className="flex items-center gap-2 text-sm text-sprout-700">
            <span>🔊</span>
            <span>{isPaused ? '已暂停' : '正在播放...'}</span>
          </div>
        </div>
      )}
    </div>
  )
}
