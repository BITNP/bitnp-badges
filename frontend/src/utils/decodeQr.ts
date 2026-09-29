import jsQR from 'jsqr'

// 识别前允许的最大边长，避免超大图片带来的性能问题
const MAX_SCAN_DIMENSION = 1600
// 图片较小时尝试放大的阈值，提高小二维码的识别率
const UPSCALE_THRESHOLD = 512

interface ScanSize {
  width: number
  height: number
}

function computeScanSizes(naturalWidth: number, naturalHeight: number): ScanSize[] {
  const sizes: ScanSize[] = []

  const push = (width: number, height: number) => {
    const next: ScanSize = {
      width: Math.max(1, Math.round(width)),
      height: Math.max(1, Math.round(height)),
    }
    if (!sizes.some((size) => size.width === next.width && size.height === next.height)) {
      sizes.push(next)
    }
  }

  const longest = Math.max(naturalWidth, naturalHeight)
  const scale = Math.min(1, MAX_SCAN_DIMENSION / longest)

  push(naturalWidth * scale, naturalHeight * scale)
  push(naturalWidth, naturalHeight)

  if (longest <= UPSCALE_THRESHOLD) {
    push(naturalWidth * 2, naturalHeight * 2)
  }

  return sizes
}

function loadImage(url: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image()
    image.onload = () => resolve(image)
    image.onerror = () => reject(new Error('图片加载失败，请确认上传的是有效的图片文件。'))
    image.src = url
  })
}

function scanImage(image: HTMLImageElement, width: number, height: number): string | null {
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height

  const context = canvas.getContext('2d', { willReadFrequently: true })
  if (!context) {
    throw new Error('当前浏览器不支持 Canvas，无法识别图片中的二维码。')
  }

  context.drawImage(image, 0, 0, width, height)
  const imageData = context.getImageData(0, 0, width, height)
  const result = jsQR(imageData.data, imageData.width, imageData.height, {
    inversionAttempts: 'attemptBoth',
  })

  return result ? result.data : null
}

/**
 * 从图片文件中识别二维码，返回二维码中的文本内容
 * @param file 用户上传的图片文件
 * @returns 二维码中解码出的字符串
 */
export async function decodeQrFromImage(file: File): Promise<string> {
  const objectUrl = URL.createObjectURL(file)

  try {
    const image = await loadImage(objectUrl)
    const naturalWidth = image.naturalWidth || image.width
    const naturalHeight = image.naturalHeight || image.height

    for (const size of computeScanSizes(naturalWidth, naturalHeight)) {
      const text = scanImage(image, size.width, size.height)
      if (text) {
        return text
      }
    }
  } finally {
    URL.revokeObjectURL(objectUrl)
  }

  throw new Error('未能在图片中识别到二维码，请确认图片中包含清晰、完整的二维码。')
}
