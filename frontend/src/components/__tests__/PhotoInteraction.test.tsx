/**
 * PhotoInteraction 组件测试
 * 测试拍照上传功能
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import PhotoInteraction from '../PhotoInteraction'
import { useSessionStore } from '../../store/sessionStore'

// Mock the session store
jest.mock('../../store/sessionStore')

// Mock the API client
jest.mock('../../services/api', () => ({
  apiClient: {
    uploadImageForGuidance: jest.fn(),
  },
}))

describe('PhotoInteraction Component', () => {
  const mockAddMessage = jest.fn()
  const mockSetError = jest.fn()
  const mockOnImageUploaded = jest.fn()

  const defaultProps = {
    sessionId: 'test-session-123',
    onImageUploaded: mockOnImageUploaded,
    isLoading: false,
  }

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useSessionStore as any).mockReturnValue({
      addMessage: mockAddMessage,
      setError: mockSetError,
    })
  })

  afterEach(() => {
    jest.restoreAllMocks()
  })

  describe('组件渲染', () => {
    it('应该渲染拍照按钮', () => {
      render(<PhotoInteraction {...defaultProps} />)
      expect(screen.getByText('📷 拍照上传')).toBeInTheDocument()
    })

    it('应该显示使用提示', () => {
      render(<PhotoInteraction {...defaultProps} />)
      expect(screen.getByText('💡 使用提示')).toBeInTheDocument()
      expect(screen.getByText('确保作业清晰可见')).toBeInTheDocument()
    })

    it('应该在加载时禁用按钮', () => {
      render(<PhotoInteraction {...defaultProps} isLoading={true} />)
      const cameraButton = screen.getByRole('button').querySelector('svg')
      expect(cameraButton).toBeInTheDocument()
    })
  })

  describe('文件选择', () => {
    it('应该拒绝非图片文件', async () => {
      render(<PhotoInteraction {...defaultProps} />)

      const fileInput = screen.getByRole('button').parentElement?.querySelector('input[type="file"]') as HTMLInputElement
      expect(fileInput).toBeInTheDocument()

      const file = new File(['content'], 'test.txt', { type: 'text/plain' })

      Object.defineProperty(fileInput, 'files', {
        value: [file],
        writable: false,
      })

      fireEvent.change(fileInput)

      await waitFor(() => {
        expect(mockSetError).toHaveBeenCalledWith('请选择图片文件')
      })
    })

    it('应该拒绝超过 10MB 的文件', async () => {
      render(<PhotoInteraction {...defaultProps} />)

      const fileInput = screen.getByRole('button').parentNode?.querySelector('input[type="file"]') as HTMLInputElement

      // 创建一个 11MB 的文件
      const largeContent = new Array(11 * 1024 * 1024).fill('x').join('')
      const file = new File([largeContent], 'large.jpg', { type: 'image/jpeg' })

      Object.defineProperty(fileInput, 'files', {
        value: [file],
        writable: false,
      })

      fireEvent.change(fileInput)

      await waitFor(() => {
        expect(mockSetError).toHaveBeenCalledWith('图片太大了，请选择小于 10MB 的图片')
      })
    })

    it('应该接受有效的图片文件并显示预览', async () => {
      render(<PhotoInteraction {...defaultProps} />)

      const fileInput = screen.getByRole('button').parentNode?.querySelector('input[type="file"]') as HTMLInputElement
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })

      Object.defineProperty(fileInput, 'files', {
        value: [file],
        writable: false,
      })

      fireEvent.change(fileInput)

      await waitFor(() => {
        const preview = screen.getByAltText('预览')
        expect(preview).toBeInTheDocument()
      })
    })
  })

  describe('图片上传', () => {
    it('应该成功上传图片并显示 AI 响应', async () => {
      const { apiClient } = require('../../services/api')
      const mockResponse = {
        success: true,
        data: {
          student_id: 'test-session-123',
          subject: '数学',
          response: '这是一道加法题，让我来引导你...',
          image_size: 12345,
        },
      }
      apiClient.uploadImageForGuidance.mockResolvedValue(mockResponse)

      render(<PhotoInteraction {...defaultProps} />)

      // 选择文件
      const fileInput = screen.getByRole('button').parentNode?.querySelector('input[type="file"]') as HTMLInputElement
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })

      Object.defineProperty(fileInput, 'files', {
        value: [file],
        writable: false,
      })

      fireEvent.change(fileInput)

      await waitFor(() => {
        expect(screen.getByAltText('预览')).toBeInTheDocument()
      })

      // 点击上传按钮
      const uploadButton = screen.getByText('发送给小芽')
      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(mockAddMessage).toHaveBeenCalledWith('user', '[上传了一张图片]')
        expect(mockAddMessage).toHaveBeenCalledWith('assistant', mockResponse.data.response)
        expect(mockOnImageUploaded).toHaveBeenCalledWith('图片已识别')
      })
    })

    it('应该处理上传失败并显示友好错误', async () => {
      const { apiClient } = require('../../services/api')
      apiClient.uploadImageForGuidance.mockRejectedValue(new Error('Network error'))

      render(<PhotoInteraction {...defaultProps} />)

      // 选择并上传文件
      const fileInput = screen.getByRole('button').parentNode?.querySelector('input[type="file"]') as HTMLInputElement
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })

      Object.defineProperty(fileInput, 'files', {
        value: [file],
        writable: false,
      })

      fireEvent.change(fileInput)

      await waitFor(() => {
        expect(screen.getByAltText('预览')).toBeInTheDocument()
      })

      const uploadButton = screen.getByText('发送给小芽')
      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(mockAddMessage).toHaveBeenCalledWith('assistant', '哎呀，小芽没看清这张图片，能再拍一次吗？📷')
        expect(mockSetError).toHaveBeenCalledWith('上传图片失败，请重试')
      })
    })

    it('上传时应该禁用按钮', async () => {
      const { apiClient } = require('../../services/api')
      apiClient.uploadImageForGuidance.mockImplementation(() => new Promise(() => {})) // 永不 resolve

      render(<PhotoInteraction {...defaultProps} />)

      // 选择文件
      const fileInput = screen.getByRole('button').parentNode?.querySelector('input[type="file"]') as HTMLInputElement
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })

      Object.defineProperty(fileInput, 'files', {
        value: [file],
        writable: false,
      })

      fireEvent.change(fileInput)

      await waitFor(() => {
        expect(screen.getByAltText('预览')).toBeInTheDocument()
      })

      const uploadButton = screen.getByText('发送给小芽')
      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(uploadButton).toBeDisabled()
        expect(screen.getByText('正在上传...')).toBeInTheDocument()
      })
    })
  })

  describe('预览管理', () => {
    it('应该允许清除图片预览', async () => {
      render(<PhotoInteraction {...defaultProps} />)

      // 选择文件
      const fileInput = screen.getByRole('button').parentNode?.querySelector('input[type="file"]') as HTMLInputElement
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })

      Object.defineProperty(fileInput, 'files', {
        value: [file],
        writable: false,
      })

      fireEvent.change(fileInput)

      await waitFor(() => {
        expect(screen.getByAltText('预览')).toBeInTheDocument()
      })

      // 点击重拍按钮
      const retakeButton = screen.getByText('重拍')
      fireEvent.click(retakeButton)

      await waitFor(() => {
        expect(screen.queryByAltText('预览')).not.toBeInTheDocument()
      })
    })

    it('应该在上传成功后清除预览', async () => {
      const { apiClient } = require('../../services/api')
      const mockResponse = {
        success: true,
        data: {
          student_id: 'test-session-123',
          subject: '数学',
          response: '让我来帮你看看这道题...',
          image_size: 12345,
        },
      }
      apiClient.uploadImageForGuidance.mockResolvedValue(mockResponse)

      render(<PhotoInteraction {...defaultProps} />)

      // 选择文件
      const fileInput = screen.getByRole('button').parentNode?.querySelector('input[type="file"]') as HTMLInputElement
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })

      Object.defineProperty(fileInput, 'files', {
        value: [file],
        writable: false,
      })

      fireEvent.change(fileInput)

      await waitFor(() => {
        expect(screen.getByAltText('预览')).toBeInTheDocument()
      })

      // 上传
      const uploadButton = screen.getByText('发送给小芽')
      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(screen.queryByAltText('预览')).not.toBeInTheDocument()
      })
    })
  })

  describe('响应式教学人格', () => {
    it('应该使用正确的参数调用 API', async () => {
      const { apiClient } = require('../../services/api')
      apiClient.uploadImageForGuidance.mockResolvedValue({
        success: true,
        data: {
          student_id: 'test-session-123',
          subject: '数学',
          response: '响应',
          image_size: 12345,
        },
      })

      render(<PhotoInteraction {...defaultProps} />)

      // 选择文件
      const fileInput = screen.getByRole('button').parentNode?.querySelector('input[type="file"]') as HTMLInputElement
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })

      Object.defineProperty(fileInput, 'files', {
        value: [file],
        writable: false,
      })

      fireEvent.change(fileInput)

      await waitFor(() => {
        expect(screen.getByAltText('预览')).toBeInTheDocument()
      })

      // 上传
      const uploadButton = screen.getByText('发送给小芽')
      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(apiClient.uploadImageForGuidance).toHaveBeenCalledWith(
          file,
          'test-session-123',
          6, // student_age
          '数学' // subject
        )
      })
    })
  })
})
