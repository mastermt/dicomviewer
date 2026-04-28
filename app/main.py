import sys

from PyQt5.QtWidgets import QApplication

from app.db.database import init_db
from app.ui.main_window import DICOMViewer


def run():
    init_db()
    app = QApplication(sys.argv)
    viewer = DICOMViewer()
    viewer.show()
    sys.exit(app.exec_())

