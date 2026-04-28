import re

from PyQt5.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
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
        self.current_page = 1
        self.page_size = 10
        self.total_rows = 0

        layout = QVBoxLayout(self)
        self.title_label = QLabel(self)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 600;")

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit(self)
        self.search_button = QPushButton(self)
        self.search_clear_button = QPushButton(self)
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.search_clear_button)

        form_layout = QFormLayout()
        self.full_name_label = QLabel(self)
        self.full_name_input = QLineEdit(self)
        self.crm_label = QLabel(self)
        self.crm_input = QLineEdit(self)
        self.specialty_label = QLabel(self)
        self.specialty_input = QLineEdit(self)
        self.phone_label = QLabel(self)
        self.phone_input = QLineEdit(self)
        form_layout.addRow(self.full_name_label, self.full_name_input)
        form_layout.addRow(self.crm_label, self.crm_input)
        form_layout.addRow(self.specialty_label, self.specialty_input)
        form_layout.addRow(self.phone_label, self.phone_input)

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

        pagination_layout = QHBoxLayout()
        self.prev_page_button = QPushButton(self)
        self.next_page_button = QPushButton(self)
        self.page_label = QLabel(self)
        self.page_size_label = QLabel(self)
        self.page_size_spin = QSpinBox(self)
        self.page_size_spin.setRange(5, 100)
        self.page_size_spin.setSingleStep(5)
        self.page_size_spin.setValue(self.page_size)
        pagination_layout.addWidget(self.prev_page_button)
        pagination_layout.addWidget(self.next_page_button)
        pagination_layout.addWidget(self.page_label, 1)
        pagination_layout.addWidget(self.page_size_label)
        pagination_layout.addWidget(self.page_size_spin)

        layout.addWidget(self.title_label)
        layout.addLayout(search_layout)
        layout.addLayout(form_layout)
        layout.addLayout(actions_layout)
        layout.addWidget(self.table)
        layout.addLayout(pagination_layout)

        self.form_layout = form_layout
        self.create_button.clicked.connect(self._create_doctor)
        self.update_button.clicked.connect(self._update_doctor)
        self.delete_button.clicked.connect(self._delete_doctor)
        self.clear_button.clicked.connect(self._clear_form)
        self.refresh_button.clicked.connect(self.refresh_data)
        self.search_button.clicked.connect(self._apply_search)
        self.search_clear_button.clicked.connect(self._clear_search)
        self.prev_page_button.clicked.connect(self._go_prev_page)
        self.next_page_button.clicked.connect(self._go_next_page)
        self.page_size_spin.valueChanged.connect(self._on_page_size_change)
        self.update_language()
        self.refresh_data()

    def update_language(self):
        self.title_label.setText(self.translator.get("doctors_module_title"))
        self.full_name_label.setText(self.translator.get("doctors_field_full_name"))
        self.crm_label.setText(self.translator.get("doctors_field_crm"))
        self.specialty_label.setText(self.translator.get("doctors_field_specialty"))
        self.phone_label.setText(self.translator.get("doctors_field_phone"))
        self.create_button.setText(self.translator.get("crud_create"))
        self.update_button.setText(self.translator.get("crud_update"))
        self.delete_button.setText(self.translator.get("crud_delete"))
        self.clear_button.setText(self.translator.get("crud_clear"))
        self.refresh_button.setText(self.translator.get("crud_refresh"))
        self.search_input.setPlaceholderText(self.translator.get("crud_search_placeholder"))
        self.search_button.setText(self.translator.get("crud_search"))
        self.search_clear_button.setText(self.translator.get("crud_search_clear"))
        self.prev_page_button.setText(self.translator.get("crud_prev_page"))
        self.next_page_button.setText(self.translator.get("crud_next_page"))
        self.page_size_label.setText(self.translator.get("crud_page_size"))
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
        doctors, total = CRUDService.list_doctors(
            search_text=self.search_input.text().strip(),
            page=self.current_page,
            page_size=self.page_size,
        )
        self.total_rows = total
        self.table.setRowCount(len(doctors))
        for row, doctor in enumerate(doctors):
            self.table.setItem(row, 0, QTableWidgetItem(str(doctor.id)))
            self.table.setItem(row, 1, QTableWidgetItem(doctor.full_name or ""))
            self.table.setItem(row, 2, QTableWidgetItem(doctor.crm or ""))
            self.table.setItem(row, 3, QTableWidgetItem(doctor.specialty or ""))
            self.table.setItem(row, 4, QTableWidgetItem(doctor.phone or ""))
        self.table.resizeColumnsToContents()
        total_pages = max(1, (self.total_rows + self.page_size - 1) // self.page_size)
        self.page_label.setText(
            self.translator.get("crud_page_status").format(
                page=self.current_page, total_pages=total_pages, total=self.total_rows
            )
        )
        self.prev_page_button.setEnabled(self.current_page > 1)
        self.next_page_button.setEnabled(self.current_page < total_pages)

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

    def _validate_optional_fields(self, data):
        phone = data["phone"]
        if phone and not re.fullmatch(r"[0-9()+\- ]{8,20}", phone):
            QMessageBox.warning(
                self,
                self.translator.get("crud_validation_title"),
                self.translator.get("crud_invalid_phone"),
            )
            return False
        return True

    def _create_doctor(self):
        data = self._collect_data()
        if not self._validate_required(data) or not self._validate_optional_fields(data):
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
        if not self._validate_required(data) or not self._validate_optional_fields(data):
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

    def _apply_search(self):
        self.current_page = 1
        self.refresh_data()

    def _clear_search(self):
        self.search_input.clear()
        self.current_page = 1
        self.refresh_data()

    def _go_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_data()

    def _go_next_page(self):
        total_pages = max(1, (self.total_rows + self.page_size - 1) // self.page_size)
        if self.current_page < total_pages:
            self.current_page += 1
            self.refresh_data()

    def _on_page_size_change(self, value):
        self.page_size = value
        self.current_page = 1
        self.refresh_data()

