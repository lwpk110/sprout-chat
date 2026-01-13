/**
 * 文字交互组件
 * 允许学生通过文字输入与小芽对话
 */

import { useState, FormEvent } from 'react'
import type { VoiceInteractionProps } from '../types'
import { apiClient } from '../services/api'
import { useSessionStore } from '../store/sessionStore'

export default function TextInteraction({
  sessionId,
  onMessageSent,
  isLoading,
}: VoiceInteractionProps) {
  const [inputText, setInputText] = useState('')
  const [isSending, setIsSending] = useState(false)
  const { addMessage, setError } = useSessionStore()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()

    if (!inputText.trim()) {
      setError('请输入你想说的话')
      return
    }

    if (isSending || isLoading) return

    try {
      setIsSending(true)
      addMessage('user', inputText)

      const response = await apiClient.sendTextInput({
        session_id: sessionId,
        content: inputText.trim(),
      })

      addMessage('assistant', response.response)
      onMessageSent(inputText)

      // 清空输入
      setInputText('')
    } catch (err) {
      console.error('发送文字失败:', err)
      setError('发送消息失败，请重试')
    } finally {
      setIsSending(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Ctrl+Enter 或 Cmd+Enter 发送消息
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleSubmit(e)
    }
  }

  return (
    <div className="card-sprout">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-sprout-800 mb-2">
          ✍️ 文字对话
        </h2>
        <p className="text-lg text-sprout-600">
          输入文字，和小芽聊天
        </p>
      </div>

      {/* 输入表单 */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* 文字输入框 */}
        <div>
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="在这里输入你想说的话..."
            disabled={isSending || isLoading}
            className={`
              w-full px-6 py-4 rounded-2xl
              border-3 border-sprout-300
              bg-white
              text-xl
              placeholder:text-sprout-400
              focus:outline-none focus:border-sprout-500 focus:ring-4 focus:ring-sprout-200
              disabled:opacity-50 disabled:cursor-not-allowed
              resize-none
              transition-all duration-200
              min-h-[120px]
            `}
            rows={4}
          />
        </div>

        {/* 提示文字 */}
        <div className="text-center text-sm text-sprout-500">
          💡 小贴士：按 Ctrl+Enter 快速发送
        </div>

        {/* 发送按钮 */}
        <div className="flex justify-center">
          <button
            type="submit"
            disabled={isSending || isLoading || !inputText.trim()}
            className={`
              px-8 py-4 rounded-full
              text-xl font-bold
              shadow-lg
              transition-all duration-200
              ${
                isSending || isLoading || !inputText.trim()
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-sprout-500 to-sprout-600 text-white hover:from-sprout-600 hover:to-sprout-700 hover:scale-105 active:scale-95'
              }
            `}
          >
            {isSending ? (
              <span className="flex items-center gap-2">
                <svg
                  className="animate-spin h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                发送中...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                  />
                </svg>
                发送消息
              </span>
            )}
          </button>
        </div>
      </form>

      {/* 快捷输入建议 */}
      <div className="mt-6">
        <div className="text-sm font-semibold text-sprout-600 mb-3">
          💭 试试这些：
        </div>
        <div className="flex flex-wrap gap-2">
          {[
            '今天天气怎么样',
            '给我讲个故事',
            '教我算术',
            '帮我检查作业',
          ].map((suggestion) => (
            <button
              key={suggestion}
              onClick={() => setInputText(suggestion)}
              disabled={isSending || isLoading}
              className={`
                px-4 py-2 rounded-full
                text-sm font-medium
                bg-sprout-100 text-sprout-700
                hover:bg-sprout-200
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all duration-200
              `}
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
