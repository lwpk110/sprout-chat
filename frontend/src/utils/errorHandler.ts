/**
 * 错误处理工具
 * 将技术错误转换为适合一年级学生理解的友好提示
 */

/**
 * 错误类型定义
 */
export type ErrorType =
  | 'network'
  | 'permission'
  | 'recognition'
  | 'camera'
  | 'upload'
  | 'validation'
  | 'unknown';

/**
 * 错误信息映射
 */
const ERROR_MESSAGES: Record<ErrorType, { title: string; message: string; suggestion: string }> = {
  network: {
    title: '网络好像有问题',
    message: '连接不上服务器，请检查网络',
    suggestion: '试试：\n1. 检查 WiFi 是否开启\n2. 稍后再试',
  },
  permission: {
    title: '需要使用麦克风',
    message: '请允许使用麦克风，这样才能和小芽对话',
    suggestion: '试试：\n1. 点击地址栏左侧的锁图标\n2. 允许使用麦克风\n3. 刷新页面',
  },
  recognition: {
    title: '没听清楚',
    message: '小芽没听懂你说什么，能再说一遍吗？',
    suggestion: '试试：\n1. 说话大声一点\n2. 说慢一点\n3. 或者用文字输入',
  },
  camera: {
    title: '需要使用相机',
    message: '请允许使用相机，这样才能拍照上传作业',
    suggestion: '试试：\n1. 点击地址栏左侧的锁图标\n2. 允许使用相机\n3. 刷新页面',
  },
  upload: {
    title: '上传失败',
    message: '图片上传失败了，请重试',
    suggestion: '试试：\n1. 检查网络连接\n2. 重新拍照\n3. 选择更清晰的图片',
  },
  validation: {
    title: '输入有误',
    message: '请检查输入内容',
    suggestion: '试试：\n1. 确保内容不为空\n2. 内容不超过 2000 字',
  },
  unknown: {
    title: '出错了',
    message: '小芽遇到一点问题，请再试一次',
    suggestion: '如果问题一直存在，请告诉爸爸妈妈',
  },
};

/**
 * 错误对象
 */
export interface SproutError {
  type: ErrorType;
  title: string;
  message: string;
  suggestion: string;
  originalError?: Error;
}

/**
 * 分类错误类型
 */
function classifyError(error: Error | string | unknown): ErrorType {
  if (typeof error === 'string') {
    const message = error.toLowerCase();
    if (message.includes('network') || message.includes('fetch') || message.includes('connection')) {
      return 'network';
    }
    if (message.includes('permission') || message.includes('denied') || message.includes('allowed')) {
      return 'permission';
    }
    if (message.includes('recognition') || message.includes('speech') || message.includes('audio')) {
      return 'recognition';
    }
    if (message.includes('camera') || message.includes('video')) {
      return 'camera';
    }
    if (message.includes('upload') || message.includes('file')) {
      return 'upload';
    }
    return 'unknown';
  }

  if (error instanceof Error) {
    const message = error.message.toLowerCase();

    // Network errors
    if (
      message.includes('network') ||
      message.includes('fetch') ||
      message.includes('connection') ||
      message.includes('timeout') ||
      message.includes('ECONNREFUSED') ||
      message.includes('ENOTFOUND')
    ) {
      return 'network';
    }

    // Permission errors
    if (
      message.includes('permission') ||
      message.includes('denied') ||
      message.includes('allowed') ||
      message.includes('NotAllowedError') ||
      message.includes('SecurityError')
    ) {
      return 'permission';
    }

    // Recognition errors
    if (
      message.includes('recognition') ||
      message.includes('speech') ||
      message.includes('audio') ||
      message.includes('no-speech') ||
      message.includes('aborted'
    )) {
      return 'recognition';
    }

    // Camera errors
    if (
      message.includes('camera') ||
      message.includes('video') ||
      message.includes('NotFoundError') ||
      message.includes('DevicesNotFoundError')
    ) {
      return 'camera';
    }

    // Upload errors
    if (message.includes('upload') || message.includes('file')) {
      return 'upload';
    }

    // Validation errors
    if (message.includes('validation') || message.includes('invalid')) {
      return 'validation';
    }
  }

  return 'unknown';
}

/**
 * 处理错误并返回用户友好的错误信息
 * @param error 错误对象或消息
 * @returns SproutError
 *
 * @example
 * try {
 *   await uploadImage(file);
 * } catch (error) {
 *   const friendlyError = handleError(error);
 *   showErrorToUser(friendlyError);
 * }
 */
export function handleError(error: Error | string | unknown): SproutError {
  const errorType = classifyError(error);
  const errorTemplate = ERROR_MESSAGES[errorType];

  return {
    type: errorType,
    ...errorTemplate,
    originalError: error instanceof Error ? error : undefined,
  };
}

/**
 * 格式化错误为用户可读的完整消息
 * @param error 错误对象
 * @returns 完整的错误消息
 */
export function formatErrorMessage(error: SproutError): string {
  return `${error.title}\n\n${error.message}\n\n${error.suggestion}`;
}

/**
 * 判断错误是否可重试
 * @param error 错误对象
 * @returns 是否可重试
 */
export function isRetryableError(error: SproutError): boolean {
  return ['network', 'upload', 'recognition'].includes(error.type);
}

/**
 * 创建默认错误对象
 */
export function createDefaultError(type: ErrorType = 'unknown'): SproutError {
  const errorTemplate = ERROR_MESSAGES[type];
  return {
    type,
    ...errorTemplate,
  };
}

/**
 * API 错误处理
 * 将 API 响应错误转换为用户友好的错误信息
 */
export function handleApiError(response: { status?: number; data?: { error?: string } }): SproutError {
  const status = response.status;
  const apiError = response.data?.error;

  if (status === 401 || status === 403) {
    return createDefaultError('permission');
  }

  if (status === 413) {
    return {
      type: 'upload',
      title: '图片太大',
      message: '图片文件太大，上传失败',
      suggestion: '试试：\n1. 选择小一点的图片\n2. 拍照时离远一点',
    };
  }

  if (status >= 500) {
    return createDefaultError('network');
  }

  // 如果 API 返回了具体的错误信息，尝试分类
  if (apiError) {
    return handleError(apiError);
  }

  return createDefaultError('unknown');
}
