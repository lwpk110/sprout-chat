/**
 * 时间格式化工具
 * 提供适合一年级学生理解的时间显示
 */

/**
 * 格式化相对时间
 * @param timestamp ISO 8601 时间戳或日期字符串
 * @returns 学生友好的相对时间描述
 *
 * @example
 * formatRelativeTime("2025-01-13T10:00:00") // "刚刚"
 * formatRelativeTime("2025-01-13T09:55:00") // "5分钟前"
 * formatRelativeTime("2025-01-12T10:00:00") // "昨天"
 */
export function formatRelativeTime(timestamp: string): string {
  const now = new Date();
  const date = new Date(timestamp);
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  // 小于1分钟
  if (diffSecs < 60) {
    return '刚刚';
  }

  // 小于1小时
  if (diffMins < 60) {
    return `${diffMins}分钟前`;
  }

  // 小于1天
  if (diffHours < 24) {
    return `${diffHours}小时前`;
  }

  // 小于7天
  if (diffDays < 7) {
    if (diffDays === 1) {
      return '昨天';
    }
    if (diffDays === 2) {
      return '前天';
    }
    return `${diffDays}天前`;
  }

  // 超过7天，显示具体日期
  const month = date.getMonth() + 1;
  const day = date.getDate();
  return `${month}月${day}日`;
}

/**
 * 格式化学习时长
 * @param seconds 秒数
 * @returns 学生友好的时长描述
 *
 * @example
 * formatStudyDuration(90) // "1分30秒"
 * formatStudyDuration(3665) // "1小时1分5秒"
 */
export function formatStudyDuration(seconds: number): string {
  if (seconds < 60) {
    return `${seconds}秒`;
  }

  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  const parts: string[] = [];

  if (hours > 0) {
    parts.push(`${hours}小时`);
  }
  if (minutes > 0) {
    parts.push(`${minutes}分`);
  }
  if (secs > 0 && hours === 0) {
    parts.push(`${secs}秒`);
  }

  return parts.join('');
}

/**
 * 格式化进度百分比
 * @param current 当前值
 * @param total 总值
 * @returns 格式化的百分比字符串
 *
 * @example
 * formatProgress(7, 10) // "70%"
 * formatProgress(0, 10) // "0%"
 */
export function formatProgress(current: number, total: number): string {
  if (total === 0) {
    return '0%';
  }
  const percentage = Math.round((current / total) * 100);
  return `${percentage}%`;
}

/**
 * 格式化数字为中文
 * @param num 数字
 * @returns 中文数字字符串
 *
 * @example
 * formatNumberChinese(1) // "一"
 * formatNumberChinese(10) // "十"
 * formatNumberChinese(100) // "100" // 超过100使用阿拉伯数字
 */
export function formatNumberChinese(num: number): string {
  const chineseNums = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十'];

  if (num <= 10) {
    return chineseNums[num] || num.toString();
  }

  // 超过10使用阿拉伯数字（更适合一年级学生理解）
  return num.toString();
}
