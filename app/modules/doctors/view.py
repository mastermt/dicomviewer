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


class DoctorsView(QWidget):
    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator

        self.selected_doctor_id = None

        layout = QVBoxLayout(self)
        self.title_label = QLabel(self)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 600;")

        form_layout = QFormLayout()
        self.full_name_input = QLineEdit(self)
        self.crm_input = QLineEdit(self)
        self.specialty_input = QLineEdit(self)
        self.phone_input = QLineEdit(self)
        form_layout.addRow("", self.full_name_input)
        form_layout.addRow("", self.crm_input)
        form_layout.addRow("", self.specialty_input)
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
        self.create_button.clicked.connect(self._create_doctor)
        self.update_button.clicked.connect(self._update_doctor)
        self.delete_button.clicked.connect(self._delete_doctor)
        self.clear_button.clicked.connect(self._clear_form)
        self.refresh_button.clicked.connect(self.refresh_data)
        self.update_language()
        self.refresh_data()

    def update_language(self):
        self.title_label.setText(self.translator.get("doctors_module_title"))
        self.form_layout.labelForField(self.full_name_input).setText(
            self.translator.get("doctors_field_full_name")
        )
        self.form_layout.labelForField(self.crm_input).setText(
            self.translator.get("doctors_field_crm")
        )
        self.form_layout.labelForField(self.specialty_input).setText(
            self.translator.get("doctors_field_specialty")
        )
        self.form_layout.labelForField(self.phone_input).setText(
            self.translator.get("doctors_field_phone")
        )
        self.create_button.setText(self.translator.get("crud_create"))
        self.update_button.setText(self.translator.get("crud_update"))
        self.delete_button.setText(self.translator.get("crud_delete"))
        self.clear_button.setText(self.translator.get("crud_clear"))
        self.refresh_button.setText(self.translator.get("crud_refresh"))
        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                self.translator.get("doctors_field_full_name"),
                self.translator.get("doctors_field_crm"),
                self.translator.get("doctors_field_specialty"),
                self.translator.get("doctors_field_phone"),
            ]
        )

    def refresh_data(self):
        doctors = CRUDService.list_doctors()
        self.table.setRowCount(len(doctors))
        for row, doctor in enumerate(doctors):
            self.table.setItem(row, 0, QTableWidgetItem(str(doctor.id)))
            self.table.setItem(row, 1, QTableWidgetItem(doctor.full_name or ""))
            self.table.setItem(row, 2, QTableWidgetItem(doctor.crm or ""))
            self.table.setItem(row, 3, QTableWidgetItem(doctor.specialty or ""))
            self.table.setItem(row, 4, QTableWidgetItem(doctor.phone or ""))
        self.table.resizeColumnsToContents()

    def _collect_data(self):
        return {
            "full_name": self.full_name_input.text().strip(),
            "crm": self.crm_input.text().strip(),
            "specialty": self.specialty_input.text().strip() or None,
            "phone": self.phone_input.text().strip() or None,
        }

    def _validate_required(self, data):
        if not data["full_name"] or not data["crm"]:
            QMessageBox.warning(
                self,
                self.translator.get("crud_validation_title"),
                self.translator.get("crud_required_fields"),
            )
            return False
        return True

    def _create_doctor(self):
        data = self._collect_data()
        if not self._validate_required(data):
            return
        try:
            CRUDService.create_doctor(data)
            self.refresh_data()
            self._clear_form()
        except ValueError:
            QMessageBox.warning(
                self,
                self.translator.get("crud_validation_title"),
                self.translator.get("crud_duplicate"),
            )

    def _update_doctor(self):
        if self.selected_doctor_id is None:
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
            CRUDService.update_doctor(self.selected_doctor_id, data)
            self.refresh_data()
            self._clear_form()
        except ValueError:
            QMessageBox.warning(
                self,
                self.translator.get("crud_validation_title"),
                self.translator.get("crud_duplicate"),
            )

    def _delete_doctor(self):
        if self.selected_doctor_id is None:
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
        CRUDService.delete_doctor(self.selected_doctor_id)
        self.refresh_data()
        self._clear_form()

    def _on_table_select(self):
        items = self.table.selectedItems()
        if not items:
            return
        row = items[0].row()
        self.selected_doctor_id = int(self.table.item(row, 0).text())
        self.full_name_input.setText(self.table.item(row, 1).text())
        self.crm_input.setText(self.table.item(row, 2).text())
        self.specialty_input.setText(self.table.item(row, 3).text())
        self.phone_input.setText(self.table.item(row, 4).text())

    def _clear_form(self):
        self.selected_doctor_id = None
        self.full_name_input.clear()
        self.crm_input.clear()
        self.specialty_input.clear()
        self.phone_input.clear()
        self.table.clearSelection()

