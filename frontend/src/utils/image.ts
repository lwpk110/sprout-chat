/**
 * 图片处理工具
 * 基于 browser-image-compression 实现图片压缩
 */

import imageCompression from 'browser-image-compression';

/**
 * 压缩配置
 */
const COMPRESSION_OPTIONS = {
  maxSizeMB: 1,
  maxWidthOrHeight: 1920,
  useWebWorker: true,
  fileType: 'image/jpeg',
  quality: 0.8,
};

/**
 * 压缩图片文件
 * @param file 原始图片文件
 * @returns 压缩后的图片文件
 *
 * @example
 * const compressedFile = await compressImage(file);
 * console.log(`Original size: ${file.size} bytes`);
 * console.log(`Compressed size: ${compressedFile.size} bytes`);
 */
export async function compressImage(file: File): Promise<File> {
  try {
    const compressedFile = await imageCompression(file, COMPRESSION_OPTIONS);

    console.log(`Image compressed: ${file.size} → ${compressedFile.size} bytes`);

    return compressedFile;
  } catch (error) {
    console.error('Image compression failed:', error);
    throw new Error('图片压缩失败，请重试');
  }
}

/**
 * 将图片文件转换为 Base64
 * @param file 图片文件
 * @returns Base64 字符串（带 data URL 前缀）
 */
export async function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      resolve(reader.result as string);
    };
    reader.onerror = () => {
      reject(new Error('图片读取失败'));
    };
    reader.readAsDataURL(file);
  });
}

/**
 * 验证图片文件类型
 * @param file 文件对象
 * @returns 是否为支持的图片类型
 */
export function isValidImageType(file: File): boolean {
  const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
  return validTypes.includes(file.type);
}

/**
 * 验证图片文件大小
 * @param file 文件对象
 * @param maxSizeMB 最大大小（MB）
 * @returns 是否在大小限制内
 */
export function isValidImageSize(file: File, maxSizeMB: number = 10): boolean {
  const maxSizeBytes = maxSizeMB * 1024 * 1024;
  return file.size <= maxSizeBytes;
}

/**
 * 获取图片尺寸
 * @param file 图片文件
 * @returns 图片宽高
 */
export async function getImageDimensions(file: File): Promise<{ width: number; height: number }> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      resolve({ width: img.width, height: img.height });
    };
    img.onerror = () => {
      reject(new Error('无法读取图片尺寸'));
    };
    img.src = URL.createObjectURL(file);
  });
}

/**
 * 简单的模糊检测（基于图片尺寸）
 * 注意：这只是简单启发式检测，真正的模糊检测需要更复杂的算法
 * @param file 图片文件
 * @returns 是否可能模糊
 */
export async function isLikelyBlurry(file: File): Promise<boolean> {
  try {
    const dimensions = await getImageDimensions(file);
    const minDimension = Math.min(dimensions.width, dimensions.height);

    // 如果最小边小于 500px，可能模糊
    return minDimension < 500;
  } catch {
    return false;
  }
}

/**
 * 生成图片预览URL
 * @param file 图片文件
 * @returns 预览URL（需要手动释放）
 */
export function createPreviewUrl(file: File): string {
  return URL.createObjectURL(file);
}

/**
 * 释放预览URL
 * @param url 预览URL
 */
export function revokePreviewUrl(url: string): void {
  URL.revokeObjectURL(url);
}

/**
 * 完整的图片上传前处理流程
 * @param file 原始文件
 * @returns 处理后的文件
 * @throws 如果验证失败
 */
export async function prepareImageForUpload(file: File): Promise<File> {
  // 1. 验证类型
  if (!isValidImageType(file)) {
    throw new Error('不支持的图片格式，请使用 JPG、PNG 或 WebP');
  }

  // 2. 验证大小
  if (!isValidImageSize(file, 10)) {
    throw new Error('图片太大，请选择小于 10MB 的图片');
  }

  // 3. 压缩图片
  const compressed = await compressImage(file);

  return compressed;
}
