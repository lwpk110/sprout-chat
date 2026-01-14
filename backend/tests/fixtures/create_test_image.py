"""
创建测试图片

生成简单的数学题图片用于测试 OCR 功能
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_simple_math_image(text: str, filename: str):
    """
    创建简单的数学题图片

    Args:
        text: 数学题文本，如 "5 + 3 = ?"
        filename: 保存的文件名
    """
    # 创建白色背景图片
    img = Image.new('RGB', (400, 200), color='white')

    # 创建绘图对象
    draw = ImageDraw.Draw(img)

    # 尝试使用系统字体，如果失败则使用默认字体
    try:
        # Linux 系统字体
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 60)
    except:
        # 使用默认字体
        font = ImageFont.load_default()

    # 计算文本位置（居中）
    # 使用 getbbox 获取文本边界框
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    position = ((400 - text_width) // 2, (200 - text_height) // 2)

    # 绘制文本
    draw.text(position, text, fill='black', font=font)

    # 保存图片
    img.save(filename)
    print(f"✓ 创建测试图片: {filename}")


def create_all_test_images():
    """创建所有测试用图片"""
    fixtures_dir = os.path.dirname(os.path.abspath(__file__))

    # 测试用例
    test_cases = [
        ("5 + 3 = ?", "math_addition.png"),
        ("10 - 4 = ?", "math_subtraction.png"),
        ("小明有 5 个苹果", "math_word_problem.png"),
    ]

    for text, filename in test_cases:
        filepath = os.path.join(fixtures_dir, filename)
        create_simple_math_image(text, filepath)


if __name__ == "__main__":
    create_all_test_images()
    print("\n✓ 所有测试图片创建完成！")
