from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QProgressDialog,
    QPushButton,
    QToolButton,
    QVBoxLayout,
)

from main_view_parts.theme import (
    apply_native_title_bar_theme,
    apply_widget_stylesheet,
    generate_application_stylesheet,
    get_current_theme,
    get_current_theme_colors,
)


def _global_progress_stylesheet() -> str:
    app = QApplication.instance()
    return app.styleSheet() if app is not None else generate_application_stylesheet(get_current_theme())


def _progress_dialog_stylesheet() -> str:
    colors = get_current_theme_colors()
    t = {
        **colors,
        "bg_dialog": colors.get("bg_dropdown", "#0E1428"),
        "border": colors.get("border_input", "rgba(255, 255, 255, 0.12)"),
        "fg": colors.get("text_primary", "#E2E8F0"),
        "fg_muted": colors.get("text_muted", "#64748B"),
        "soft_bg": colors.get("btn_soft_bg", "rgba(255, 255, 255, 0.06)"),
        "soft_hover": colors.get("btn_soft_hover", "rgba(255, 255, 255, 0.12)"),
        "soft_pressed": colors.get("btn_soft_pressed", "rgba(255, 255, 255, 0.18)"),
        "soft_border": colors.get("btn_soft_border", "rgba(255, 255, 255, 0.08)"),
        "soft_text": colors.get("btn_soft_text", "#E2E8F0"),
    }

    cta_gradient_start = t.get("cta_gradient_start", t.get("btn_primary_bg", "#4F46E5"))
    cta_gradient_end = t.get("cta_gradient_end", t.get("btn_primary_bg", "#4F46E5"))

    return f"""
        QFrame#progressDialogContainer {{
            background: {t["bg_dialog"]};
            border: 1px solid {t["border"]};
            border-radius: 14px;
        }}
        QLabel#progressDialogLabel {{
            background: transparent;
            color: {t["fg"]};
            font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
            font-size: 12px;
            line-height: 1.4;
        }}
        QWidget#dialogHeader {{
            background: transparent;
        }}
        QLabel#dialogWindowTitle {{
            color: {t["fg"]};
            font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
            font-size: 12px;
            font-weight: 600;
        }}
        QToolButton#dialogCloseButton {{
            background: transparent;
            border: none;
            border-radius: 8px;
            color: {t["fg_muted"]};
            font-size: 16px;
            font-weight: 600;
            min-width: 28px;
            min-height: 28px;
            padding: 0;
        }}
        QToolButton#dialogCloseButton:hover {{
            background: {t["soft_bg"]};
            color: {t["fg"]};
        }}
        QToolButton#dialogCloseButton:pressed {{
            background: {t["soft_pressed"]};
        }}
        QProgressBar#progressDialogBar {{
            border: none;
            background: {t["border"]};
            height: 6px;
            border-radius: 3px;
        }}
        QProgressBar#progressDialogBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 {cta_gradient_start}, stop:1 {cta_gradient_end});
            border-radius: 3px;
        }}
        QPushButton#progressDialogCancelButton {{
            min-width: 80px;
            min-height: 28px;
            border-radius: 8px;
            padding: 4px 12px;
            font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
            font-size: 12px;
            font-weight: 500;
            background: {t["soft_bg"]};
            border: 1px solid {t["soft_border"]};
            color: {t["soft_text"]};
        }}
        QPushButton#progressDialogCancelButton:hover {{
            background: {t["soft_hover"]};
            border-color: {t["border"]};
        }}
        QPushButton#progressDialogCancelButton:pressed {{
            background: {t["soft_pressed"]};
        }}
    """


class ThemedProgressDialog(QProgressDialog):
    def __init__(self, label_text: str, cancel_button_text: str | None, parent=None):
        super().__init__(label_text, cancel_button_text, 0, 0, parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setMinimumDuration(0)

        # Extract children
        self.label = self.findChild(QLabel)
        self.progress_bar = self.findChild(QProgressBar)
        self.cancel_button = self.findChild(QPushButton)

        # Top-level layout for drop shadow padding
        top_layout = QVBoxLayout(self)
        top_layout.setContentsMargins(12, 12, 12, 12)
        top_layout.setSpacing(0)

        # Styled container
        self.container = QFrame(self)
        self.container.setObjectName("progressDialogContainer")
        top_layout.addWidget(self.container)

        # Drop shadow on the container
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 90))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)

        # Container layout
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(12)

        # Header / Title Bar
        self.header = QFrame(self.container)
        self.header.setObjectName("dialogHeader")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        self.title_label = QLabel(self.windowTitle(), self.header)
        self.title_label.setObjectName("dialogWindowTitle")
        self.title_label.setTextFormat(Qt.TextFormat.PlainText)
        header_layout.addWidget(self.title_label, 1)

        self.close_button = QToolButton(self.header)
        self.close_button.setObjectName("dialogCloseButton")
        self.close_button.setText("×")
        self.close_button.setAutoRaise(True)
        self.close_button.clicked.connect(self.cancel)
        header_layout.addWidget(self.close_button)

        layout.addWidget(self.header)

        # Add Label
        if self.label is not None:
            self.label.setParent(self.container)
            self.label.setObjectName("progressDialogLabel")
            self.label.setWordWrap(True)
            self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            layout.addWidget(self.label)

        # Add Progress Bar
        if self.progress_bar is not None:
            self.progress_bar.setParent(self.container)
            self.progress_bar.setObjectName("progressDialogBar")
            self.progress_bar.setTextVisible(False)
            self.progress_bar.setFixedHeight(8)
            layout.addWidget(self.progress_bar)

        # Add Cancel Button
        if self.cancel_button is not None:
            self.cancel_button.setParent(self.container)
            self.cancel_button.setObjectName("progressDialogCancelButton")

            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(0, 4, 0, 0)
            btn_layout.addStretch()
            btn_layout.addWidget(self.cancel_button)
            layout.addLayout(btn_layout)

        # Apply stylesheet
        apply_widget_stylesheet(self, _progress_dialog_stylesheet())

        # Size settings
        self.setMinimumWidth(400)
        self.setMinimumHeight(150)
        self.adjustSize()

    def setWindowTitle(self, title: str):
        super().setWindowTitle(title)
        if hasattr(self, "title_label") and self.title_label is not None:
            self.title_label.setText(title)

    def resizeEvent(self, event):
        QDialog.resizeEvent(self, event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, "_drag_position"):
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)


def apply_progress_dialog_style(dialog: QProgressDialog) -> QProgressDialog:
    if isinstance(dialog, ThemedProgressDialog):
        return dialog

    dialog.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    dialog.setWindowModality(Qt.WindowModality.WindowModal)
    dialog.setMinimumWidth(360)
    dialog.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
    apply_widget_stylesheet(dialog, _global_progress_stylesheet())
    QTimer.singleShot(0, lambda: apply_native_title_bar_theme(dialog, get_current_theme()))

    progress_bar = dialog.findChild(QProgressBar)
    if progress_bar is not None:
        progress_bar.setTextVisible(False)

    return dialog


def create_progress_dialog(parent, title: str, label_text: str, cancel_button_text: str | None = None) -> QProgressDialog:
    dialog = ThemedProgressDialog(label_text, cancel_button_text, parent)
    dialog.setWindowTitle(title)
    if cancel_button_text is None:
        dialog.setCancelButton(None)
    return dialog
