from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QPainter
from PyQt5.QtWidgets import (
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QLabel,
    QShortcut,
    QStyle,
    QToolButton,
)


class ImageViewer(QGraphicsView):
    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator

        self.setScene(QGraphicsScene(self))
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene().addItem(self.pixmap_item)

        self.zoom_factor = 1.0
        self.min_zoom = 0.2
        self.max_zoom = 8.0
        self.pan_enabled = True

        self.setRenderHints(self.renderHints() | QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        self.placeholder = QLabel("", self)
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setStyleSheet("color: #999; font-size: 14px;")

        self.btn_zoom_in = QToolButton(self)
        self.btn_zoom_in.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
        self.btn_zoom_in.clicked.connect(lambda: self.zoom_image(1.2))

        self.btn_zoom_out = QToolButton(self)
        self.btn_zoom_out.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        self.btn_zoom_out.clicked.connect(lambda: self.zoom_image(1 / 1.2))

        self.btn_pan = QToolButton(self)
        self.btn_pan.setIcon(self.style().standardIcon(QStyle.SP_ArrowLeft))
        self.btn_pan.setCheckable(True)
        self.btn_pan.setChecked(True)
        self.btn_pan.clicked.connect(self.toggle_pan)

        self.btn_reset = QToolButton(self)
        self.btn_reset.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.btn_reset.clicked.connect(self.reset_view)

        button_style = """
            QToolButton {
                background-color: rgba(40, 40, 40, 180);
                color: white;
                border: 1px solid rgba(255, 255, 255, 120);
                border-radius: 6px;
                min-width: 28px;
                min-height: 28px;
                padding: 2px;
            }
            QToolButton:hover {
                background-color: rgba(60, 60, 60, 220);
            }
            QToolButton:checked {
                background-color: rgba(35, 110, 70, 220);
                border: 1px solid rgba(130, 220, 170, 180);
            }
        """
        self.btn_zoom_in.setStyleSheet(button_style)
        self.btn_zoom_out.setStyleSheet(button_style)
        self.btn_pan.setStyleSheet(button_style)
        self.btn_reset.setStyleSheet(button_style)
        self._controls = [self.btn_zoom_in, self.btn_zoom_out, self.btn_pan, self.btn_reset]
        for btn in self._controls:
            btn.raise_()

        self.shortcut_zoom_in_main = QShortcut(QKeySequence("Ctrl++"), self)
        self.shortcut_zoom_in_main.activated.connect(lambda: self.zoom_image(1.2))
        self.shortcut_zoom_in_alt = QShortcut(QKeySequence("Ctrl+="), self)
        self.shortcut_zoom_in_alt.activated.connect(lambda: self.zoom_image(1.2))
        self.shortcut_zoom_out = QShortcut(QKeySequence("Ctrl+-"), self)
        self.shortcut_zoom_out.activated.connect(lambda: self.zoom_image(1 / 1.2))
        self.shortcut_reset = QShortcut(QKeySequence("R"), self)
        self.shortcut_reset.activated.connect(self.reset_view)
        self.update_language()

    def update_language(self):
        self.placeholder.setText(self.translator.get("placeholder_no_image"))
        self.btn_zoom_in.setToolTip(self.translator.get("tooltip_zoom_in"))
        self.btn_zoom_out.setToolTip(self.translator.get("tooltip_zoom_out"))
        self.btn_reset.setToolTip(self.translator.get("tooltip_reset"))
        self.btn_pan.setToolTip(
            self.translator.get("tooltip_pan_on")
            if self.pan_enabled
            else self.translator.get("tooltip_pan_off")
        )

    def set_pixmap(self, pixmap):
        self.pixmap_item.setPixmap(pixmap)
        self.zoom_factor = 1.0
        self.resetTransform()

        has_image = not pixmap.isNull()
        self.placeholder.setVisible(not has_image)
        if has_image:
            self.scene().setSceneRect(self.pixmap_item.boundingRect())
            self.fitInView(self.pixmap_item, Qt.KeepAspectRatio)
            self.zoom_factor = 1.0
        self._position_overlay()

    def zoom_image(self, step):
        new_zoom = self.zoom_factor * step
        if new_zoom < self.min_zoom or new_zoom > self.max_zoom:
            return
        self.zoom_factor = new_zoom
        self.scale(step, step)
        self._position_overlay()

    def toggle_pan(self):
        self.pan_enabled = not self.pan_enabled
        self.setDragMode(QGraphicsView.ScrollHandDrag if self.pan_enabled else QGraphicsView.NoDrag)
        self.btn_pan.setChecked(self.pan_enabled)
        self.update_language()

    def reset_view(self):
        if self.pixmap_item.pixmap().isNull():
            return
        self.resetTransform()
        self.fitInView(self.pixmap_item, Qt.KeepAspectRatio)
        self.zoom_factor = 1.0
        self._position_overlay()

    def wheelEvent(self, event):
        if self.pixmap_item.pixmap().isNull():
            return
        if event.angleDelta().y() > 0:
            self.zoom_image(1.15)
        else:
            self.zoom_image(1 / 1.15)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_overlay()

    def _position_overlay(self):
        margin = 12
        gap = 8
        view_rect = self.viewport().geometry()
        self.placeholder.setGeometry(view_rect)

        for btn in self._controls:
            btn.adjustSize()
            btn.raise_()

        y = view_rect.top() + margin
        for btn in self._controls:
            x = view_rect.right() - margin - btn.width()
            btn.move(x, y)
            y += btn.height() + gap

