/**
 * ErrorBoundary 组件
 * 捕获子组件树中的 JavaScript 错误，显示友好的错误提示
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error?: Error;
}

/**
 * 错误边界组件
 * 捕获子组件中的错误并显示友好的错误界面
 */
class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    // 调用自定义错误处理函数
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined });
  };

  render() {
    if (this.state.hasError) {
      // 如果提供了自定义 fallback，使用它
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // 默认错误界面
      return (
        <div className="min-h-screen flex items-center justify-center bg-sprout-50 p-4">
          <div className="max-w-md w-full bg-white rounded-2xl shadow-lg p-8 text-center">
            {/* 友好的图标 */}
            <div className="text-6xl mb-4">🌱</div>

            <h1 className="text-sprout-xl font-bold text-sprout-900 mb-4">
              哎呀，小芽遇到问题了
            </h1>

            <p className="text-sprout-base text-sprout-700 mb-6">
              就像小芽有时候会生病一样，程序也会遇到一点小问题。
            </p>

            <div className="bg-sprout-50 rounded-xl p-4 mb-6 text-left">
              <p className="text-sprout-sm text-sprout-800 mb-2">
                <strong>试试这些方法：</strong>
              </p>
              <ul className="text-sprout-sm text-sprout-700 space-y-1">
                <li>1. 刷新页面</li>
                <li>2. 清除浏览器缓存</li>
                <li>3. 告诉爸爸妈妈</li>
              </ul>
            </div>

            {/* 操作按钮 */}
            <button
              onClick={this.handleReset}
              className="w-full bg-sprout-500 hover:bg-sprout-600 text-white font-bold py-4 px-6 rounded-xl text-sprout-lg transition-colors duration-200 mb-3"
            >
              重新开始
            </button>

            <button
              onClick={() => window.location.reload()}
              className="w-full bg-sprout-100 hover:bg-sprout-200 text-sprout-700 font-bold py-4 px-6 rounded-xl text-sprout-lg transition-colors duration-200"
            >
              刷新页面
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
