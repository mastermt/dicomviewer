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
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt


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

        self.image_label = QLabel(central_widget)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("Nenhuma imagem carregada.")
        layout.addWidget(self.image_label, 1)

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
                self.image_label.setText(f"Error loading DICOM: {e}")
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
        self.image_label.setPixmap(
            self.current_pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_image_display()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = DICOMViewer()
    viewer.show()
    sys.exit(app.exec_())
