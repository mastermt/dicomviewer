from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget


class HomeView(QWidget):
    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator

        layout = QVBoxLayout(self)
        layout.addStretch(1)

        self.logo_label = QLabel(self)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setPixmap(self._load_logo_pixmap())

        self.title_label = QLabel(self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 22px; font-weight: 700;")

        self.subtitle_label = QLabel(self)
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setStyleSheet("font-size: 14px; color: #555;")

        layout.addWidget(self.logo_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        layout.addStretch(1)
        self.update_language()

    def _load_logo_pixmap(self):
        assets_path = Path(__file__).resolve().parents[3] / "assets"
        for name in ("logo.svg", "logo.png"):
            logo_path = assets_path / name
            if logo_path.exists():
                pixmap = QPixmap(str(logo_path))
                if not pixmap.isNull():
                    return pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return self._build_logo_pixmap()

    def _build_logo_pixmap(self):
        size = 160
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)

        painter.setBrush(QColor("#2563eb"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(10, 10, 140, 140)

        painter.setBrush(QColor("#ffffff"))
        painter.drawRoundedRect(46, 44, 68, 74, 10, 10)

        painter.setBrush(QColor("#93c5fd"))
        painter.drawRect(58, 58, 44, 10)
        painter.drawRect(58, 76, 44, 10)
        painter.drawRect(58, 94, 28, 10)

        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Arial", 16, QFont.Bold))
        painter.drawText(0, 130, size, 22, Qt.AlignCenter, "DICOM")
        painter.end()
        return pixmap

    def update_language(self):
        self.title_label.setText(self.translator.get("home_title"))
        self.subtitle_label.setText(self.translator.get("home_subtitle"))

