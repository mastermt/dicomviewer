import pydicom
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QAction,
    QFileDialog,
    QFrame,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.i18n.translator import Translator
from app.modules.doctors.view import DoctorsView
from app.modules.patients.view import PatientsView
from app.services.dicom_service import DICOMService
from app.ui.image_viewer import ImageViewer


class DICOMViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.translator = Translator(default_language="pt")
        self.setGeometry(100, 100, 800, 600)

        self.current_pixmap = None
        self.last_metadata_ds = None

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        info_frame = QFrame(central_widget)
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(8, 8, 8, 8)
        self.info_label = QLabel("", info_frame)
        self.info_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.info_label.setWordWrap(True)
        self.info_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        info_layout.addWidget(self.info_label)
        layout.addWidget(info_frame, 0)

        self.stack = QStackedWidget(central_widget)

        viewer_page = QWidget(central_widget)
        viewer_layout = QVBoxLayout(viewer_page)
        viewer_layout.setContentsMargins(0, 0, 0, 0)
        self.image_viewer = ImageViewer(self.translator, viewer_page)
        viewer_layout.addWidget(self.image_viewer)

        self.patients_view = PatientsView(self.translator, central_widget)
        self.doctors_view = DoctorsView(self.translator, central_widget)
        self.stack.addWidget(viewer_page)
        self.stack.addWidget(self.patients_view)
        self.stack.addWidget(self.doctors_view)
        layout.addWidget(self.stack, 1)
        self.setCentralWidget(central_widget)

        self.file_menu = self.menuBar().addMenu("")
        self.open_action = QAction("", self)
        self.open_action.triggered.connect(self.open_dicom)
        self.file_menu.addAction(self.open_action)

        self.modules_menu = self.menuBar().addMenu("")
        self.module_dicom_action = QAction("", self)
        self.module_dicom_action.triggered.connect(lambda: self.show_module("dicom"))
        self.modules_menu.addAction(self.module_dicom_action)

        self.module_patients_action = QAction("", self)
        self.module_patients_action.triggered.connect(lambda: self.show_module("patients"))
        self.modules_menu.addAction(self.module_patients_action)

        self.module_doctors_action = QAction("", self)
        self.module_doctors_action.triggered.connect(lambda: self.show_module("doctors"))
        self.modules_menu.addAction(self.module_doctors_action)

        self.language_menu = self.menuBar().addMenu("")
        self.lang_pt_action = QAction("", self)
        self.lang_pt_action.setCheckable(True)
        self.lang_pt_action.triggered.connect(lambda: self.set_language("pt"))
        self.language_menu.addAction(self.lang_pt_action)

        self.lang_en_action = QAction("", self)
        self.lang_en_action.setCheckable(True)
        self.lang_en_action.triggered.connect(lambda: self.set_language("en"))
        self.language_menu.addAction(self.lang_en_action)

        self.set_language("pt")
        self.show_module("dicom")

    def set_language(self, language):
        self.translator.set_language(language)
        self.setWindowTitle(self.translator.get("window_title"))
        self.file_menu.setTitle(self.translator.get("file_menu"))
        self.open_action.setText(self.translator.get("open_dicom"))
        self.modules_menu.setTitle(self.translator.get("modules_menu"))
        self.module_dicom_action.setText(self.translator.get("module_dicom"))
        self.module_patients_action.setText(self.translator.get("module_patients"))
        self.module_doctors_action.setText(self.translator.get("module_doctors"))
        self.language_menu.setTitle(self.translator.get("language_menu"))
        self.lang_pt_action.setText(self.translator.get("lang_pt"))
        self.lang_en_action.setText(self.translator.get("lang_en"))
        self.lang_pt_action.setChecked(language == "pt")
        self.lang_en_action.setChecked(language == "en")
        self.image_viewer.update_language()
        self.patients_view.update_language()
        self.doctors_view.update_language()

        if self.last_metadata_ds is not None:
            self.info_label.setText(self.format_metadata(self.last_metadata_ds))
        else:
            self.info_label.setText(self.translator.get("info_default"))
        self._refresh_open_action_state()

    def show_module(self, module_name):
        module_map = {"dicom": 0, "patients": 1, "doctors": 2}
        self.stack.setCurrentIndex(module_map[module_name])
        self._refresh_open_action_state()

    def _refresh_open_action_state(self):
        self.open_action.setEnabled(self.stack.currentIndex() == 0)

    def open_dicom(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.translator.get("open_dialog_title"),
            "",
            self.translator.get("open_filter"),
        )
        if not file_path:
            return

        try:
            ds = pydicom.dcmread(file_path)
            self.last_metadata_ds = ds
            self.info_label.setText(self.format_metadata(ds))
            qimage = DICOMService.dataset_to_qimage(
                ds, self.translator.get("unsupported_format")
            )
            self.current_pixmap = QPixmap.fromImage(qimage)
            self.update_image_display()
        except Exception as err:
            self.image_viewer.placeholder.setText(
                self.translator.get("error_loading").format(error=err)
            )
            self.image_viewer.placeholder.show()
            self.image_viewer.set_pixmap(QPixmap())
            self.info_label.setText(self.translator.get("metadata_error"))
            self.current_pixmap = None

    def format_metadata(self, ds):
        fields = self.translator.get("metadata_fields")
        return DICOMService.format_metadata(ds, fields)

    def update_image_display(self):
        if not self.current_pixmap:
            return
        self.image_viewer.set_pixmap(self.current_pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.current_pixmap and self.stack.currentIndex() == 0:
            self.image_viewer.reset_view()

