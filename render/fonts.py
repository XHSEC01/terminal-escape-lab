"""截图用字体：优先微软雅黑等 CJK 字体，避免 Consolas 把中文画成方框。"""
from PIL import ImageFont

CJK_FONTS = [
    (r"C:\Windows\Fonts\msyh.ttc", 0),
    (r"C:\Windows\Fonts\msyhbd.ttc", 0),
    (r"C:\Windows\Fonts\simhei.ttf", 0),
    (r"C:\Windows\Fonts\Deng.ttf", 0),
    (r"C:\Windows\Fonts\simsun.ttc", 0),
]


def load_font(size=16):
    for path, index in CJK_FONTS:
        try:
            return ImageFont.truetype(path, size=size, index=index)
        except Exception:
            continue
    return ImageFont.load_default()
