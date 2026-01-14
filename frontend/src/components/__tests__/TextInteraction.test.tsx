/**
 * TextInteraction 组件测试
 * 测试文字交互功能，包括输入验证、快捷建议、键盘快捷键
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import TextInteraction from '../TextInteraction'
import { useSessionStore } from '../../store/sessionStore'

// Mock the session store
jest.mock('../../store/sessionStore')

// Mock the API client
jest.mock('../../services/api', () => ({
  apiClient: {
    sendTextInput: jest.fn(),
  },
}))

describe('TextInteraction Component', () => {
  const mockAddMessage = jest.fn()
  const mockSetError = jest.fn()
  const mockOnMessageSent = jest.fn()

  const defaultProps = {
    sessionId: 'test-session-123',
    onMessageSent: mockOnMessageSent,
    isLoading: false,
  }

  beforeEach(() => {
    jest.clearAllMocks()

    // Mock useSessionStore
    ;(useSessionStore as any).mockReturnValue({
      addMessage: mockAddMessage,
      setError: mockSetError,
    })
  })

  describe('组件渲染', () => {
    it('应该渲染文字对话标题', () => {
      render(<TextInteraction {...defaultProps} />)

      expect(screen.getByText('✍️ 文字对话')).toBeInTheDocument()
      expect(screen.getByText('输入文字，和小芽聊天')).toBeInTheDocument()
    })

    it('应该显示输入框', () => {
      render(<TextInteraction {...defaultProps} />)

      const textarea = screen.getByPlaceholderText('在这里输入你想说的话...')
      expect(textarea).toBeInTheDocument()
      expect(textarea).not.toBeDisabled()
    })

    it('应该显示发送按钮', () => {
      render(<TextInteraction {...defaultProps} />)

      const sendButton = screen.getByRole('button', { name: /发送消息/ })
      expect(sendButton).toBeInTheDocument()
      expect(sendButton).toBeDisabled() // 初始状态为空，应该禁用
    })

    it('应该显示快捷输入提示', () => {
      render(<TextInteraction {...defaultProps} />)

      expect(screen.getByText('💡 小贴士：按 Ctrl+Enter 快速发送')).toBeInTheDocument()
    })

    it('应该显示所有快捷输入建议', () => {
      render(<TextInteraction {...defaultProps} />)

      expect(screen.getByText('💭 试试这些：')).toBeInTheDocument()
      expect(screen.getByText('今天天气怎么样')).toBeInTheDocument()
      expect(screen.getByText('给我讲个故事')).toBeInTheDocument()
      expect(screen.getByText('教我算术')).toBeInTheDocument()
      expect(screen.getByText('帮我检查作业')).toBeInTheDocument()
    })
  })

  describe('输入功能', () => {
    it('应该允许用户输入文本', () => {
      render(<TextInteraction {...defaultProps} />)

      const textarea = screen.getByPlaceholderText('在这里输入你想说的话...')
      fireEvent.change(textarea, { target: { value: '你好，小芽' } })

      expect(textarea).toHaveValue('你好，小芽')
    })

    it('应该在输入文本后启用发送按钮', () => {
      render(<TextInteraction {...defaultProps} />)

      const textarea = screen.getByPlaceholderText('在这里输入你想说的话...')
      const sendButton = screen.getByRole('button', { name: /发送消息/ })

      // 初始状态禁用
      expect(sendButton).toBeDisabled()

      // 输入文本后启用
      fireEvent.change(textarea, { target: { value: '你好' } })
      expect(sendButton).not.toBeDisabled()
    })

    it('应该在只包含空格时禁用发送按钮', () => {
      render(<TextInteraction {...defaultProps} />)

      const textarea = screen.getByPlaceholderText('在这里输入你想说的话...')
      const sendButton = screen.getByRole('button', { name: /发送消息/ })

      fireEvent.change(textarea, { target: { value: '   ' } })
      expect(sendButton).toBeDisabled()
    })
  })

  describe('快捷输入建议', () => {
    it('点击快捷建议应该填充输入框', () => {
      render(<TextInteraction {...defaultProps} />)

      const suggestionButton = screen.getByText('今天天气怎么样')
      const textarea = screen.getByPlaceholderText('在这里输入你想说的话...')

      fireEvent.click(suggestionButton)

      expect(textarea).toHaveValue('今天天气怎么样')
    })

    it('应该有 4 个快捷建议按钮', () => {
      render(<TextInteraction {...defaultProps} />)

      const buttons = screen.getAllByRole('button')
      // 过滤出快捷建议按钮（不包括发送按钮）
      const suggestionButtons = buttons.filter(btn =>
        btn.textContent !== '发送中...' && btn.textContent !== '发送消息'
      )

      expect(suggestionButtons).toHaveLength(4)
    })
  })

  describe('键盘快捷键', () => {
    it('Ctrl+Enter 应该触发表单提交', () => {
      render(<TextInteraction {...defaultProps} />)

      const textarea = screen.getByPlaceholderText('在这里输入你想说的话...')

      fireEvent.change(textarea, { target: { value: '你好，小芽' } })

      // 模拟 Ctrl+Enter
      fireEvent.keyDown(textarea, {
        key: 'Enter',
        ctrlKey: true,
      })

      // 由于 sendTextInput 是 async mock，我们验证调用的准备
      expect(mockAddMessage).toHaveBeenCalledWith('user', '你好，小芽')
    })

    it('Cmd+Enter (Mac) 应该触发表单提交', () => {
      render(<TextInteraction {...defaultProps} />)

      const textarea = screen.getByPlaceholderText('在这里输入你想说的话...')

      fireEvent.change(textarea, { target: { value: '测试消息' } })

      // 模拟 Cmd+Enter
      fireEvent.keyDown(textarea, {
        key: 'Enter',
        metaKey: true,
      })

      expect(mockAddMessage).toHaveBeenCalledWith('user', '测试消息')
    })

    it('单独的 Enter 键不应该触发表单提交', () => {
      render(<TextInteraction {...defaultProps} />)

      const textarea = screen.getByPlaceholderText('在这里输入你想说的话...')

      fireEvent.change(textarea, { target: { value: '第一行\n第二行' } })

      // 模拟单独 Enter
      fireEvent.keyDown(textarea, { key: 'Enter', ctrlKey: false, metaKey: false })

      // 不应该调用 addMessage
      expect(mockAddMessage).not.toHaveBeenCalled()
    })
  })

  describe('表单提交', () => {
    it('空文本提交时应该显示错误', async () => {
      const { apiClient } = require('../../services/api')
      apiClient.sendTextInput.mockResolvedValue({ response: '你好！' })

      render(<TextInteraction {...defaultProps} />)

      const textarea = screen.getByPlaceholderText('在这里输入你想说的话...')
      const form = textarea.closest('form')

      // 输入空格
      fireEvent.change(textarea, { target: { value: '   ' } })

      // 提交表单
      if (form) {
        fireEvent.submit(form)
      }

      await waitFor(() => {
        expect(mockSetError).toHaveBeenCalledWith('请输入你想说的话')
      })
    })

    it('正常文本提交应该调用 API 和回调', async () => {
      const { apiClient } = require('../../services/api')
      apiClient.sendTextInput.mockResolvedValue({ response: '收到你的消息了！' })

      render(<TextInteraction {...defaultProps} />)

      const textarea = screen.getByPlaceholderText('在这里输入你想说的话...')
      const sendButton = screen.getByRole('button', { name: /发送消息/ })

      fireEvent.change(textarea, { target: { value: '你好，小芽' } })
      fireEvent.click(sendButton)

      await waitFor(() => {
        expect(mockAddMessage).toHaveBeenCalledWith('user', '你好，小芽')
        expect(apiClient.sendTextInput).toHaveBeenCalledWith({
          session_id: 'test-session-123',
          content: '你好，小芽',
        })
      })

      // API 响应后应该添加助手消息
      await waitFor(() => {
        expect(mockAddMessage).toHaveBeenCalledWith('assistant', '收到你的消息了！')
        expect(mockOnMessageSent).toHaveBeenCalledWith('你好，小芽')
      })
    })

    it('提交成功后应该清空输入框', async () => {
      const { apiClient } = require('../../services/api')
      apiClient.sendTextInput.mockResolvedValue({ response: '好的' })

      render(<TextInteraction {...defaultProps} />)

      const textarea = screen.getByPlaceholderText('在这里输入你想说的话...')
      const sendButton = screen.getByRole('button', { name: /发送消息/ })

      fireEvent.change(textarea, { target: { value: '测试消息' } })
      fireEvent.click(sendButton)

      await waitFor(() => {
        expect(textarea).toHaveValue('')
      })
    })
  })

  describe('加载状态', () => {
    it('发送中应该禁用输入框和按钮', async () => {
      const { apiClient } = require('../../services/api')
      // 模拟慢请求
      apiClient.sendTextInput.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({ response: 'OK' }), 100))
      )

      render(<TextInteraction {...defaultProps} />)

      const textarea = screen.getByPlaceholderText('在这里输入你想说的话...')
      const sendButton = screen.getByRole('button', { name: /发送消息/ })

      fireEvent.change(textarea, { target: { value: '测试' } })
      fireEvent.click(sendButton)

      // 等待状态更新
      await waitFor(() => {
        expect(textarea).toBeDisabled()
        expect(sendButton).toBeDisabled()
        expect(screen.getByText('发送中...')).toBeInTheDocument()
      })
    })

    it('外部加载时应该禁用输入框和按钮', () => {
      render(<TextInteraction {...defaultProps} isLoading={true} />)

      const textarea = screen.getByPlaceholderText('在这里输入你想说的话...')
      const sendButton = screen.getByRole('button', { name: /发送消息/ })

      expect(textarea).toBeDisabled()
      expect(sendButton).toBeDisabled()
    })
  })

  describe('快捷建议禁用状态', () => {
    it('发送中应该禁用快捷建议按钮', async () => {
      const { apiClient } = require('../../services/api')
      apiClient.sendTextInput.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({ response: 'OK' }), 100))
      )

      render(<TextInteraction {...defaultProps} />)

      const textarea = screen.getByPlaceholderText('在这里输入你想说的话...')
      const sendButton = screen.getByRole('button', { name: /发送消息/ })
      const suggestionButton = screen.getByText('今天天气怎么样')

      fireEvent.change(textarea, { target: { value: '测试' } })
      fireEvent.click(sendButton)

      await waitFor(() => {
        expect(suggestionButton).toBeDisabled()
      })
    })

    it('外部加载时应该禁用快捷建议按钮', () => {
      render(<TextInteraction {...defaultProps} isLoading={true} />)

      const suggestionButton = screen.getByText('今天天气怎么样')
      expect(suggestionButton).toBeDisabled()
    })
  })
})
