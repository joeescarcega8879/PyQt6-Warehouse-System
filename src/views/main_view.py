import sys
from pathlib import Path
from PyQt6 import uic
from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QApplication, QComboBox, QMdiSubWindow

from src.common.style_manager import StyleManager

# Base directory for assets — resolves correctly on any OS
_ICONS_DIR = Path(__file__).resolve().parent.parent / "assets" / "icons"


def _icon(filename: str) -> QIcon:
    """Return a QIcon from the icons directory. Safe on any OS."""
    return QIcon(str(_ICONS_DIR / filename))


class MainView(QMainWindow):

    # Signals
    form_material_signal = pyqtSignal()
    form_line_signal = pyqtSignal()
    form_user_signal = pyqtSignal()
    form_receipt_signal = pyqtSignal()
    form_supplier_signal = pyqtSignal()
    
    def __init__(self):
        super(MainView, self).__init__()

        # Initialize components
        self.initializeComponents()

        # Load global styles
        StyleManager.apply_global_styles(self)

    def initializeComponents(self) -> None:
        
        # Load UI — Path resolves correctly on any OS
        ui_path = Path(__file__).resolve().parent / "ui" / "main_view.ui"
        uic.loadUi(str(ui_path), self)

        # Set button icons
        self.btn_materials.setIcon(_icon("IMG-Materials.png"))
        self.btn_lines.setIcon(_icon("IMG-ProductionLines.png"))
        self.btn_users.setIcon(_icon("IMG-AddUser.png"))
        self.btn_suppliers.setIcon(_icon("IMG-Proveedor.png"))
        self.btn_requests.setIcon(_icon("IMG-Requests.png"))
        self.btn_receipts.setIcon(_icon("IMG-Receipts.png"))

        # Connect signals
        self.btn_materials.clicked.connect(self.form_material_signal.emit)
        self.btn_users.clicked.connect(self.form_user_signal.emit)
        self.btn_lines.clicked.connect(self.form_line_signal.emit)
        self.btn_receipts.clicked.connect(self.form_receipt_signal.emit)
        self.btn_suppliers.clicked.connect(self.form_supplier_signal.emit)
        self.btn_toggle.clicked.connect(self.toggle_dashboard)

        self.show()

    
    def open_child_form(self, objectInstance, mdiSubWindow) -> None:
        """"
        Opens a child form inside the MDI container.
        Closes any previously opened child forms.
        
        :param objectInstance: The instance of the child form to be opened.
        :param mdiSubWindow: The QMdiSubWindow that will contain the child form.

        """
        self.mdi_container.closeAllSubWindows()

        StyleManager.apply_global_styles(objectInstance)

        mdiSubWindow.setWidget(objectInstance)
        mdiSubWindow.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        mdiSubWindow.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

        self.mdi_container.addSubWindow(mdiSubWindow)
        mdiSubWindow.showMaximized()

    def toggle_dashboard(self) -> None:
        if self.panel_dashboard.width() == 220:
            self.panel_dashboard.setFixedWidth(64)
            self.btn_toggle.setText(">>")
            self.btn_requests.setText("")
            self.btn_receipts.setText("")
            self.btn_suppliers.setText("")
            self.btn_materials.setText("")
            self.btn_lines.setText("")
            self.btn_users.setText("")
        else:
            self.panel_dashboard.setFixedWidth(220)
            self.btn_toggle.setText("<< Collapse")
            self.btn_requests.setText("Requests")
            self.btn_receipts.setText("Receipts")
            self.btn_suppliers.setText("Suppliers")
            self.btn_materials.setText("Materials")
            self.btn_lines.setText("Production Lines")
            self.btn_users.setText("Users")


if __name__ == '__main__':

    app = QApplication(sys.argv)

    instance = MainView()

    app.exec()
