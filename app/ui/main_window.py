import pydicom
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QAction,
    QActionGroup,
    QBoxLayout,
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
from app.modules.home.view import HomeView
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
        self.info_position = "left"

        central_widget = QWidget(self)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(8)

        self.dicom_container = QWidget(central_widget)
        self.main_layout.addWidget(self.dicom_container, 1)

        self.info_frame = QFrame(self.dicom_container)
        self.info_frame.setFrameShape(QFrame.StyledPanel)
        info_layout = QVBoxLayout(self.info_frame)
        info_layout.setContentsMargins(8, 8, 8, 8)
        self.info_label = QLabel("", self.info_frame)
        self.info_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.info_label.setWordWrap(True)
        self.info_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        info_layout.addWidget(self.info_label)

        self.stack = QStackedWidget(self.dicom_container)
        self.home_view = HomeView(self.translator, self.dicom_container)

        viewer_page = QWidget(self.dicom_container)
        viewer_layout = QVBoxLayout(viewer_page)
        viewer_layout.setContentsMargins(0, 0, 0, 0)
        self.image_viewer = ImageViewer(self.translator, viewer_page)
        viewer_layout.addWidget(self.image_viewer)

        self.patients_view = PatientsView(self.translator, self.dicom_container)
        self.doctors_view = DoctorsView(self.translator, self.dicom_container)
        self.stack.addWidget(self.home_view)
        self.stack.addWidget(viewer_page)
        self.stack.addWidget(self.patients_view)
        self.stack.addWidget(self.doctors_view)

        self.dicom_layout = QBoxLayout(QBoxLayout.LeftToRight)
        self.dicom_layout.setContentsMargins(0, 0, 0, 0)
        self.dicom_layout.setSpacing(8)
        self.dicom_layout.addWidget(self.info_frame, 0)
        self.dicom_layout.addWidget(self.stack, 1)
        self.dicom_container.setLayout(self.dicom_layout)
        self._apply_info_position_layout()
        self.setCentralWidget(central_widget)

        self.file_menu = self.menuBar().addMenu("")
        self.open_action = QAction("", self)
        self.open_action.triggered.connect(self.open_dicom)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addSeparator()
        self.exit_action = QAction("", self)
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)

        self.modules_menu = self.menuBar().addMenu("")
        self.module_home_action = QAction("", self)
        self.module_home_action.triggered.connect(lambda: self.show_module("home"))
        self.modules_menu.addAction(self.module_home_action)

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

        self.view_menu = self.menuBar().addMenu("")
        self.info_position_group = QActionGroup(self)
        self.info_position_group.setExclusive(True)

        self.info_position_left_action = QAction("", self)
        self.info_position_left_action.setCheckable(True)
        self.info_position_left_action.triggered.connect(
            lambda: self.set_info_position("left")
        )
        self.info_position_group.addAction(self.info_position_left_action)
        self.view_menu.addAction(self.info_position_left_action)

        self.info_position_top_action = QAction("", self)
        self.info_position_top_action.setCheckable(True)
        self.info_position_top_action.triggered.connect(
            lambda: self.set_info_position("top")
        )
        self.info_position_group.addAction(self.info_position_top_action)
        self.view_menu.addAction(self.info_position_top_action)

        self.set_language("pt")
        self.show_module("home")

    def set_language(self, language):
        self.translator.set_language(language)
        self.setWindowTitle(self.translator.get("window_title"))
        self.file_menu.setTitle(self.translator.get("file_menu"))
        self.open_action.setText(self.translator.get("open_dicom"))
        self.exit_action.setText(self.translator.get("exit_app"))
        self.modules_menu.setTitle(self.translator.get("modules_menu"))
        self.module_home_action.setText(self.translator.get("module_home"))
        self.module_dicom_action.setText(self.translator.get("module_dicom"))
        self.module_patients_action.setText(self.translator.get("module_patients"))
        self.module_doctors_action.setText(self.translator.get("module_doctors"))
        self.language_menu.setTitle(self.translator.get("language_menu"))
        self.lang_pt_action.setText(self.translator.get("lang_pt"))
        self.lang_en_action.setText(self.translator.get("lang_en"))
        self.view_menu.setTitle(self.translator.get("view_menu"))
        self.info_position_left_action.setText(
            self.translator.get("info_position_left")
        )
        self.info_position_top_action.setText(self.translator.get("info_position_top"))
        self.lang_pt_action.setChecked(language == "pt")
        self.lang_en_action.setChecked(language == "en")
        self.info_position_left_action.setChecked(self.info_position == "left")
        self.info_position_top_action.setChecked(self.info_position == "top")
        self.home_view.update_language()
        self.image_viewer.update_language()
        self.patients_view.update_language()
        self.doctors_view.update_language()

        if self.last_metadata_ds is not None:
            self.info_label.setText(self.format_metadata(self.last_metadata_ds))
        else:
            self.info_label.setText(self.translator.get("info_default"))
        self._refresh_open_action_state()

    def _apply_info_position_layout(self):
        if self.info_position == "top":
            self.dicom_layout.setDirection(QBoxLayout.TopToBottom)
            self.info_frame.setMaximumWidth(16777215)
        else:
            self.dicom_layout.setDirection(QBoxLayout.LeftToRight)
            self.info_frame.setMaximumWidth(360)

    def set_info_position(self, position):
        if position not in ("left", "top") or position == self.info_position:
            return
        self.info_position = position
        self._apply_info_position_layout()
        self.info_position_left_action.setChecked(position == "left")
        self.info_position_top_action.setChecked(position == "top")

    def show_module(self, module_name):
        module_map = {"home": 0, "dicom": 1, "patients": 2, "doctors": 3}
        self.stack.setCurrentIndex(module_map[module_name])
        self.info_frame.setVisible(module_name == "dicom")
        self._refresh_open_action_state()

    def _refresh_open_action_state(self):
        self.open_action.setEnabled(self.stack.currentIndex() == 1)

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
        return DICOMService.format_metadata(ds, fields, self.translator.language)

    def update_image_display(self):
        if not self.current_pixmap:
            return
        self.image_viewer.set_pixmap(self.current_pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.current_pixmap and self.stack.currentIndex() == 1:
            self.image_viewer.reset_view()

