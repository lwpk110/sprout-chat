/**
 * 拍照交互组件
 * 支持拍照上传作业，AI 识别后引导式教学
 */

import { useState, useRef } from 'react'
import type { PhotoInteractionProps } from '../types'
import { apiClient } from '../services/api'
import { useSessionStore } from '../store/sessionStore'

export default function PhotoInteraction({
  sessionId,
  onImageUploaded,
  isLoading,
}: PhotoInteractionProps) {
  const [preview, setPreview] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const { addMessage, setError } = useSessionStore()

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      setError('请选择图片文件')
      return
    }

    // 验证文件大小（最大 10MB）
    if (file.size > 10 * 1024 * 1024) {
      setError('图片太大了，请选择小于 10MB 的图片')
      return
    }

    // 创建预览
    const reader = new FileReader()
    reader.onloadend = () => {
      setPreview(reader.result as string)
    }
    reader.readAsDataURL(file)
  }

  const handleUpload = async () => {
    if (!preview || !fileInputRef.current?.files?.[0]) return

    setIsUploading(true)
    setError(null)

    try {
      const file = fileInputRef.current.files[0]

      // 添加用户消息
      addMessage('user', '[上传了一张图片]')

      // 调用真实的后端 API
      const response = await apiClient.uploadImageForGuidance(
        file,
        sessionId,
        6, // student_age
        '数学' // subject
      )

      // 添加 AI 响应
      if (response.success && response.data.response) {
        addMessage('assistant', response.data.response)
        onImageUploaded('图片已识别')
      } else {
        throw new Error('未能获取 AI 响应')
      }

      // 清理预览
      setPreview(null)

      // 重置文件输入
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

    } catch (err) {
      console.error('上传图片失败:', err)
      setError('上传图片失败，请重试')
      addMessage('assistant', '哎呀，小芽没看清这张图片，能再拍一次吗？📷')
    } finally {
      setIsUploading(false)
    }
  }

  const handleClear = () => {
    setPreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleCameraClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="card-sprout">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-sprout-800 mb-2">
          📷 拍照上传
        </h2>
        <p className="text-lg text-sprout-600">
          拍下你的作业，小芽来帮你
        </p>
      </div>

      {/* 隐藏的文件输入 */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        className="hidden"
        data-testid="file-input"
      />

      {/* 图片预览区域 */}
      {preview ? (
        <div className="mb-6">
          <div className="relative">
            <img
              src={preview}
              alt="预览"
              className="w-full h-64 object-cover rounded-2xl border-4 border-sprout-200"
            />
            <button
              onClick={handleClear}
              className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-2 shadow-lg hover:bg-red-600 transition-colors"
              disabled={isUploading}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* 上传按钮 */}
          <div className="mt-4 flex gap-4">
            <button
              onClick={handleUpload}
              disabled={isUploading || isLoading}
              className="flex-1 btn-sprout btn-sprout-primary disabled:opacity-50"
            >
              {isUploading ? '正在上传...' : '发送给小芽'}
            </button>
            <button
              onClick={handleClear}
              disabled={isUploading}
              className="btn-sprout btn-sprout-secondary"
            >
              重拍
            </button>
          </div>
        </div>
      ) : (
        /* 相机按钮 */
        <div className="flex justify-center">
          <button
            onClick={handleCameraClick}
            disabled={isLoading || isUploading}
            className={`
              w-32 h-32 rounded-full shadow-2xl
              bg-gradient-to-br from-blue-400 to-blue-600
              hover:from-blue-500 hover:to-blue-700
              active:scale-95 transition-all duration-200
              flex items-center justify-center
              disabled:opacity-50 disabled:cursor-not-allowed
              hover:scale-105
            `}
          >
            <svg
              className="w-16 h-16 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
          </button>
        </div>
      )}

      {/* 提示文字 */}
      <div className="mt-6 text-center">
        {!preview ? (
          <div className="text-lg text-sprout-600">
            点击拍照
          </div>
        ) : (
          <div className="text-lg text-sprout-700 font-semibold">
            准备发送给小芽
          </div>
        )}
      </div>

      {/* 使用提示 */}
      <div className="mt-4 p-4 bg-blue-50 rounded-xl border-2 border-blue-200">
        <div className="text-sm text-blue-700">
          <div className="font-semibold mb-1">💡 使用提示</div>
          <ul className="list-disc list-inside space-y-1">
            <li>确保作业清晰可见</li>
            <li>在光线充足的地方拍照</li>
            <li>对焦后再拍摄</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
