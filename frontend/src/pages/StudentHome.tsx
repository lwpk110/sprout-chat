/**
 * 学生主页
 * 适合一年级学生的简洁友好界面
 */

import { useEffect } from 'react'
import { useSessionStore } from '../store/sessionStore'
import { apiClient } from '../services/api'
import VoiceInteraction from '../components/VoiceInteraction'
import PhotoInteraction from '../components/PhotoInteraction'
import TextInteraction from '../components/TextInteraction'
import GuidedResponse from '../components/GuidedResponse'

export default function StudentHome() {
  const { sessionId, setSession, messages, isLoading, error, setLoading, setError } = useSessionStore()

  useEffect(() => {
    // 组件挂载时创建会话
    initializeSession()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const initializeSession = async () => {
    try {
      setLoading(true)
      const session = await apiClient.createSession({
        student_id: `student_${Date.now()}`,
        subject: '数学',
        student_age: 6,
        topic: '学习伙伴',
      })
      setSession(session)
    } catch (err) {
      console.error('创建会话失败:', err)
      setError('哎呀，小芽遇到了一点问题，请刷新页面试试')
    } finally {
      setLoading(false)
    }
  }

  if (isLoading && !sessionId) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-2xl text-sprout-700">小芽正在赶来...</p>
        </div>
      </div>
    )
  }

  if (error && !sessionId) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="card-sprout max-w-md w-full text-center">
          <div className="text-6xl mb-4">😢</div>
          <h2 className="text-2xl font-bold text-sprout-800 mb-4">
            哎呀，出错了
          </h2>
          <p className="text-xl text-sprout-700 mb-6">{error}</p>
          <button
            onClick={initializeSession}
            className="btn-sprout btn-sprout-primary"
          >
            再试一次
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen p-4 md:p-8">
      {/* 顶部欢迎栏 */}
      <header className="mb-8">
        <div className="card-sprout max-w-4xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="text-5xl">🌱</div>
              <div>
                <h1 className="text-3xl md:text-4xl font-bold text-sprout-800">
                  小芽家教
                </h1>
                <p className="text-lg text-sprout-600">
                  你的 AI 学习伙伴
                </p>
              </div>
            </div>
            {sessionId && (
              <div className="hidden md:block text-right">
                <div className="text-sm text-sprout-500">会话 ID</div>
                <div className="text-lg font-mono text-sprout-700">
                  {sessionId.slice(0, 8)}...
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* 主要交互区域 */}
      <main className="max-w-4xl mx-auto space-y-6">
        {/* 引导响应显示 */}
        {messages.length > 0 && (
          <div className="space-y-4">
            {messages.map((msg, index) => (
              <div key={index}>
                {msg.role === 'assistant' && (
                  <GuidedResponse
                    response={msg.content}
                    timestamp={msg.timestamp}
                  />
                )}
              </div>
            ))}
          </div>
        )}

        {/* 交互模式选择 */}
        {sessionId && (
          <div className="grid md:grid-cols-3 gap-6">
            {/* 语音交互 */}
            <VoiceInteraction
              sessionId={sessionId}
              onMessageSent={(message) => {
                console.log('消息已发送:', message)
              }}
              isLoading={isLoading}
            />

            {/* 文字交互 */}
            <TextInteraction
              sessionId={sessionId}
              onMessageSent={(message) => {
                console.log('消息已发送:', message)
              }}
              isLoading={isLoading}
            />

            {/* 拍照交互 */}
            <PhotoInteraction
              sessionId={sessionId}
              onImageUploaded={(result) => {
                console.log('图片已上传:', result)
              }}
              isLoading={isLoading}
            />
          </div>
        )}

        {/* 历史记录（可折叠） */}
        {messages.length > 3 && (
          <details className="card-sprout">
            <summary className="cursor-pointer text-lg font-semibold text-sprout-700">
              查看更多对话
            </summary>
            <div className="mt-4 space-y-3">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-2xl ${
                    msg.role === 'user'
                      ? 'bg-sprout-100 ml-8'
                      : 'bg-sprout-50 mr-8 border-2 border-sprout-200'
                  }`}
                >
                  <div className="text-sm text-sprout-500 mb-1">
                    {msg.role === 'user' ? '👦 你说' : '🌱 小芽说'}
                  </div>
                  <div className="text-lg">{msg.content}</div>
                </div>
              ))}
            </div>
          </details>
        )}
      </main>

      {/* 底部提示 */}
      <footer className="mt-12 text-center">
        <p className="text-sprout-500 text-sm">
          💡 点击麦克风、输入文字或拍照开始学习吧！
        </p>
      </footer>
    </div>
  )
}
