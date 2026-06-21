"""跨平台等宽字体；避免在 macOS 上硬编码 Consolas 触发 Qt 字体别名警告。"""

from __future__ import annotations

from PyQt6.QtGui import QFont, QFontDatabase


def monospace_qfont(point_size: int = 11) -> QFont:
    """
    优先使用系统固定宽度字体（FixedFont），再按常见等宽字体族名回退。
    """
    try:
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        fam = font.family()
        if fam:
            font.setPointSize(point_size)
            return font
    except Exception:
        pass

    families = set(QFontDatabase.families())
    for name in (
        "Menlo",
        "Monaco",
        "Consolas",
        "Courier New",
        "Liberation Mono",
        "DejaVu Sans Mono",
        "monospace",
    ):
        if name in families:
            return QFont(name, point_size)

    f = QFont()
    f.setStyleHint(QFont.StyleHint.Monospace)
    f.setPointSize(point_size)
    return f
