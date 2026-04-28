import sys
import numpy as np
import pydicom
from pydicom.pixel_data_handlers.util import apply_voi_lut
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QFileDialog,
    QAction,
    QWidget,
    QVBoxLayout,
    QFrame,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QToolButton,
    QStyle,
)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QKeySequence
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QShortcut


class ImageViewer(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
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

        self.placeholder = QLabel("Nenhuma imagem carregada.", self)
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setStyleSheet("color: #999; font-size: 14px;")

        self.btn_zoom_in = QToolButton(self)
        self.btn_zoom_in.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
        self.btn_zoom_in.setToolTip("Zoom in")
        self.btn_zoom_in.clicked.connect(lambda: self.zoom_image(1.2))

        self.btn_zoom_out = QToolButton(self)
        self.btn_zoom_out.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        self.btn_zoom_out.setToolTip("Zoom out")
        self.btn_zoom_out.clicked.connect(lambda: self.zoom_image(1 / 1.2))

        self.btn_pan = QToolButton(self)
        self.btn_pan.setIcon(self.style().standardIcon(QStyle.SP_ArrowLeft))
        self.btn_pan.setToolTip("Pan: ligado")
        self.btn_pan.setCheckable(True)
        self.btn_pan.setChecked(True)
        self.btn_pan.clicked.connect(self.toggle_pan)

        self.btn_reset = QToolButton(self)
        self.btn_reset.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.btn_reset.setToolTip("Resetar zoom/posicao")
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
        self.setDragMode(
            QGraphicsView.ScrollHandDrag if self.pan_enabled else QGraphicsView.NoDrag
        )
        self.btn_pan.setChecked(self.pan_enabled)
        self.btn_pan.setToolTip("Pan: ligado" if self.pan_enabled else "Pan: desligado")

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


class DICOMViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt DICOM Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.current_pixmap = None

        # Central widget with metadata frame + image
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        info_frame = QFrame(central_widget)
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(8, 8, 8, 8)
        self.info_label = QLabel("Abra um arquivo DICOM para visualizar os metadados.", info_frame)
        self.info_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.info_label.setWordWrap(True)
        self.info_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        info_layout.addWidget(self.info_label)
        layout.addWidget(info_frame, 0)

        self.image_viewer = ImageViewer(central_widget)
        layout.addWidget(self.image_viewer, 1)

        self.setCentralWidget(central_widget)

        # Menu for opening files
        open_action = QAction("Open DICOM", self)
        open_action.triggered.connect(self.open_dicom)
        menu = self.menuBar().addMenu("File")
        menu.addAction(open_action)

    def open_dicom(self):
        """Open a DICOM file and display it."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open DICOM File", "", "DICOM Files (*.dcm);;All Files (*)"
        )
        if file_path:
            try:
                ds = pydicom.dcmread(file_path)
                self.info_label.setText(self.format_metadata(ds))
                qimage = self.dataset_to_qimage(ds)
                self.current_pixmap = QPixmap.fromImage(qimage)
                self.update_image_display()

            except Exception as e:
                self.image_viewer.placeholder.setText(f"Error loading DICOM: {e}")
                self.image_viewer.placeholder.show()
                self.image_viewer.set_pixmap(QPixmap())
                self.info_label.setText("Falha ao ler metadados do arquivo.")
                self.current_pixmap = None

    def format_metadata(self, ds):
        fields = [
            ("Paciente", "PatientName"),
            ("ID", "PatientID"),
            ("Modalidade", "Modality"),
            ("Estudo", "StudyDescription"),
            ("Série", "SeriesDescription"),
            ("Data", "StudyDate"),
            ("Tamanho", "Rows"),
            ("Colunas", "Columns"),
            ("Bits", "BitsStored"),
            ("Photometric", "PhotometricInterpretation"),
        ]

        lines = []
        for label, attr in fields:
            value = getattr(ds, attr, "N/A")
            lines.append(f"{label}: {value}")
        return "\n".join(lines)

    def dataset_to_qimage(self, ds):
        pixel_array = ds.pixel_array

        if getattr(ds, "SamplesPerPixel", 1) == 1:
            try:
                data = apply_voi_lut(pixel_array, ds)
            except Exception:
                data = pixel_array

            slope = float(getattr(ds, "RescaleSlope", 1))
            intercept = float(getattr(ds, "RescaleIntercept", 0))
            data = data.astype(np.float32) * slope + intercept

            min_val = np.min(data)
            max_val = np.max(data)
            if max_val > min_val:
                data = (data - min_val) * (255.0 / (max_val - min_val))
            else:
                data = np.zeros_like(data, dtype=np.float32)

            img8 = np.clip(data, 0, 255).astype(np.uint8)
            if img8.ndim == 3:
                # Multi-frame: displays only first frame
                img8 = img8[0]

            if getattr(ds, "PhotometricInterpretation", "") == "MONOCHROME1":
                img8 = 255 - img8

            img8 = np.ascontiguousarray(img8)
            height, width = img8.shape
            qimage = QImage(
                img8.data,
                width,
                height,
                img8.strides[0],
                QImage.Format_Grayscale8,
            ).copy()
            return qimage

        data = pixel_array
        if data.ndim == 4:
            data = data[0]
        if data.ndim != 3 or data.shape[2] != 3:
            raise ValueError(f"Formato de imagem não suportado: shape={data.shape}")

        data = data.astype(np.float32)
        min_val = np.min(data)
        max_val = np.max(data)
        if max_val > min_val:
            data = (data - min_val) * (255.0 / (max_val - min_val))
        img8 = np.clip(data, 0, 255).astype(np.uint8)
        img8 = np.ascontiguousarray(img8)

        height, width, _ = img8.shape
        qimage = QImage(
            img8.data,
            width,
            height,
            img8.strides[0],
            QImage.Format_RGB888,
        ).copy()
        return qimage

    def update_image_display(self):
        if not self.current_pixmap:
            return
        self.image_viewer.set_pixmap(self.current_pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.current_pixmap:
            self.image_viewer.reset_view()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = DICOMViewer()
    viewer.show()
    sys.exit(app.exec_())
