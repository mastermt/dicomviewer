from PyQt5.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.crud_service import CRUDService


class PatientsView(QWidget):
    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator

        self.selected_patient_id = None

        layout = QVBoxLayout(self)
        self.title_label = QLabel(self)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 600;")

        form_layout = QFormLayout()
        self.full_name_input = QLineEdit(self)
        self.patient_code_input = QLineEdit(self)
        self.birth_date_input = QLineEdit(self)
        self.phone_input = QLineEdit(self)
        form_layout.addRow("", self.full_name_input)
        form_layout.addRow("", self.patient_code_input)
        form_layout.addRow("", self.birth_date_input)
        form_layout.addRow("", self.phone_input)

        actions_layout = QHBoxLayout()
        self.create_button = QPushButton(self)
        self.update_button = QPushButton(self)
        self.delete_button = QPushButton(self)
        self.clear_button = QPushButton(self)
        self.refresh_button = QPushButton(self)
        actions_layout.addWidget(self.create_button)
        actions_layout.addWidget(self.update_button)
        actions_layout.addWidget(self.delete_button)
        actions_layout.addWidget(self.clear_button)
        actions_layout.addWidget(self.refresh_button)

        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemSelectionChanged.connect(self._on_table_select)

        layout.addWidget(self.title_label)
        layout.addLayout(form_layout)
        layout.addLayout(actions_layout)
        layout.addWidget(self.table)

        self.form_layout = form_layout
        self.create_button.clicked.connect(self._create_patient)
        self.update_button.clicked.connect(self._update_patient)
        self.delete_button.clicked.connect(self._delete_patient)
        self.clear_button.clicked.connect(self._clear_form)
        self.refresh_button.clicked.connect(self.refresh_data)
        self.update_language()
        self.refresh_data()

    def update_language(self):
        self.title_label.setText(self.translator.get("patients_module_title"))
        self.form_layout.labelForField(self.full_name_input).setText(
            self.translator.get("patients_field_full_name")
        )
        self.form_layout.labelForField(self.patient_code_input).setText(
            self.translator.get("patients_field_code")
        )
        self.form_layout.labelForField(self.birth_date_input).setText(
            self.translator.get("patients_field_birth_date")
        )
        self.form_layout.labelForField(self.phone_input).setText(
            self.translator.get("patients_field_phone")
        )
        self.create_button.setText(self.translator.get("crud_create"))
        self.update_button.setText(self.translator.get("crud_update"))
        self.delete_button.setText(self.translator.get("crud_delete"))
        self.clear_button.setText(self.translator.get("crud_clear"))
        self.refresh_button.setText(self.translator.get("crud_refresh"))
        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                self.translator.get("patients_field_full_name"),
                self.translator.get("patients_field_code"),
                self.translator.get("patients_field_birth_date"),
                self.translator.get("patients_field_phone"),
            ]
        )

    def refresh_data(self):
        patients = CRUDService.list_patients()
        self.table.setRowCount(len(patients))
        for row, patient in enumerate(patients):
            self.table.setItem(row, 0, QTableWidgetItem(str(patient.id)))
            self.table.setItem(row, 1, QTableWidgetItem(patient.full_name or ""))
            self.table.setItem(row, 2, QTableWidgetItem(patient.patient_code or ""))
            self.table.setItem(row, 3, QTableWidgetItem(patient.birth_date or ""))
            self.table.setItem(row, 4, QTableWidgetItem(patient.phone or ""))
        self.table.resizeColumnsToContents()

    def _collect_data(self):
        return {
            "full_name": self.full_name_input.text().strip(),
            "patient_code": self.patient_code_input.text().strip(),
            "birth_date": self.birth_date_input.text().strip() or None,
            "phone": self.phone_input.text().strip() or None,
        }

    def _validate_required(self, data):
        if not data["full_name"] or not data["patient_code"]:
            QMessageBox.warning(
                self,
                self.translator.get("crud_validation_title"),
                self.translator.get("crud_required_fields"),
            )
            return False
        return True

    def _create_patient(self):
        data = self._collect_data()
        if not self._validate_required(data):
            return
        try:
            CRUDService.create_patient(data)
            self.refresh_data()
            self._clear_form()
        except ValueError:
            QMessageBox.warning(
                self,
                self.translator.get("crud_validation_title"),
                self.translator.get("crud_duplicate"),
            )

    def _update_patient(self):
        if self.selected_patient_id is None:
            QMessageBox.warning(
                self,
                self.translator.get("crud_validation_title"),
                self.translator.get("crud_select_record"),
            )
            return
        data = self._collect_data()
        if not self._validate_required(data):
            return
        try:
            CRUDService.update_patient(self.selected_patient_id, data)
            self.refresh_data()
            self._clear_form()
        except ValueError:
            QMessageBox.warning(
                self,
                self.translator.get("crud_validation_title"),
                self.translator.get("crud_duplicate"),
            )

    def _delete_patient(self):
        if self.selected_patient_id is None:
            QMessageBox.warning(
                self,
                self.translator.get("crud_validation_title"),
                self.translator.get("crud_select_record"),
            )
            return
        confirm = QMessageBox.question(
            self,
            self.translator.get("crud_delete"),
            self.translator.get("crud_confirm_delete"),
        )
        if confirm != QMessageBox.Yes:
            return
        CRUDService.delete_patient(self.selected_patient_id)
        self.refresh_data()
        self._clear_form()

    def _on_table_select(self):
        items = self.table.selectedItems()
        if not items:
            return
        row = items[0].row()
        self.selected_patient_id = int(self.table.item(row, 0).text())
        self.full_name_input.setText(self.table.item(row, 1).text())
        self.patient_code_input.setText(self.table.item(row, 2).text())
        self.birth_date_input.setText(self.table.item(row, 3).text())
        self.phone_input.setText(self.table.item(row, 4).text())

    def _clear_form(self):
        self.selected_patient_id = None
        self.full_name_input.clear()
        self.patient_code_input.clear()
        self.birth_date_input.clear()
        self.phone_input.clear()
        self.table.clearSelection()

