"""
OfflineVoiceLogger アイコン生成スクリプト
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """アプリケーションアイコンを作成"""

    # 複数のサイズを生成（ICOファイル用）
    sizes = [256, 128, 64, 48, 32, 16]
    images = []

    for size in sizes:
        # 新しい画像を作成（RGBA）
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # マイクのアイコンを描画
        # 背景円（青色のグラデーション）
        margin = size // 10
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=(33, 150, 243, 255),  # Material Blue
            outline=(25, 118, 210, 255),
            width=max(1, size // 32)
        )

        # マイクの本体（白色）
        mic_width = size // 4
        mic_height = size // 2.5
        mic_x = (size - mic_width) // 2
        mic_y = size // 4

        # マイクの上部（丸み）
        draw.ellipse(
            [mic_x, mic_y, mic_x + mic_width, mic_y + mic_width],
            fill=(255, 255, 255, 255),
            outline=(200, 200, 200, 255),
            width=max(1, size // 64)
        )

        # マイクの本体（長方形）
        draw.rectangle(
            [mic_x, mic_y + mic_width // 2, mic_x + mic_width, mic_y + mic_height],
            fill=(255, 255, 255, 255),
            outline=(200, 200, 200, 255),
            width=max(1, size // 64)
        )

        # マイクの下部（台座）
        stand_y = mic_y + mic_height
        stand_height = size // 8
        draw.line(
            [size // 2, stand_y, size // 2, stand_y + stand_height],
            fill=(255, 255, 255, 255),
            width=max(2, size // 16)
        )

        # 台座の底
        base_width = size // 3
        draw.line(
            [size // 2 - base_width // 2, stand_y + stand_height,
             size // 2 + base_width // 2, stand_y + stand_height],
            fill=(255, 255, 255, 255),
            width=max(2, size // 16)
        )

        # 音波のアクセント
        wave_offset = size // 6
        wave_length = size // 10
        for i in range(2):
            offset = wave_offset + i * (size // 15)
            # 左側の音波
            draw.arc(
                [mic_x - offset, mic_y + mic_height // 3,
                 mic_x - offset + wave_length, mic_y + mic_height // 3 + wave_length],
                start=300, end=60,
                fill=(255, 255, 255, 200),
                width=max(1, size // 48)
            )
            # 右側の音波
            draw.arc(
                [mic_x + mic_width + offset - wave_length, mic_y + mic_height // 3,
                 mic_x + mic_width + offset, mic_y + mic_height // 3 + wave_length],
                start=120, end=240,
                fill=(255, 255, 255, 200),
                width=max(1, size // 48)
            )

        images.append(img)

    # ICOファイルとして保存
    icon_path = 'app_icon.ico'
    images[0].save(
        icon_path,
        format='ICO',
        sizes=[(img.width, img.height) for img in images]
    )

    print(f"[OK] アイコンを作成しました: {icon_path}")
    print(f"  含まれるサイズ: {sizes}")

    # PNG版も保存（プレビュー用）
    images[0].save('app_icon.png', format='PNG')
    print(f"[OK] プレビュー用PNGを作成しました: app_icon.png")

    return icon_path

if __name__ == "__main__":
    create_icon()
